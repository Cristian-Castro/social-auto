#!/usr/bin/env python3
"""Envía el video a tu Telegram para aprobar. Responde 'ok' o 'no' y el flujo continúa.
Variables: TELEGRAM_TOKEN (BotFather, gratis), TELEGRAM_CHAT_ID. Uso: aprobar_telegram.py video.mp4 "texto" """
import os, sys, time, json, urllib.request, urllib.parse, uuid
T = os.environ["TELEGRAM_TOKEN"]; CHAT = os.environ["TELEGRAM_CHAT_ID"]
def tg(m, **p):
    d = urllib.parse.urlencode(p).encode()
    return json.loads(urllib.request.urlopen(f"https://api.telegram.org/bot{T}/{m}", data=d, timeout=60).read())
def enviar_video(ruta, texto):
    b = uuid.uuid4().hex; cuerpo = b""
    for k, v in (("chat_id", CHAT), ("caption", texto[:900] + "\n\nResponde: ok / no")):
        cuerpo += f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    cuerpo += f'--{b}\r\nContent-Disposition: form-data; name="video"; filename="reel.mp4"\r\nContent-Type: video/mp4\r\n\r\n'.encode() + open(ruta, "rb").read() + f"\r\n--{b}--\r\n".encode()
    urllib.request.urlopen(urllib.request.Request(f"https://api.telegram.org/bot{T}/sendVideo", data=cuerpo, headers={"Content-Type": f"multipart/form-data; boundary={b}"}), timeout=300)
if __name__ == "__main__":
    enviar_video(sys.argv[1], sys.argv[2]); off = 0; limite = time.time() + 6 * 3600
    while time.time() < limite:
        for u in tg("getUpdates", offset=off, timeout=50)["result"]:
            off = u["update_id"] + 1; r = u.get("message", {}).get("text", "").strip().lower()
            if r in ("ok", "si", "sí", "aprobar"): print("APROBADO"); sys.exit(0)
            if r in ("no", "rechazar"): print("RECHAZADO"); sys.exit(1)
    print("SIN RESPUESTA"); sys.exit(2)
