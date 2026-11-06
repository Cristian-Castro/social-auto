#!/usr/bin/env python3
"""Prueba de voz clonada GRATIS con Chatterbox Multilingual (MIT). Corre en CPU.
Genera varias versiones con ajustes distintos, unidas en un solo audio con 2 s de silencio entre cada una.
Uso: python3 video/clonar_voz.py ref.wav "Texto" salida.wav"""
import sys, time, torch, torchaudio
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
ref, texto, salida = sys.argv[1:4]
modelo = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
VERSIONES = [  # (nombre, ajustes)
    ("1) estándar",                       {}),
    ("2) más calmada",                    {"exaggeration": 0.35, "cfg_weight": 0.3}),
    ("3) sin acento de la referencia",    {"cfg_weight": 0.0}),
    ("4) más expresiva",                  {"exaggeration": 0.75, "cfg_weight": 0.4}),
]
partes, silencio = [], torch.zeros(1, int(modelo.sr * 2))
for nombre, kw in VERSIONES:
    t = time.time()
    try:
        wav = modelo.generate(texto, language_id="es", audio_prompt_path=ref, **kw)
    except TypeError:
        wav = modelo.generate(texto, language_id="es", audio_prompt_path=ref)
    print(f"{nombre}: {wav.shape[-1]/modelo.sr:.1f}s de audio en {time.time()-t:.0f}s")
    partes += [wav.cpu() if wav.dim() == 2 else wav.cpu().unsqueeze(0), silencio]
torchaudio.save(salida, torch.cat(partes, dim=1), modelo.sr)
print("Orden del audio: " + " | ".join(n for n, _ in VERSIONES))
