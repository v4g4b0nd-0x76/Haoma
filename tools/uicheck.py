"""Minimal Chrome DevTools Protocol driver for exercising tools/admin.html headlessly.

    EDITOR_PORT=8765 python3 tools/uicheck_map.py      # the map studio scenario

`start()` launches google-chrome with remote debugging, `connect()` wraps a page
target, and Page exposes js()/tap()/box()/shot(). Scenario files live next to it.
"""
import base64
import json
import os
import subprocess
import sys
import threading
import time
import urllib.request

import websocket

PORT = int(os.environ.get("UICHECK_PORT", "9333"))
BASE = os.environ.get("UICHECK_URL", "http://127.0.0.1:8765/")


def targets():
    with urllib.request.urlopen("http://127.0.0.1:%d/json" % PORT, timeout=5) as r:
        return json.load(r)


class Page:
    def __init__(self, ws):
        self.ws = ws
        self.seq = 0
        self.lock = threading.Lock()

    def call(self, method, **params):
        with self.lock:
            self.seq += 1
            i = self.seq
            self.ws.send(json.dumps({"id": i, "method": method, "params": params}))
        deadline = time.time() + 30
        while time.time() < deadline:
            try:
                msg = json.loads(self.ws.recv())
            except Exception:
                continue
            if msg.get("id") == i:
                if "error" in msg:
                    raise RuntimeError(method + ": " + json.dumps(msg["error"]))
                return msg.get("result", {})
        raise RuntimeError("timeout on " + method)

    def js(self, expr):
        r = self.call("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=True)
        if r.get("exceptionDetails"):
            raise RuntimeError(json.dumps(r["exceptionDetails"])[:900])
        return r.get("result", {}).get("value")

    def shot(self, path, clip=None):
        p = {"format": "png"}
        if clip:
            p["captureBeyondViewport"] = False
            p["clip"] = clip
        d = self.call("Page.captureScreenshot", **p)
        open(path, "wb").write(base64.b64decode(d["data"]))
        print("shot ->", path)

    def click(self, x, y, kind="mousePressed"):
        self.call("Input.dispatchMouseEvent", type=kind, x=x, y=y, button="left",
                  clickCount=1 if kind.startswith("mouseP") else 0)

    def tap(self, x, y):
        for k in ("mousePressed", "mouseReleased"):
            self.call("Input.dispatchMouseEvent", type=k, x=x, y=y, button="left", clickCount=1)

    def move(self, x, y):
        self.call("Input.dispatchMouseEvent", type="mouseMoved", x=x, y=y)

    def box(self, sel):
        return self.js("(function(){var e=document.querySelector(%s);if(!e)return null;"
                       "var r=e.getBoundingClientRect();return{x:r.x,y:r.y,w:r.width,h:r.height}})()"
                       % json.dumps(sel))


def start():
    subprocess.Popen([
        "google-chrome", "--headless=new", "--remote-debugging-port=%d" % PORT,
        "--remote-allow-origins=*",
        "--window-size=1440,980", "--force-device-scale-factor=1", "--hide-scrollbars",
        "--no-first-run", "--disable-gpu", "--user-data-dir=/tmp/opencode/cdp-profile",
        "about:blank",
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(60):
        try:
            t = targets()
            for x in t:
                if x.get("type") == "page":
                    return x
        except Exception:
            pass
        time.sleep(0.5)
    raise RuntimeError("chrome did not start")


def connect(url):
    ws = websocket.create_connection(url, timeout=30, origin="http://127.0.0.1:%d" % PORT)
    return Page(ws)
