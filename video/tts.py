#!/usr/bin/env python3
"""Voz en off gratis (edge-tts, voz es-CO) + tiempos por palabra sincronizados con el video.
Uso: python3 video/tts.py guion.json guion_t.json audio.mp3"""
import asyncio, json, subprocess, sys, edge_tts
import os, base64, json as _json, urllib.request
# Voces multilingües (suenan más naturales en español). Cambia con la variable VOZ si quieres probar otra:
# en-US-AndrewMultilingualNeural, en-US-BrianMultilingualNeural, en-US-AvaMultilingualNeural, en-US-EmmaMultilingualNeural
# Respaldo con acento colombiano: es-CO-GonzaloNeural / es-CO-SalomeNeural
VOZ = os.environ.get("VOZ", "en-US-AndrewMultilingualNeural")
PAUSA = 0.45                  # segundos de aire entre escenas
def dur(ruta):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", ruta]))

def escena_eleven(texto, ruta):
    """ElevenLabs: voz natural (o tu voz clonada) + tiempos por palabra. Variables: ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID"""
    vid = os.environ["ELEVENLABS_VOICE_ID"]
    cuerpo = _json.dumps({"text": texto, "model_id": "eleven_multilingual_v2", "language_code": "es",
                          "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.3, "use_speaker_boost": True}}).encode()
    r = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{vid}/with-timestamps?output_format=mp3_44100_128",
                               data=cuerpo, headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "Content-Type": "application/json"})
    d = _json.loads(urllib.request.urlopen(r, timeout=120).read())
    open(ruta, "wb").write(base64.b64decode(d["audio_base64"]))
    a = d["alignment"]; t, previo = [], " "
    for ch, ini in zip(a["characters"], a["character_start_times_seconds"]):
        if ch.strip() and not previo.strip(): t.append(ini)
        previo = ch
    return t

_MODELO = None
def escena_clonada(texto, ruta):
    """Tu voz clonada GRATIS con Chatterbox Multilingual (MIT), en CPU. Necesita VOZ_REF = grabación tuya (wav)."""
    global _MODELO
    import torchaudio
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    if _MODELO is None:
        _MODELO = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
    wav = _MODELO.generate(texto, language_id="es", audio_prompt_path=os.environ["VOZ_REF"])
    tmp = ruta + ".wav"; torchaudio.save(tmp, wav.cpu(), _MODELO.sr)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-codec:a", "libmp3lame", "-q:a", "2", ruta], check=True)
    return []   # sin tiempos por palabra: main() los reparte según el largo de cada palabra
VOCES = [VOZ, "es-MX-JorgeNeural", "es-CO-GonzaloNeural"]   # si una falla, prueba la siguiente
async def escena(texto, ruta):
    if os.environ.get("VOZ_REF") and os.path.exists(os.environ["VOZ_REF"]):
        try:
            t = escena_clonada(texto, ruta); print("voz usada: tu voz clonada (Chatterbox)", file=sys.stderr); return t
        except Exception as ex:
            print(f"Voz clonada falló, uso otra: {ex}", file=sys.stderr)
    if os.environ.get("ELEVENLABS_API_KEY"):
        try:
            t = escena_eleven(texto, ruta); print("voz usada: ElevenLabs", file=sys.stderr); return t
        except Exception as ex:
            print(f"ElevenLabs falló, uso edge-tts: {ex}", file=sys.stderr)
    ultimo = None
    for voz in dict.fromkeys(VOCES):
        for kw in ({"boundary": "WordBoundary"}, {}):       # primero con tiempos por palabra, luego sin ellos
            try:
                com = edge_tts.Communicate(texto, voz, **kw)
                t, audio = [], b""
                async for ch in com.stream():
                    if ch["type"] == "audio": audio += ch["data"]
                    elif ch["type"] == "WordBoundary": t.append(ch["offset"] / 1e7)
                if audio:
                    open(ruta, "wb").write(audio); print(f"voz usada: {voz}", file=sys.stderr); return t
            except Exception as ex:
                ultimo = ex; print(f"voz {voz} {kw} falló: {ex}", file=sys.stderr)
    raise RuntimeError(f"Ninguna voz funcionó: {ultimo}")
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
