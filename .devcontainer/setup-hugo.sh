#!/bin/sh
# Install Hugo (extended) for this codespace. Run once at creation from
# postCreateCommand. The version matches the one the Pages workflow installs, so
# a codespace build and a CI build produce the same site.
#
# This is done here instead of with a devcontainer feature on purpose: a feature
# is pulled from ghcr.io during the image build, and if that pull fails
# Codespaces silently falls back to a recovery container with no language
# tooling, no port forwarding and no postAttachCommand. A plain download in
# postCreateCommand fails loudly in the creation log instead.
set -eu

VERSION=0.139.0
DEST=/usr/local/bin/hugo

if command -v hugo >/dev/null 2>&1; then
    echo "hugo is already installed: $(hugo version)"
    exit 0
fi

tarball="hugo_extended_${VERSION}_linux-amd64.tar.gz"
url="https://github.com/gohugoio/hugo/releases/download/v${VERSION}/${tarball}"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

echo "Downloading ${url}"
if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$url" -o "$tmp/$tarball"
elif command -v wget >/dev/null 2>&1; then
    wget -q -O "$tmp/$tarball" "$url"
else
    echo "error: neither curl nor wget is available" >&2
    exit 1
fi

tar -xzf "$tmp/$tarball" -C "$tmp" hugo
sudo install -m 0755 "$tmp/hugo" "$DEST"
echo "Installed $("$DEST" version)"
