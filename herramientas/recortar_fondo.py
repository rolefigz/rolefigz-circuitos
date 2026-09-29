"""Recorta el fondo verde de las fotos de circuiti/ y las publica en la web.

Uso (desde la carpeta del proyecto):
    python herramientas/recortar_fondo.py            # procesa las fotos nuevas o cambiadas
    python herramientas/recortar_fondo.py --forzar   # vuelve a procesarlas todas

Para cada circuiti/<circuito>.jpeg|.jpg|.png (con fondo verde croma) genera
circuiti/<circuito>.webp con fondo transparente y actualiza la lista PHOTOS de
index.html para que la ficha de ese circuito muestre la foto.

Requiere: pip install pillow numpy
"""
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
PHOTO_DIR = ROOT / "circuiti"
INDEX = ROOT / "index.html"
SLUGS = [
    "melbourne", "shanghai", "suzuka", "sakhir", "jeddah", "miami", "montreal",
    "monaco", "barcelona", "spielberg", "silverstone", "spa", "hungaroring",
    "zandvoort", "monza", "madrid", "baku", "austin", "mexico-city", "interlagos",
    "las-vegas", "lusail", "yas-marina",
    # GT, World Challenge, Circuiti italiani
    "le-mans", "nordschleife", "daytona", "bathurst", "sebring", "paul-ricard", "brands-hatch",
    "misano", "magny-cours", "nurburgring", "portimao", "imola", "mugello", "vallelunga",
]
MAX_WIDTH = 1100


def key_out_green(src: Path, dst: Path) -> None:
    rgb = np.asarray(Image.open(src).convert("RGB")).astype(np.float32)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]

    greenness = g - np.maximum(r, b)
    bg = float(np.median(np.concatenate([greenness[:40, :40].ravel(), greenness[:40, -40:].ravel()])))
    if bg < 60:
        raise ValueError("no parece tener fondo verde croma (verde de fondo = %.0f)" % bg)
    t0, t1 = 0.25 * bg, 0.6 * bg
    alpha = 1.0 - np.clip((greenness - t0) / (t1 - t0), 0, 1)

    # Despill: evita el halo verde en los bordes blancos del trazado.
    g_clean = np.minimum(g, np.maximum(r, b))
    rgba = np.dstack([r, g_clean, b, alpha * 255]).clip(0, 255).astype(np.uint8)
    img = Image.fromarray(rgba, "RGBA")

    a = img.getchannel("A").point(lambda v: 0 if v < 24 else v).filter(ImageFilter.MedianFilter(3))
    img.putalpha(a)

    bbox = a.point(lambda v: 255 if v > 40 else 0).getbbox()
    if not bbox:
        raise ValueError("no se encontró el producto en la imagen")
    pad = 24
    x0, y0, x1, y1 = bbox
    img = img.crop((max(0, x0 - pad), max(0, y0 - pad), min(img.width, x1 + pad), min(img.height, y1 + pad)))
    if img.width > MAX_WIDTH:
        img = img.resize((MAX_WIDTH, round(img.height * MAX_WIDTH / img.width)), Image.LANCZOS)

    img.save(dst, "WEBP", quality=90, method=6)


def update_photo_list() -> list:
    available = [s for s in SLUGS if (PHOTO_DIR / f"{s}.webp").exists()]
    html = INDEX.read_text(encoding="utf-8")
    new_line = "const PHOTOS = [" + ",".join(f'"{s}"' for s in available) + "];"
    html, n = re.subn(r"const PHOTOS = \[[^\]]*\];", new_line, html)
    if n != 1:
        raise SystemExit("No encontré la lista PHOTOS en index.html")
    INDEX.write_text(html, encoding="utf-8", newline="\n")
    return available


def main() -> None:
    force = "--forzar" in sys.argv
    processed, errors = [], []
    for slug in SLUGS:
        sources = [p for ext in ("jpeg", "jpg", "png") if (p := PHOTO_DIR / f"{slug}.{ext}").exists()]
        if not sources:
            continue
        src = max(sources, key=lambda p: p.stat().st_mtime)
        dst = PHOTO_DIR / f"{slug}.webp"
        if dst.exists() and not force and dst.stat().st_mtime >= src.stat().st_mtime:
            continue
        try:
            key_out_green(src, dst)
            processed.append(slug)
        except Exception as exc:
            errors.append(f"{src.name}: {exc}")

    available = update_photo_list()
    print("Procesadas:", ", ".join(processed) if processed else "ninguna nueva")
    print("Con foto en la web (%d/%d):" % (len(available), len(SLUGS)), ", ".join(available))
    for e in errors:
        print("ERROR", e)
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
