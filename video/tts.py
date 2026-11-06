#!/usr/bin/env python3
"""Voz en off gratis (edge-tts, voz es-CO) + tiempos por palabra sincronizados con el video.
Uso: python3 video/tts.py guion.json guion_t.json audio.mp3"""
import asyncio, json, subprocess, sys, edge_tts
import os
# Voces multilingües (suenan más naturales en español). Cambia con la variable VOZ si quieres probar otra:
# en-US-AndrewMultilingualNeural, en-US-BrianMultilingualNeural, en-US-AvaMultilingualNeural, en-US-EmmaMultilingualNeural
# Respaldo con acento colombiano: es-CO-GonzaloNeural / es-CO-SalomeNeural
VOZ = os.environ.get("VOZ", "en-US-AndrewMultilingualNeural")
PAUSA = 0.45                  # segundos de aire entre escenas
def dur(ruta):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", ruta]))
async def escena(texto, ruta):
    com = edge_tts.Communicate(texto, VOZ, rate="+0%", boundary="WordBoundary")
    t, audio = [], b""
    async for ch in com.stream():
        if ch["type"] == "audio": audio += ch["data"]
        elif ch["type"] == "WordBoundary": t.append(ch["offset"] / 1e7)
    open(ruta, "wb").write(audio); return t
async def main(entrada, salida, mp3):
    g = json.load(open(entrada, encoding="utf-8")); lista = []
    for i, e in enumerate(g["escenas"]):
        ruta = f"/tmp/esc{i}.mp3"; t = await escena(e["texto"], ruta); pal = e["texto"].split(); n = len(pal)
        d = dur(ruta)
        if len(t) != n:   # respaldo: repartir las palabras según su largo a lo largo del audio
            tot = sum(len(p) + 2 for p in pal); acum = 0; t = []
            for p in pal:
                t.append(d * 0.9 * acum / tot); acum += len(p) + 2
        e["tiempos"] = [x + 0.15 for x in t]
        e["duracion"] = round(d + 0.15 + PAUSA, 2)
        sil = f"/tmp/sil{i}.mp3"   # audio + silencio para igualar la duración de la escena
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", ruta, "-af", f"adelay=150,apad=whole_dur={e['duracion']}", "-t", str(e["duracion"]), sil], check=True)
        lista.append(sil)
    open("/tmp/lista.txt", "w").write("".join(f"file '{p}'\n" for p in lista))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "/tmp/lista.txt", "-c:a", "libmp3lame", mp3], check=True)
    json.dump(g, open(salida, "w", encoding="utf-8"), ensure_ascii=False)
asyncio.run(main(*sys.argv[1:4]))
