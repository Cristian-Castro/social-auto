#!/usr/bin/env python3
"""Publica un Reel en Instagram y Facebook con la Graph API de Meta.
Requiere: META_TOKEN (token de larga duración de la página), IG_USER_ID, FB_PAGE_ID,
y el video en una URL pública (ej. GitHub Release o tu hosting)."""
import os, sys, time, json, urllib.parse, urllib.request
V = "v21.0"; TOKEN = os.environ["META_TOKEN"]
def api(ruta, datos):
    d = urllib.parse.urlencode({**datos, "access_token": TOKEN}).encode()
    with urllib.request.urlopen(urllib.request.Request(f"https://graph.facebook.com/{V}/{ruta}", data=d), timeout=120) as r:
        return json.loads(r.read())
def instagram(video_url, texto):
    c = api(f"{os.environ['IG_USER_ID']}/media", {"media_type": "REELS", "video_url": video_url, "caption": texto, "share_to_feed": "true"})
    for _ in range(40):                               # espera a que Instagram procese el video
        with urllib.request.urlopen(f"https://graph.facebook.com/{V}/{c['id']}?fields=status_code&access_token={TOKEN}") as r:
            if json.loads(r.read())["status_code"] == "FINISHED": break
        time.sleep(15)
    return api(f"{os.environ['IG_USER_ID']}/media_publish", {"creation_id": c["id"]})
def facebook(video_url, texto):
    return api(f"{os.environ['FB_PAGE_ID']}/videos", {"file_url": video_url, "description": texto})
if __name__ == "__main__":
    url, texto = sys.argv[1], sys.argv[2]
    print(json.dumps({"instagram": instagram(url, texto), "facebook": facebook(url, texto)}))
