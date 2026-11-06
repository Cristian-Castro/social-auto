#!/usr/bin/env python3
"""guion.json -> reel.mp4 (1080x1920, 30fps). Voz opcional: audio.mp3 + tiempos por palabra en el guion."""
import json, subprocess, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
FPS = 30
def main(guion_path, salida, audio=None):
    g = json.load(open(guion_path, encoding="utf-8"))
    html = (Path(__file__).parent / "plantilla.html").read_text().replace("__GUION__", json.dumps(g, ensure_ascii=False))
    tmp = Path(salida).with_suffix(".html"); tmp.write_text(html, encoding="utf-8")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-i", "-"]
    if audio: cmd += ["-i", audio, "-shortest"]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "veryfast", "-movflags", "+faststart"]
    if audio: cmd += ["-c:a", "aac", "-b:a", "160k"]
    cmd += [salida]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.goto(tmp.resolve().as_uri()); pg.wait_for_timeout(400)
        total = pg.evaluate("window.TOTAL"); n = int(total * FPS)
        for i in range(n):
            pg.evaluate(f"render({i / FPS})")
            ff.stdin.write(pg.screenshot(type="jpeg", quality=88))
        b.close()
    ff.stdin.close(); ff.wait(); tmp.unlink(); print(f"{salida}: {total:.1f}s, {n} fotogramas")
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
