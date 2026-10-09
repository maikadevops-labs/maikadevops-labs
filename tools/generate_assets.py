"""Genera los SVG animados del README (nave espacial pixel art + cabecera que se teclea).

Uso:  python tools/generate_assets.py
Salida: assets/nave.svg, assets/cabecera.svg
"""
import math
import os
import random

OUT = os.path.join(os.path.dirname(__file__), "..", "assets")
os.makedirs(OUT, exist_ok=True)

PX = 4            # tamaño de cada "pixel"
W, H = 160, 60    # grid -> 640 x 240
BG = "#0b0f1a"


def r(x, y, w=1, h=1, fill="#fff", extra=""):
    return (f'<rect x="{x*PX}" y="{y*PX}" width="{w*PX}" height="{h*PX}" '
            f'fill="{fill}" shape-rendering="crispEdges"{extra}/>')


def sprite(rows, palette, ox, oy):
    """Dibuja un sprite desde ASCII; '.' es transparente."""
    out = []
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in palette:
                out.append(r(ox + x, oy + y, 1, 1, palette[ch]))
    return "".join(out)


def star_layer(n, seed, size, colors, dur):
    """Capa de estrellas que se desplaza a la izquierda en bucle sin cortes."""
    rnd = random.Random(seed)
    stars = [(rnd.randint(0, W - 1), rnd.randint(0, H - 4), rnd.choice(colors)) for _ in range(n)]
    items = [r(x + off, y, size, size, c) for off in (0, W) for x, y, c in stars]
    return (f'<g><animateTransform attributeName="transform" type="translate" '
            f'values="0 0;{-W*PX} 0" dur="{dur}s" repeatCount="indefinite"/>' + "".join(items) + "</g>")


def streak_layer(n, seed, dur):
    """Líneas de velocidad detrás de la nave."""
    rnd = random.Random(seed)
    items = []
    for _ in range(n):
        x, y, ln = rnd.randint(0, W - 1), rnd.randint(4, H - 8), rnd.randint(6, 14)
        for off in (0, W):
            items.append(r(x + off, y, ln, 1, "#c9d1d9", ' opacity="0.25"'))
    return (f'<g><animateTransform attributeName="transform" type="translate" '
            f'values="0 0;{-W*PX} 0" dur="{dur}s" repeatCount="indefinite"/>' + "".join(items) + "</g>")


def planet(cx, cy, rad, colors, dur, begin, ring=None):
    """Planeta pixelado que cruza la pantalla de derecha a izquierda."""
    parts = []
    if ring:
        parts.append(r(cx - rad - 6, cy - 1, 2 * rad + 13, 2, ring, ' opacity="0.7"'))
    for dy in range(-rad, rad + 1):
        hw = int(round(math.sqrt(rad * rad - dy * dy)))
        col = colors[min(len(colors) - 1, (dy + rad) * len(colors) // (2 * rad + 1))]
        parts.append(r(cx - hw, cy + dy, 2 * hw + 1, 1, col))
    if ring:
        parts.append(r(cx - rad - 6, cy, 2 * rad + 13, 1, ring, ' opacity="0.9"'))
    travel = (W + 2 * rad + 16 + 6) * PX
    return (f'<g><animateTransform attributeName="transform" type="translate" '
            f'values="0 0;{-travel} 0" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
            + "".join(parts) + "</g>")


def asteroid(y, dur, begin, scale_rows=None):
    rows = scale_rows or [".GG.", "GGGG", "GDGG", ".GG."]
    s = sprite(rows, {"G": "#6e7681", "D": "#484f58"}, W + 2, y)
    return (f'<g><animateTransform attributeName="transform" type="translate" '
            f'values="0 0;{-(W+10)*PX} {4*PX}" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
            f'{s}</g>')


GIRL = [
    "...HJHHH...",
    "..HHHJHHH..",
    ".HHHHHHHHH.",
    ".HGLGSGLGH.",
    ".HHSSSSSHH.",
    ".HHSSMSSHH.",
    ".HHHSSSHHH.",
]
GIRL_PAL = {"H": "#7a4e30", "J": "#b88a5a", "S": "#f2cc9b", "G": "#111111",
            "L": "#dff1ff", "M": "#c0504d"}


def ship():
    """Nave en coordenadas locales (0,0 = esquina trasera del fuselaje)."""
    p = []
    # aletas (rojas)
    for y, x0, x1 in [(3, 7, 8), (4, 6, 9), (5, 5, 10), (6, 4, 11)]:
        p.append(r(x0, y, x1 - x0 + 1, 1, "#f85149"))
    for y, x0, x1 in [(15, 4, 11), (16, 5, 10), (17, 6, 9), (18, 7, 8)]:
        p.append(r(x0, y, x1 - x0 + 1, 1, "#f85149"))
    # tobera
    p.append(r(-3, 10, 3, 4, "#484f58"))
    p.append(r(-4, 10, 1, 4, "#30363d"))
    # fuselaje
    body = [
        (7, 6, 36, "#e6edf3"), (8, 3, 40, "#e6edf3"), (9, 1, 43, "#e6edf3"),
        (10, 0, 45, "#e6edf3"), (11, 0, 45, "#a5b1c2"), (12, 1, 43, "#a5b1c2"),
        (13, 3, 40, "#6e7681"), (14, 6, 36, "#6e7681"),
    ]
    for y, x0, x1, c in body:
        p.append(r(x0, y, x1 - x0 + 1, 1, c))
    p.append(r(3, 11, 36, 1, "#1f6feb"))          # franja azul
    p.append(r(44, 10, 2, 2, "#f85149"))          # punta
    for x in (6, 10, 14):                         # ventanillas
        p.append(r(x, 9, 2, 2, "#79c0ff"))
    # cúpula con la piloto
    for y, x0, x1 in [(-1, 22, 30), (0, 20, 32), (1, 19, 33), (2, 19, 33),
                      (3, 19, 33), (4, 19, 33), (5, 19, 33)]:
        p.append(r(x0, y, x1 - x0 + 1, 1, "#79c0ff", ' opacity="0.45"'))
    p.append(sprite(GIRL, GIRL_PAL, 21, -1))
    p.append(r(20, 1, 1, 2, "#ffffff", ' opacity="0.8"'))   # brillo del cristal
    p.append(r(18, 6, 17, 1, "#8b949e"))                    # base de la cúpula
    # llama del motor
    p.append(r(-14, 10, 10, 4, "#f0883e",
               '><animate attributeName="opacity" values="1;0.35;1" dur="0.2s" repeatCount="indefinite"/></rect><rect width="0" height="0"'))
    p.append(r(-10, 11, 6, 2, "#f2cc3c",
               '><animate attributeName="opacity" values="0.4;1;0.4" dur="0.2s" repeatCount="indefinite"/></rect><rect width="0" height="0"'))
    return "".join(p)


def scene():
    p = [f'<rect width="{W*PX}" height="{H*PX}" fill="{BG}"/>']

    # estrellas (3 capas con parallax)
    p.append(star_layer(26, 1, 1, ["#484f58", "#6e7681"], 60))
    p.append(star_layer(18, 2, 1, ["#8b949e", "#c9d1d9"], 30))
    p.append(star_layer(8, 3, 2, ["#e6edf3", "#ffd866"], 16))

    # estrellas parpadeando fijas
    rnd = random.Random(11)
    for _ in range(14):
        x, y = rnd.randint(2, W - 3), rnd.randint(1, H - 6)
        p.append(
            f'<rect x="{x*PX}" y="{y*PX}" width="{PX}" height="{PX}" fill="#ffffff" opacity="0.2">'
            f'<animate attributeName="opacity" values="0.1;1;0.1" dur="{rnd.choice([2, 2.5, 3, 3.5])}s" '
            f'begin="{round(rnd.uniform(0, 3), 1)}s" repeatCount="indefinite"/></rect>')

    # planetas
    p.append(planet(W + 14, 14, 9, ["#d2a8ff", "#a371f7", "#8957e5", "#6e40c9"], 55, -8, ring="#f2cc9b"))
    p.append(planet(W + 8, 46, 5, ["#79c0ff", "#388bfd", "#1f6feb"], 38, -22))

    # asteroides
    p.append(asteroid(8, 20, -3))
    p.append(asteroid(44, 26, -14, ["..GG.", ".GGGG", "GGDGG", "GGGG.", ".GG.."]))

    # líneas de velocidad
    p.append(streak_layer(10, 5, 1.6))

    # láseres
    for i in range(2):
        p.append(
            f'<g><animateTransform attributeName="transform" type="translate" '
            f'values="0 0;{(W-100)*PX} 0" dur="1.2s" begin="{i*0.6}s" repeatCount="indefinite"/>'
            + r(99, 30, 5, 1, "#3fb950") + r(100, 29, 3, 3, "#3fb950", ' opacity="0.3"')
            + "</g>")

    # nave: flota arriba/abajo
    p.append(
        f'<g transform="translate({52*PX},{20*PX})">'
        f'<g><animateTransform attributeName="transform" type="translate" '
        f'values="0 0;0 {-3*PX};0 0" dur="2.4s" repeatCount="indefinite"/>'
        + ship() + "</g></g>")

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W*PX} {H*PX}" '
            f'width="{W*PX}" height="{H*PX}" role="img" '
            f'aria-label="Maika pilotando una nave espacial pixel art">' + "".join(p) + "</svg>")


def header(lines, width=800, height=90, size=24, cw=14.4):
    per_line = 5.0
    total = per_line * len(lines)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        f'role="img" aria-label="{" / ".join(lines)}">',
        f'<rect width="{width}" height="{height}" rx="8" fill="{BG}"/>',
        f'<rect x="0" y="0" width="{width}" height="26" rx="8" fill="#1f2430"/>',
        # barra de título estilo Windows: icono + título a la izquierda, controles a la derecha
        '<rect x="10" y="7" width="12" height="12" rx="2" fill="#1f6feb"/>'
        '<path d="M13 10 l4 3 -4 3" stroke="#fff" stroke-width="1.6" fill="none"/>'
        '<rect x="17" y="15" width="3" height="1.4" fill="#fff"/>'
        '<text x="30" y="18" fill="#c9d1d9" font-family="Segoe UI,Arial,sans-serif" font-size="12">'
        'Windows PowerShell</text>'
        f'<path d="M{width-130} 13 h10" stroke="#c9d1d9" stroke-width="1.2"/>'
        f'<rect x="{width-85}" y="8.5" width="9" height="9" fill="none" stroke="#c9d1d9" stroke-width="1.2"/>'
        f'<path d="M{width-40} 8.5 l9 9 M{width-31} 8.5 l-9 9" stroke="#c9d1d9" stroke-width="1.2"/>',
    ]
    x0, y = 24, 64
    n = len(lines)
    for i, text in enumerate(lines):
        full = len(text.replace("&gt;", ">")) * cw
        s = i / n
        a, b, c, d = s + 0.02, s + 0.45 / n + 0.02, s + 0.85 / n, s + 0.98 / n
        kt = f"0;{a:.3f};{b:.3f};{c:.3f};{d:.3f};1"
        out.append(
            f'<clipPath id="c{i}"><rect x="{x0}" y="30" height="50" width="0">'
            f'<animate attributeName="width" values="0;0;{full:.0f};{full:.0f};0;0" keyTimes="{kt}" '
            f'dur="{total}s" repeatCount="indefinite"/></rect></clipPath>')
        out.append(
            f'<text x="{x0}" y="{y}" clip-path="url(#c{i})" fill="#3fb950" '
            f'font-family="Consolas,Menlo,monospace" font-size="{size}" xml:space="preserve">{text}</text>')
        out.append(
            f'<rect x="{x0}" y="{y-size+4}" width="8" height="{size}" fill="#e6edf3" opacity="0">'
            f'<animate attributeName="x" values="{x0};{x0};{x0+full:.0f};{x0+full:.0f};{x0};{x0}" keyTimes="{kt}" '
            f'dur="{total}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;1;0;1;0;1;0;1;0" dur="0.8s" repeatCount="indefinite" '
            f'calcMode="discrete" keyTimes="0;0.125;0.25;0.375;0.5;0.625;0.75;0.875;1"/></rect>')
    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    with open(os.path.join(OUT, "nave.svg"), "w", encoding="utf-8") as f:
        f.write(scene())
    with open(os.path.join(OUT, "cabecera.svg"), "w", encoding="utf-8") as f:
        f.write(header([
            "PS&gt; Hola, soy Maika Devops",
            "PS&gt; DevOps + Web",
            "PS&gt; CI/CD, Docker, Cloud",
        ]))
    print("OK -> assets/nave.svg, assets/cabecera.svg")
