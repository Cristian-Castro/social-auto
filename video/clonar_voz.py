#!/usr/bin/env python3
"""Prueba de voz clonada GRATIS con Chatterbox Multilingual (MIT). Corre en CPU, es lento pero no cuesta nada.
Uso: python3 video/clonar_voz.py voz/mi_voz.wav "Texto a decir" salida.wav"""
import sys, time, torch, torchaudio
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
ref, texto, salida = sys.argv[1:4]
t0 = time.time()
modelo = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
print(f"Modelo cargado en {time.time()-t0:.0f}s")
t1 = time.time()
wav = modelo.generate(texto, language_id="es", audio_prompt_path=ref)
torchaudio.save(salida, wav, modelo.sr)
seg = wav.shape[-1] / modelo.sr
print(f"Audio de {seg:.1f}s generado en {time.time()-t1:.0f}s  (factor {(time.time()-t1)/seg:.1f}x)")
