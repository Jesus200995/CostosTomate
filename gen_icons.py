"""Genera íconos de tomate para la PWA en todos los tamaños requeridos."""
from PIL import Image, ImageDraw
import math, os

ICONS_DIR = r"c:\Users\Admin_1\Pictures\TOMATE\CostosTomate\pwacostos\public\icons"


def draw_tomato(draw: ImageDraw.ImageDraw, cx: float, cy: float, r: float, with_bg=False, bg_r=None, size=None):
    """Dibuja un tomate centrado en (cx, cy) con radio r."""
    # Sombra sutil debajo del tomate
    shadow_offset = r * 0.08
    draw.ellipse(
        [cx - r * 0.92, cy - r * 0.85 + shadow_offset,
         cx + r * 0.92, cy + r * 0.95 + shadow_offset],
        fill=(120, 20, 10, 80)
    )

    # Cuerpo principal del tomate — rojo vibrante
    tomato_color = (220, 50, 32)  # rojo tomate
    draw.ellipse(
        [cx - r, cy - r * 0.85,
         cx + r, cy + r * 0.95],
        fill=tomato_color
    )

    # Segmentos (líneas suaves de separación)
    seg_color = (190, 35, 20)
    line_w = max(1, int(r * 0.04))
    # línea central vertical (suave)
    draw.line([(cx, cy - r * 0.8), (cx, cy + r * 0.85)], fill=seg_color, width=line_w)
    # línea horizontal central
    draw.line([(cx - r * 0.9, cy + r * 0.05), (cx + r * 0.9, cy + r * 0.05)], fill=seg_color, width=line_w)

    # Reflejo / brillo
    shine_rx = r * 0.28
    shine_ry = r * 0.18
    shine_x = cx - r * 0.25
    shine_y = cy - r * 0.48
    draw.ellipse(
        [shine_x - shine_rx, shine_y - shine_ry,
         shine_x + shine_rx, shine_y + shine_ry],
        fill=(255, 220, 215, 160)
    )
    # segundo reflejo pequeño
    draw.ellipse(
        [shine_x + shine_rx * 0.6, shine_y - shine_ry * 0.2,
         shine_x + shine_rx * 0.6 + shine_rx * 0.4,
         shine_y - shine_ry * 0.2 + shine_ry * 0.35],
        fill=(255, 240, 235, 120)
    )

    # Tallo verde
    stem_w = max(2, int(r * 0.12))
    stem_h = r * 0.28
    stem_x = cx
    stem_top = cy - r * 0.85 - stem_h
    stem_bot = cy - r * 0.85
    green_dark = (34, 120, 40)
    draw.rounded_rectangle(
        [stem_x - stem_w // 2, stem_top,
         stem_x + stem_w // 2, stem_bot],
        radius=stem_w // 2,
        fill=green_dark
    )

    # Hojas del cáliz
    green_leaf = (45, 155, 50)
    leaf_len = r * 0.42
    leaf_w = r * 0.14
    leaf_origin_y = cy - r * 0.82

    # Hoja izquierda
    lx, ly = stem_x - leaf_len, leaf_origin_y - leaf_w * 0.3
    draw.polygon([
        (stem_x, leaf_origin_y),
        (lx, ly),
        (lx + leaf_len * 0.3, leaf_origin_y - leaf_w * 1.1),
    ], fill=green_leaf)

    # Hoja derecha
    rx2, ry2 = stem_x + leaf_len, leaf_origin_y - leaf_w * 0.3
    draw.polygon([
        (stem_x, leaf_origin_y),
        (rx2, ry2),
        (rx2 - leaf_len * 0.3, leaf_origin_y - leaf_w * 1.1),
    ], fill=green_leaf)

    # Hoja central (hacia arriba)
    draw.polygon([
        (stem_x, leaf_origin_y),
        (stem_x - leaf_w * 0.7, leaf_origin_y - leaf_len * 0.85),
        (stem_x + leaf_w * 0.7, leaf_origin_y - leaf_len * 0.85),
    ], fill=green_leaf)


def make_icon(size: int, maskable=False) -> Image.Image:
    """Crea un ícono cuadrado de `size`x`size` px."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")

    bg_red = (192, 57, 43)          # rojo fondo
    bg_red_dark = (160, 40, 28)     # borde más oscuro

    # Fondo redondeado
    if maskable:
        # Maskable: fondo llena todo el cuadrado (para que la zona segura quede visible)
        draw.rectangle([0, 0, size, size], fill=bg_red)
        # Sutil gradiente: esquinas más oscuras
        for i in range(0, size // 6):
            alpha = int(30 * (1 - i / (size // 6)))
            draw.rectangle([i, i, size - i, size - i], outline=(0, 0, 0, alpha), width=1)
    else:
        radius = int(size * 0.22)
        draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=bg_red)

    # Tomate centrado
    # En maskable dejamos algo de margen para zona segura (80% del área)
    if maskable:
        margin = size * 0.12
        tomato_r = (size / 2 - margin) * 0.82
    else:
        tomato_r = size * 0.36

    cx = size / 2
    cy = size * 0.52  # ligeramente hacia abajo para dejar espacio al tallo

    draw_tomato(draw, cx, cy, tomato_r)

    return img


def save_all():
    sizes = {
        "icon-48x48.png": 48,
        "icon-72x72.png": 72,
        "icon-96x96.png": 96,
        "icon-128x128.png": 128,
        "icon-144x144.png": 144,
        "icon-152x152.png": 152,
        "icon-192x192.png": 192,
        "icon-256x256.png": 256,
        "icon-384x384.png": 384,
        "icon-512x512.png": 512,
    }

    for fname, sz in sizes.items():
        img = make_icon(sz)
        # Flatten sobre fondo blanco para formato no-RGBA (algunos destinos)
        out_path = os.path.join(ICONS_DIR, fname)
        img.save(out_path, "PNG")
        print(f"Saved {out_path} ({sz}x{sz})")

    # Apple touch icon
    apple = make_icon(180)
    apple.save(os.path.join(ICONS_DIR, "apple-touch-icon.png"), "PNG")
    print("Saved apple-touch-icon.png (180x180)")

    # Maskable
    for fname, sz in [("maskable-192x192.png", 192), ("maskable-512x512.png", 512)]:
        img = make_icon(sz, maskable=True)
        img.save(os.path.join(ICONS_DIR, fname), "PNG")
        print(f"Saved {fname} ({sz}x{sz}) [maskable]")

    print("\nDone! All icons generated.")


if __name__ == "__main__":
    save_all()
