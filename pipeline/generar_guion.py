#!/usr/bin/env python3
"""Escribe el guion del Reel del día con la API de Claude, según config/calendario.yaml.
Imprime un JSON listo para video/tts.py. Variable: ANTHROPIC_API_KEY"""
import json, datetime, pathlib, re, yaml, anthropic
DIAS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
RAIZ = pathlib.Path(__file__).resolve().parent.parent
hoy = DIAS[datetime.date.today().weekday()]
plan = yaml.safe_load((RAIZ / "config/calendario.yaml").read_text(encoding="utf-8"))[hoy]
ICONOS = "robot, escudo, codigo, rayo, paleta, globo"
prompt = f"""Eres el creador de contenido de CCCS - Freelance Tecnológico (Colombia).
Hoy toca el pilar: {plan['pilar']}. Objetivo: {plan['objetivo']}.
Escribe el guion de un Reel vertical de 25 a 35 segundos, en español colombiano neutro, tono cercano,
profesional y simple, para gente con poca experiencia en tecnología. Evita datos dudosos o inventados:
si no estás seguro de algo, usa un consejo atemporal y verificable.
Responde SOLO con JSON válido con esta forma:
{{"etiqueta": "{plan['pilar']}", "cta": "Síguenos · @freelanceccs",
 "caption": "texto del post con 3 a 5 hashtags",
 "escenas": [{{"titulo": "titular corto, resalta 1 palabra con <em>palabra</em>",
              "texto": "frase hablada de máx. 14 palabras", "icono": "uno de: {ICONOS}"}}]}}
Usa entre 5 y 7 escenas: primera con gancho fuerte, última con llamado a seguirnos."""
msg = anthropic.Anthropic().messages.create(model="claude-sonnet-5-5", max_tokens=1500,
                                            messages=[{"role": "user", "content": prompt}])
texto = msg.content[0].text
print(json.dumps(json.loads(re.search(r"\{.*\}", texto, re.S).group(0)), ensure_ascii=False))
