#!/usr/bin/env python3
"""Sube el MP4 a la mediateca de tu WordPress y imprime su URL pública (Meta la necesita).
Variables: WP_URL, WP_USER, WP_APP_PASSWORD (las mismas del blog automático)."""
import base64, json, os, sys, urllib.request
wp = os.environ["WP_URL"].rstrip("/")
auth = "Basic " + base64.b64encode(f'{os.environ["WP_USER"]}:{os.environ["WP_APP_PASSWORD"]}'.encode()).decode()
r = urllib.request.Request(f"{wp}/wp-json/wp/v2/media", data=open(sys.argv[1], "rb").read(), method="POST",
    headers={"Authorization": auth, "Content-Type": "video/mp4", "User-Agent": "cccs-social-auto/1.0",
             "Content-Disposition": 'attachment; filename="reel.mp4"'})
print(json.loads(urllib.request.urlopen(r, timeout=300).read())["source_url"])
