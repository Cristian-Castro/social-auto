#!/usr/bin/env python3
"""Voz en off gratis con edge-tts (voces es-CO) + tiempos por palabra para los subtítulos.
Uso: python3 video/tts.py guion.json salida_guion.json audio.mp3   (corre en GitHub Actions)"""
import asyncio, json, sys, edge_tts
VOZ = "es-CO-GonzaloNeural"   # alternativa femenina: es-CO-SalomeNeural
async def escena(texto, ruta):
    com = edge_tts.Communicate(texto, VOZ, rate="+8%", boundary="WordBoundary")
    tiempos, audio = [], b""
    async for ch in com.stream():
        if ch["type"] == "audio": audio += ch["data"]
        elif ch["type"] == "WordBoundary": tiempos.append(ch["offset"] / 1e7)
    open(ruta, "wb").write(audio); return tiempos
async def main(entrada, salida, mp3):
    g = json.load(open(entrada, encoding="utf-8")); partes = []
    for i, e in enumerate(g["escenas"]):
        t = await escena(e["texto"], f"/tmp/esc{i}.mp3"); n = len(e["texto"].split())
        e["tiempos"] = (t + [t[-1]] * n)[:n]; partes.append(f"/tmp/esc{i}.mp3")
    json.dump(g, open(salida, "w", encoding="utf-8"), ensure_ascii=False)
    print("Concatenar audios con ffmpeg y alinear por escena en render_reel (ver PLAN.md)")
asyncio.run(main(*sys.argv[1:4]))
