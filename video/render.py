"""Render video/video.html to frames, synthesize sound, and encode the 1920x1080 MP4.

Usage: python3 video/render.py   (needs playwright+chromium, numpy, scipy, ffmpeg)
"""
import pathlib, shutil, subprocess, sys
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
FRAMES = HERE / "frames"; OUT = HERE.parent / "dist"
FPS, DUR = 30, 30

def main():
    shutil.rmtree(FRAMES, ignore_errors=True); FRAMES.mkdir(); OUT.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1920, "height": 1080})
        pg.goto((HERE / "video.html").as_uri()); pg.wait_for_timeout(500)
        for i in range(FPS * DUR):
            pg.evaluate(f"render({i / FPS})")
            pg.screenshot(path=str(FRAMES / f"f{i:04d}.png"))
        b.close()
    subprocess.run([sys.executable, str(HERE / "sound.py")], cwd=HERE, check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
                    "-i", str(FRAMES / "f%04d.png"), "-i", str(HERE / "sound.wav"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", "-preset", "slow",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
                    str(OUT / "CVVH_circuit_30s_1080p.mp4")], check=True)
    print("wrote", OUT / "CVVH_circuit_30s_1080p.mp4")

if __name__ == "__main__":
    main()
