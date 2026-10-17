#!/usr/bin/env python3
"""Local site editor. Standard library only. Run from the project: python tools/editor.py
Binds to 127.0.0.1 only. Needs: git and hugo (in PATH). Python is optional when using
the released binary (see .github/workflows/release-editor.yml)."""
import hashlib, time, json, mimetypes, os, re, secrets, shutil, socket, subprocess, sys, tempfile, atexit, webbrowser
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs


def find_root():
    """Project root = directory with hugo.toml. Env HAOMA_ROOT wins; else cwd; else beside the binary."""
    env = os.environ.get("HAOMA_ROOT")
    if env:
        return Path(env).resolve()
    here = Path.cwd().resolve()
    for p in [here, *here.parents]:
        if (p / "hugo.toml").exists():
            return p
    if getattr(sys, "frozen", False):
        exe = Path(sys.executable).resolve().parent
        for p in [exe, *exe.parents]:
            if (p / "hugo.toml").exists():
                return p
    return Path(__file__).resolve().parent.parent


def admin_html_path():
    if getattr(sys, "frozen", False):
        bundled = Path(getattr(sys, "_MEIPASS", "")) / "admin.html"
        if bundled.exists():
            return bundled
    return ROOT / "tools" / "admin.html"


ROOT = find_root()
PORT = int(os.environ.get("EDITOR_PORT", "8765"))
HUGO_PORT = int(os.environ.get("HUGO_PORT", "1313"))
# A GitHub codespace reaches every port through its own forwarded https
# hostname (<codespace>-<port>.<domain>), so a localhost URL would point at the
# reader's own machine. The codespace sets both variables.
CODESPACE = os.environ.get("CODESPACE_NAME")
FWD_DOMAIN = os.environ.get("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN", "app.github.dev")
TOKEN = secrets.token_urlsafe(16)
DIRS = ("content", "data", "i18n", "layouts", "static", "assets")
TEXT = {".md", ".json", ".toml", ".yaml", ".yml", ".html", ".css", ".js", ".svg", ".txt", ".xml"}
LOG = ROOT / "tools" / ".preview.log"
WS = ROOT / "tools" / ".preview"
HIST = ROOT / "tools" / ".history"
DRAFTS = ROOT / "tools" / ".drafts"
DEL = DRAFTS / "__deleted.json"
MAXH = 60
preview = {"proc": None, "port": None}


def safe(rel):
    p = (ROOT / rel).resolve()
    if ROOT not in p.parents:
        raise ValueError("path outside project")
    top = p.relative_to(ROOT).parts[0]
    if top not in DIRS and p.name != "hugo.toml":
        raise ValueError("path not editable")
    return p


def run(cmd, timeout=120):
    try:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout + r.stderr).strip()
    except FileNotFoundError:
        return 127, "command not found: " + cmd[0]
    except subprocess.TimeoutExpired:
        return 124, "timed out"


def tree():
    out = ["hugo.toml"] if (ROOT / "hugo.toml").exists() else []
    for d in DIRS:
        for p in sorted((ROOT / d).rglob("*")) if (ROOT / d).exists() else []:
            if p.is_file() and not any(x.startswith(".") for x in p.relative_to(ROOT).parts):
                out.append(p.relative_to(ROOT).as_posix())
    return out


def ws_sync():
    """Preview copy = saved files + temporary drafts."""
    shutil.rmtree(WS, ignore_errors=True)
    WS.mkdir(parents=True)
    for d in DIRS:
        if (ROOT / d).exists():
            shutil.copytree(ROOT / d, WS / d)
    if (ROOT / "hugo.toml").exists():
        shutil.copy2(ROOT / "hugo.toml", WS / "hugo.toml")
    for rel, e in dr_load().items():
        real = ROOT / rel
        if e["kind"] == "del":
            ws_delete(real)
        elif dr_blob(rel).exists():
            ws_write(real, dr_blob(rel).read_bytes())


def dr_load():
    f = DRAFTS / "index.json"
    return json.loads(f.read_text()) if f.exists() else {}


def dr_save(d):
    DRAFTS.mkdir(parents=True, exist_ok=True)
    (DRAFTS / "index.json").write_text(json.dumps(d))


def dr_blob(rel):
    return DRAFTS / hashlib.sha1(rel.encode()).hexdigest()


def dr_put(rel, data):
    d = dr_load()
    DRAFTS.mkdir(parents=True, exist_ok=True)
    dr_blob(rel).write_bytes(data)
    kind = "text" if Path(rel).suffix.lower() in TEXT else "bin"
    d[rel] = {"kind": kind, "time": time.time(), "size": len(data)}
    dr_save(d)


def dr_mark_delete(rel):
    d = dr_load()
    if dr_blob(rel).exists():
        dr_blob(rel).unlink()
    d[rel] = {"kind": "del", "time": time.time(), "size": 0}
    dr_save(d)


def dr_drop(rel):
    d = dr_load()
    d.pop(rel, None)
    if dr_blob(rel).exists():
        dr_blob(rel).unlink()
    dr_save(d)


def ws_path(real):
    return WS / real.relative_to(ROOT)


def ws_write(real, data):
    w = ws_path(real)
    w.parent.mkdir(parents=True, exist_ok=True)
    w.write_bytes(data)


def ws_delete(real):
    w = ws_path(real)
    if w.exists():
        w.unlink()


def rel_of(p):
    return p.relative_to(ROOT).as_posix()


def dr_deleted():
    return json.loads(DEL.read_text()) if DEL.exists() else []


def dr_save_deleted(lst):
    DRAFTS.mkdir(parents=True, exist_ok=True)
    DEL.write_text(json.dumps(sorted(set(lst))))


def draft_write(p, data):
    d = DRAFTS / rel_of(p)
    d.parent.mkdir(parents=True, exist_ok=True)
    d.write_bytes(data)
    ws_write(p, data)
    lst = dr_deleted()
    if rel_of(p) in lst:
        lst.remove(rel_of(p))
        dr_save_deleted(lst)


def draft_discard(p):
    d = DRAFTS / rel_of(p)
    if d.exists():
        d.unlink()
    lst = dr_deleted()
    if rel_of(p) in lst:
        lst.remove(rel_of(p))
        dr_save_deleted(lst)
    if p.exists():
        ws_write(p, p.read_bytes())
    else:
        ws_delete(p)


def draft_delete(p):
    if not p.exists():
        return draft_discard(p)
    d = DRAFTS / rel_of(p)
    if d.exists():
        d.unlink()
    ws_delete(p)
    dr_save_deleted(dr_deleted() + [rel_of(p)])


def draft_list():
    items = []
    if DRAFTS.exists():
        for f in DRAFTS.rglob("*"):
            if f.is_file() and f.name != "__deleted.json":
                rel = f.relative_to(DRAFTS).as_posix()
                items.append({"path": rel, "state": "edited" if (ROOT / rel).exists() else "new", "size": f.stat().st_size, "mtime": f.stat().st_mtime})
    for r in dr_deleted():
        items.append({"path": r, "state": "deleted", "size": 0, "mtime": time.time()})
    return items


def draft_apply(paths, x, lab):
    dl = dr_deleted()
    for r in paths:
        p = safe(r)
        if r in dl:
            hist_record(x, lab, p)
            if p.exists():
                p.unlink()
            ws_delete(p)
            dl.remove(r)
            continue
        d = DRAFTS / r
        if not d.exists():
            continue
        data = d.read_bytes()
        hist_record(x, lab, p)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        ws_write(p, data)
        d.unlink()
    dr_save_deleted(dl)


def hist_load():
    f = HIST / "index.json"
    return json.loads(f.read_text()) if f.exists() else []


def hist_save(h):
    HIST.mkdir(parents=True, exist_ok=True)
    (HIST / "index.json").write_text(json.dumps(h))


def hist_record(txn, label, p):
    """Back up the current state of p once per change (txn) before it is modified."""
    rel = p.relative_to(ROOT).as_posix()
    h = hist_load()
    t = next((x for x in h if x["id"] == txn), None)
    if t is None:
        t = {"id": txn, "time": time.time(), "label": label or "change", "files": []}
        h.append(t)
    if not any(f["path"] == rel for f in t["files"]):
        ent = {"path": rel, "existed": p.exists()}
        if p.exists():
            ent["bk"] = "%s__%d" % (txn, len(t["files"]))
            HIST.mkdir(parents=True, exist_ok=True)
            (HIST / ent["bk"]).write_bytes(p.read_bytes())
        t["files"].append(ent)
    while len(h) > MAXH:
        for f in h.pop(0)["files"]:
            if f.get("bk") and (HIST / f["bk"]).exists():
                (HIST / f["bk"]).unlink()
    hist_save(h)


def rollback(tid=None):
    h = hist_load()
    if not h:
        raise ValueError("nothing to roll back")
    ids = [x["id"] for x in h]
    if tid and tid not in ids:
        raise ValueError("unknown change")
    idx = ids.index(tid) if tid else len(h) - 1
    undone, paths = [], []
    for t in reversed(h[idx:]):
        for f in reversed(t["files"]):
            p = ROOT / f["path"]
            if f["existed"]:
                data = (HIST / f["bk"]).read_bytes()
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(data)
                ws_write(p, data)
            else:
                if p.exists():
                    p.unlink()
                ws_delete(p)
            paths.append(f["path"])
            if f.get("bk") and (HIST / f["bk"]).exists():
                (HIST / f["bk"]).unlink()
        undone.append(t["label"])
    hist_save(h[:idx])
    return {"undone": undone, "paths": paths}


def txn_args(q):
    x = q.get("x") or secrets.token_hex(4)
    if not re.fullmatch(r"[\w-]+", x):
        raise ValueError("bad change id")
    return x, q.get("l", "")[:120]


def free_port(start):
    for p in range(start, start + 40):
        with socket.socket() as k:
            try:
                k.bind(("127.0.0.1", p))
                return p
            except OSError:
                continue
    raise RuntimeError("no free port found")


def forward_url(port):
    """URL a browser can use to reach `port`. Local runs get http://localhost:PORT/;
    inside a codespace, the hostname the codespace forwards that port on."""
    if CODESPACE:
        return f"https://{CODESPACE}-{port}.{FWD_DOMAIN}/"
    return f"http://localhost:{port}/"


def preview_status():
    proc = preview["proc"]
    running = proc is not None and proc.poll() is None
    tail = LOG.read_text(errors="replace").splitlines()[-12:] if LOG.exists() else []
    url = forward_url(preview["port"]) if running else ""
    return {"running": running, "url": url, "log": "\n".join(tail)}


def preview_start():
    if preview_status()["running"]:
        return
    if not shutil.which("hugo"):
        LOG.write_text("hugo was not found in PATH. Install Hugo (extended) and restart the editor.\n")
        return
    if not WS.exists():
        ws_sync()
    port = free_port(HUGO_PORT)
    preview["port"] = port
    cmd = ["hugo", "server", "--source", str(WS), "--port", str(port), "--bind", "127.0.0.1", "--disableFastRender"]
    if CODESPACE:
        # Otherwise Hugo writes http://localhost:PORT/ into every link, which in a
        # codespace resolves to the reader's machine, not the preview server.
        cmd += ["--baseURL", forward_url(port), "--appendPort=false"]
    log = open(LOG, "w")
    preview["proc"] = subprocess.Popen(cmd, cwd=WS, stdout=log, stderr=subprocess.STDOUT)


def preview_stop():
    p = preview["proc"]
    if p and p.poll() is None:
        p.terminate()
        try:
            p.wait(5)
        except subprocess.TimeoutExpired:
            p.kill()
    preview["proc"] = None


atexit.register(preview_stop)


def fmval(fm, key):
    m = re.search(r"^" + key + r":\s*(.*)$", fm, re.M)
    return m.group(1).strip().strip('"') if m else ""


def audit():
    base = ROOT / "content"
    langs = [d.name for d in base.iterdir() if d.is_dir()] if base.exists() else []
    rels = {l: {p.relative_to(base / l).as_posix() for p in (base / l).rglob("*.md")} for l in langs}
    items = []
    for l in langs:
        for p in sorted((base / l).rglob("*.md")):
            rel = p.relative_to(base / l).as_posix()
            txt = p.read_text(encoding="utf-8", errors="replace")
            m = re.match(r"---\n(.*?)\n---", txt, re.S)
            fm = m.group(1) if m else ""
            idx = p.name == "_index.md"
            sb = re.search(r"^sources:\s*\n((?:[ \t]+- .*\n?)*)", fm + "\n", re.M)
            nsrc = len(re.findall(r"^\s+- ", sb.group(1), re.M)) if sb else (1 if re.search(r"^sources:\s*\[.+\]", fm, re.M) else 0)
            rev, grade = fmval(fm, "reviewed"), fmval(fm, "grade")
            try:
                stale = (date.today() - date.fromisoformat(rev)).days > 180 if rev else (not idx)
            except ValueError:
                stale = True
            items.append({"path": "content/%s/%s" % (l, rel), "lang": l, "title": fmval(fm, "title") or rel, "grade": grade,
                          "reviewed": rev, "sources": nsrc, "index": idx,
                          "draft": ("draft" in grade.lower() or "پیش‌نویس" in grade),
                          "stale": bool(stale) and not idx, "missing": [o for o in langs if o != l and rel not in rels[o]]})
    return items


def repo_url():
    c, o = run(["git", "remote", "get-url", "origin"])
    m = re.match(r"(?:git@|https?://(?:[^@/]+@)?)([^:/]+)[:/](.+?)(?:\.git)?/?$", o.strip()) if c == 0 else None
    return "https://%s/%s" % (m.group(1), m.group(2)) if m else ""


class H(BaseHTTPRequestHandler):
    server_version = "SiteEditor"

    def log_message(self, *a):
        pass

    def send(self, code, body, ctype="application/json"):
        if not isinstance(body, (bytes, bytearray)):
            body = (body if isinstance(body, str) else json.dumps(body)).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype + ("; charset=utf-8" if ctype.startswith("text") or "json" in ctype else ""))
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > 200 * 1024 * 1024:
            raise ValueError("file too large")
        return self.rfile.read(n)

    def handle_any(self, method):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        try:
            if self.headers.get("Host", "").split(":")[0] not in ("127.0.0.1", "localhost"):
                return self.send(403, {"error": "bad host"})
            if u.path == "/" and method == "GET":
                html = admin_html_path().read_text(encoding="utf-8").replace("__TOKEN__", TOKEN)
                return self.send(200, html, "text/html")
            if not u.path.startswith("/api/"):
                return self.send(404, {"error": "not found"})
            if (self.headers.get("X-Token") or q.get("t")) != TOKEN:
                return self.send(401, {"error": "bad token"})
            ep = u.path[5:]
            if ep == "tree":
                return self.send(200, tree())
            if ep == "file":
                p = safe(q["path"])
                if method == "GET":
                    if p.suffix.lower() not in TEXT:
                        return self.send(415, {"error": "binary file"})
                    return self.send(200, p.read_bytes().decode("utf-8"), "text/plain")
                x, lab = txn_args(q)
                if method == "PUT":
                    data = self.body()
                    hist_record(x, lab, p)
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_bytes(data)
                    ws_write(p, data)
                    return self.send(200, {"ok": True})
                if method == "DELETE":
                    hist_record(x, lab, p)
                    p.unlink()
                    ws_delete(p)
                    return self.send(200, {"ok": True})
            if ep == "upload" and method == "POST":
                p = safe(q["path"])
                if p.relative_to(ROOT).parts[0] != "static":
                    raise ValueError("uploads go in static/")
                x, lab = txn_args(q)
                data = self.body()
                hist_record(x, lab, p)
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(data)
                ws_write(p, data)
                return self.send(200, {"ok": True})
            if ep == "draft" and method == "PUT":
                p = safe(q["path"])
                data = self.body()
                dr_put(p.relative_to(ROOT).as_posix(), data)
                ws_write(p, data)
                return self.send(200, {"ok": True})
            if ep == "draftdel" and method == "POST":
                p = safe(q["path"])
                dr_mark_delete(p.relative_to(ROOT).as_posix())
                ws_delete(p)
                return self.send(200, {"ok": True})
            if ep == "discard" and method == "POST":
                p = safe(q["path"])
                dr_drop(p.relative_to(ROOT).as_posix())
                if p.exists():
                    ws_write(p, p.read_bytes())
                else:
                    ws_delete(p)
                return self.send(200, {"ok": True})
            if ep == "drafts":
                items = []
                for rel, e in sorted(dr_load().items()):
                    it = {"path": rel, "kind": e["kind"], "time": e["time"], "size": e["size"]}
                    if e["kind"] == "text" and dr_blob(rel).exists():
                        it["text"] = dr_blob(rel).read_bytes().decode("utf-8", "replace")
                    items.append(it)
                return self.send(200, {"items": items})
            if ep == "apply" and method == "POST":
                d = json.loads(self.body())
                x = d.get("x") or secrets.token_hex(4)
                if not re.fullmatch(r"[\w-]+", x):
                    raise ValueError("bad change id")
                lab, n, drafts = str(d.get("l", ""))[:120], 0, dr_load()
                for rel in d.get("paths", []):
                    e = drafts.get(rel)
                    if not e:
                        continue
                    p = safe(rel)
                    hist_record(x, lab, p)
                    if e["kind"] == "del":
                        if p.exists():
                            p.unlink()
                        ws_delete(p)
                    else:
                        data = dr_blob(rel).read_bytes()
                        p.parent.mkdir(parents=True, exist_ok=True)
                        p.write_bytes(data)
                        ws_write(p, data)
                    dr_drop(rel)
                    n += 1
                return self.send(200, {"ok": True, "applied": n})
            if ep == "resync" and method == "POST":
                ws_sync()
                return self.send(200, {"ok": True})
            if ep == "history":
                h = hist_load()
                return self.send(200, {"items": [{"id": t["id"], "time": t["time"], "label": t["label"], "files": [f["path"] for f in t["files"]]} for t in reversed(h)]})
            if ep == "rollback" and method == "POST":
                return self.send(200, rollback(q.get("id")))
            if ep == "revert" and method == "POST":
                c, o = run(["git", "revert", "--no-edit", "HEAD"])
                ws_sync()
                return self.send(200, {"ok": c == 0, "output": o})
            if ep == "raw":
                p = safe(q["path"])
                if q.get("ws") and ws_path(p).exists():
                    p = ws_path(p)
                return self.send(200, p.read_bytes(), mimetypes.guess_type(str(p))[0] or "application/octet-stream")
            if ep == "preview":
                if method == "POST":
                    (preview_start if q.get("a") == "start" else preview_stop)()
                return self.send(200, preview_status())
            if ep == "check":
                tmp = tempfile.mkdtemp()
                code, out = run(["hugo", "--quiet", "--destination", tmp])
                shutil.rmtree(tmp, ignore_errors=True)
                return self.send(200, {"ok": code == 0, "output": out or "Build OK"})
            if ep == "git":
                c, branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
                _, status = run(["git", "status", "--short"])
                return self.send(200, {"ok": c == 0, "branch": branch, "status": status, "remote": repo_url()})
            if ep == "audit":
                return self.send(200, {"items": audit()})
            if ep == "pull" and method == "POST":
                c, o = run(["git", "pull", "--ff-only"], 120)
                ws_sync()
                return self.send(200, {"ok": c == 0, "output": o})
            if ep == "diff":
                _, d = run(["git", "diff", "HEAD"])
                return self.send(200, {"diff": d[:300000]})
            if ep == "commit" and method == "POST":
                d = json.loads(self.body())
                msg, branch = d.get("message", "").strip(), d.get("branch", "")
                if not msg or not re.fullmatch(r"[\w./-]+", branch):
                    raise ValueError("a commit message and a valid branch name are required")
                steps = [["git", "checkout", "-b", branch]] if d.get("newBranch") else []
                steps += [["git", "add", "-A"], ["git", "commit", "-m", msg]]
                log = []
                for cmd in steps:
                    c, o = run(cmd)
                    log.append("$ " + " ".join(cmd[:3]) + "\n" + o)
                    if c and "nothing to commit" not in o:
                        return self.send(200, {"ok": False, "output": "\n".join(log)})
                if d.get("push"):
                    cmd = ["git", "push", "-u", "origin", branch] if d.get("newBranch") else ["git", "push", "origin", "HEAD:" + branch]
                    c, o = run(cmd, 180)
                    log.append("$ " + " ".join(cmd) + "\n" + o)
                    return self.send(200, {"ok": c == 0, "output": "\n".join(log)})
                return self.send(200, {"ok": True, "output": "\n".join(log)})
            return self.send(404, {"error": "unknown endpoint"})
        except Exception as e:
            return self.send(400, {"error": str(e)})

    do_GET = lambda s: s.handle_any("GET")
    do_PUT = lambda s: s.handle_any("PUT")
    do_POST = lambda s: s.handle_any("POST")
    do_DELETE = lambda s: s.handle_any("DELETE")


if __name__ == "__main__":
    if not (ROOT / "hugo.toml").exists():
        print("Could not find a Haoma project (hugo.toml).")
        print("Run this from the project folder, or set HAOMA_ROOT to that folder.")
        sys.exit(1)
    for need in ("hugo", "git"):
        c, _ = run([need, "version"] if need == "hugo" else [need, "--version"], 10)
        if c == 127:
            print(f"Warning: '{need}' not found on PATH — preview/publish may fail.")
    ws_sync()
    url = forward_url(PORT)
    print(f"Site editor: {url}  (project: {ROOT})\nCtrl+C to stop.", flush=True)
    try:
        srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
    except OSError:
        print(f"Port {PORT} is already in use — the editor is probably already running.")
        sys.exit(0)
    if not CODESPACE:
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"(could not open a browser: {e})")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
