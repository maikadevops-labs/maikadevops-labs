"""Genera los SVG animados del README (escritorio en el espacio + cabecera que se teclea).

Uso:  python tools/generate_assets.py
Salida: assets/maika-espacio.svg, assets/terminal.svg
"""
import math
import os
import random

OUT = os.path.join(os.path.dirname(__file__), "..", "assets")
os.makedirs(OUT, exist_ok=True)

PX = 4            # tamaño de cada "pixel"
W, H = 160, 60    # grid -> 640 x 240
BG = "#0b0f1a"
FLOOR = 50        # fila donde empieza el suelo


def r(x, y, w=1, h=1, fill="#fff", extra=""):
    return (f'<rect x="{x*PX}" y="{y*PX}" width="{w*PX}" height="{h*PX}" '
            f'fill="{fill}" shape-rendering="crispEdges"{extra}/>')


def sprite(rows, palette, ox, oy):
    """Dibuja un sprite desde ASCII; los caracteres sin color son transparentes."""
    out = []
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in palette:
                out.append(r(ox + x, oy + y, 1, 1, palette[ch]))
    return "".join(out)


def drift(content, dx, dy, dur, begin=0):
    return (f'<g><animateTransform attributeName="transform" type="translate" '
            f'values="0 0;{dx} {dy}" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
            f'{content}</g>')


def star_layer(n, seed, size, colors, dur):
    """Capa de estrellas que se desplaza a la izquierda en bucle sin cortes."""
    rnd = random.Random(seed)
    stars = [(rnd.randint(0, W - 1), rnd.randint(0, FLOOR - 3), rnd.choice(colors)) for _ in range(n)]
    items = [r(x + off, y, size, size, c) for off in (0, W) for x, y, c in stars]
    return drift("".join(items), -W * PX, 0, dur)


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
    return drift("".join(parts), -(W + 2 * rad + 22) * PX, 0, dur, begin)


def rocket(y, scale, dur, begin, body="#e6edf3", fin="#f85149"):
    """Cohete apuntando a la izquierda que cruza de derecha a izquierda."""
    p = [
        r(3, 1, 8, 1, body), r(1, 2, 11, 1, body), r(3, 3, 8, 1, "#a5b1c2"),
        r(0, 2, 2, 1, fin), r(8, 0, 3, 1, fin), r(8, 4, 3, 1, fin),
        r(6, 2, 2, 1, "#79c0ff"),
        r(12, 2, 5, 1, "#f0883e",
          '><animate attributeName="opacity" values="1;0.3;1" dur="0.2s" repeatCount="indefinite"/></rect><rect width="0" height="0"'),
        r(12, 1, 2, 1, "#f2cc3c"), r(12, 3, 2, 1, "#f2cc3c"),
    ]
    # el cohete mira hacia su dirección de viaje (abajo a la izquierda)
    dx, dy = -(W + 40), 60
    angle = -math.degrees(math.atan2(dy, -dx))
    inner = (f'<g transform="scale({scale}) rotate({angle:.1f} {8.5*PX} {2.5*PX})">'
             + "".join(p) + "</g>")
    start = (W + 4) * PX
    return (f'<g transform="translate({start},{y*PX})">'
            + drift(inner, dx * PX, dy * PX, dur, begin) + "</g>")


def asteroid(y, dur, begin, rows=None):
    rows = rows or [".GG.", "GGGG", "GDGG", ".GG."]
    s = sprite(rows, {"G": "#6e7681", "D": "#484f58"}, W + 2, y)
    return drift(s, -(W + 10) * PX, 4 * PX, dur, begin)


# --- personaje: pelo largo amarillo, lentes, sudadera morada -----------------
GIRL = [
    "...HJHHH...",
    "..HHHJHHH..",
    ".HHHHHHHHH.",
    ".HGLGSGLGH.",
    ".HHSSSSSHH.",
    ".HHSSMSSHH.",
    ".HHHSSSHHH.",
    "..HHSSSHH..",
    ".HHPPPPPHH.",
    ".HPPPPPPPH.",
    ".HPPPPPPPH.",
    ".HHPPPPPHH.",
    "..HPPPPPH..",
]
GIRL_PAL = {"H": "#f2c94c", "J": "#ffe58a", "S": "#f2cc9b", "G": "#111111", "L": "#dff1ff",
            "M": "#c0504d", "P": "#8957e5", "B": "#1f6feb", "K": "#e6edf3"}
GIRL_X = 46
GIRL_Y = 31       # sentada: la cabeza queda a la altura de la pantalla
MOON = ["..WWW.", ".WWW..", "WWW...", "WWW...", "WWW...", ".WWW..", "..WWW."]

HEART = [".GG.GG.", "GGGGGGG", "GGGGGGG", ".GGGGG.", "..GGG..", "...G..."]


def scene():
    p = [f'<rect width="{W*PX}" height="{H*PX}" fill="{BG}"/>']

    # espacio: estrellas con parallax, parpadeos, planetas, asteroides
    p.append(star_layer(26, 1, 1, ["#484f58", "#6e7681"], 60))
    p.append(star_layer(18, 2, 1, ["#8b949e", "#c9d1d9"], 30))
    p.append(star_layer(8, 3, 2, ["#e6edf3", "#ffd866"], 16))
    rnd = random.Random(11)
    for _ in range(14):
        x, y = rnd.randint(2, W - 3), rnd.randint(1, FLOOR - 6)
        p.append(
            f'<rect x="{x*PX}" y="{y*PX}" width="{PX}" height="{PX}" fill="#ffffff" opacity="0.2">'
            f'<animate attributeName="opacity" values="0.1;1;0.1" dur="{rnd.choice([2, 2.5, 3, 3.5])}s" '
            f'begin="{round(rnd.uniform(0, 3), 1)}s" repeatCount="indefinite"/></rect>')
    p.append(sprite(MOON, {"W": "#e6edf3"}, 140, 5))
    p.append(asteroid(6, 20, -3))
    p.append(asteroid(24, 26, -14, ["..GG.", ".GGGG", "GGDGG", "GGGG.", ".GG.."]))

    # cohetes que pasan
    p.append(rocket(-6, 1, 9, 0))
    p.append(rocket(-26, 2, 13, -6, body="#c9d1d9", fin="#58a6ff"))

    # suelo (asteroide plano)
    p.append(r(0, FLOOR, W, H - FLOOR, "#161b22"))
    p.append(r(0, FLOOR, W, 1, "#30363d"))
    for x, y, w in [(8, 53, 4), (30, 56, 3), (96, 54, 5), (120, 57, 3), (145, 53, 4), (70, 57, 2)]:
        p.append(r(x, y, w, 1, "#21262d"))

    # rack de servidores con LEDs
    rx, ry = 124, 34
    p.append(r(rx, ry, 10, FLOOR - ry, "#21262d"))
    p.append(r(rx, ry, 10, 1, "#30363d"))
    colors = ["#3fb950", "#d29922", "#f85149", "#58a6ff"]
    rnd = random.Random(4)
    for row in range(4):
        y = ry + 2 + row * 3
        p.append(r(rx + 1, y, 8, 2, "#0d1117"))
        for c in range(3):
            p.append(
                f'<rect x="{(rx+2+c*2)*PX}" y="{y*PX}" width="{PX}" height="{PX}" fill="{colors[(row+c)%4]}">'
                f'<animate attributeName="opacity" values="1;0.15;1" dur="{rnd.choice([0.8,1.2,1.6,2.0])}s" '
                f'begin="{round(rnd.uniform(0,1.5),1)}s" repeatCount="indefinite"/></rect>')

    # silla y piernas (van detrás del escritorio)
    gx = GIRL_X
    p.append(r(gx - 3, 36, 2, 12, "#484f58"))            # respaldo
    p.append(r(gx + 1, 46, 11, 2, "#6e7681"))            # asiento
    p.append(r(gx + 5, 48, 2, 1, "#484f58"))             # pie de la silla
    p.append(r(gx + 1, 49, 11, 1, "#484f58"))            # base
    p.append(r(gx + 2, 44, 13, 2, "#1f6feb"))            # cadera y muslos
    p.append(r(gx + 13, 46, 2, 3, "#1f6feb"))            # pantorrilla
    p.append(r(gx + 13, 49, 4, 1, "#e6edf3"))            # zapato

    # escritorio
    dx0, dx1, dy = 56, 112, 44
    p.append(r(dx0, dy, dx1 - dx0, 1, "#a06a42"))
    p.append(r(dx0, dy + 1, dx1 - dx0, 1, "#6e4a2e"))
    p.append(r(dx0 + 2, dy + 2, 2, FLOOR - dy - 2, "#6e4a2e"))
    p.append(r(dx1 - 4, dy + 2, 2, FLOOR - dy - 2, "#6e4a2e"))

    # laptop con código que se escribe
    lx, ly = 71, 31
    p.append(r(lx, ly, 19, 12, "#484f58"))
    p.append(r(lx + 1, ly + 1, 17, 10, "#0b1d33"))
    p.append(r(lx - 2, 43, 23, 1, "#8b949e"))
    p.append(r(lx + 7, 43, 5, 1, "#6e7681"))
    for i, (dy2, wl, col) in enumerate([(2, 8, "#3fb950"), (4, 12, "#58a6ff"),
                                        (6, 7, "#d2a8ff"), (8, 10, "#ffa657")]):
        ind = 1 if i in (1, 3) else 0
        p.append(
            f'<rect x="{(lx+2+ind)*PX}" y="{(ly+dy2)*PX+1}" height="{PX-2}" fill="{col}" width="0">'
            f'<animate attributeName="width" values="0;0;{wl*PX};{wl*PX};0" '
            f'keyTimes="0;{0.05+i*0.18:.2f};{0.18+i*0.18:.2f};0.93;1" dur="6s" repeatCount="indefinite"/></rect>')

    # taza con vapor
    p.append(sprite(["MMMM.", "MMMMM", "MMMM.", "MMMM."], {"M": "#e6edf3"}, 98, 40))
    for i, sx in enumerate((98, 100)):
        p.append(
            f'<rect x="{sx*PX+2}" y="{38*PX}" width="{PX//2}" height="{PX}" fill="#8b949e" opacity="0">'
            f'<animate attributeName="opacity" values="0;0.8;0" dur="2s" begin="{i*0.8}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0 0;0 -{PX*2}" '
            f'dur="2s" begin="{i*0.8}s" repeatCount="indefinite"/></rect>')

    # Maika
    p.append(sprite(GIRL, GIRL_PAL, GIRL_X, GIRL_Y))
    # brazo: hombro -> antebrazo con manga -> mano sobre el teclado (la mano teclea)
    p.append(r(gx + 9, 39, 2, 4, "#8957e5"))             # brazo superior
    p.append(r(gx + 9, 42, 11, 2, "#8957e5"))            # antebrazo
    p.append(
        '<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -4;0 0" '
        'dur="0.4s" repeatCount="indefinite"/>'
        + r(gx + 20, 42, 4, 2, "#f2cc9b") + "</g>")

    # corazón verde latiendo
    p.append(drift(sprite(HEART, {"G": "#3fb950"}, 36, 24), 0, -6 * PX, 1.6) .replace(
        'values="0 0;0 -24"', 'values="0 0;0 -24;0 0"'))

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W*PX} {H*PX}" '
            f'width="{W*PX}" height="{H*PX}" role="img" '
            f'aria-label="Maika en su escritorio con laptop en el espacio, con cohetes pasando">'
            + "".join(p) + "</svg>")


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
    with open(os.path.join(OUT, "maika-espacio.svg"), "w", encoding="utf-8") as f:
        f.write(scene())
    with open(os.path.join(OUT, "terminal.svg"), "w", encoding="utf-8") as f:
        f.write(header([
            "PS&gt; Hola, soy Maika Devops",
            "PS&gt; DevOps + Web",
            "PS&gt; CI/CD, Docker, Cloud",
        ]))
    print("OK -> assets/maika-espacio.svg, assets/terminal.svg")
