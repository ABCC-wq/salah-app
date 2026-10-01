import math, os
from PIL import Image, ImageDraw

GOLD = (230, 192, 123, 255)
TOP  = (10, 13, 20)
BOT  = (21, 30, 51)
OUT  = "assets"
os.makedirs(OUT, exist_ok=True)

def gradient(size):
    img = Image.new("RGB", (size, size))
    d = ImageDraw.Draw(img)
    for y in range(size):
        t = y / (size - 1)
        d.line([(0, y), (size, y)],
               fill=tuple(round(TOP[i] + (BOT[i] - TOP[i]) * t) for i in range(3)))
    return img

def arch_points(cx, cy, w, h_below, steps=180):
    """Equilateral pointed arch centred on cx, spring line at cy, legs of length h_below."""
    left, right = cx - w / 2, cx + w / 2
    base = cy + h_below
    pts = [(left, base), (left, cy)]
    for i in range(steps + 1):                       # left curve: 180deg -> 120deg
        th = math.radians(180 - 60 * i / steps)
        pts.append((right + w * math.cos(th), cy - w * math.sin(th)))
    for i in range(steps + 1):                       # right curve: 60deg -> 0deg
        th = math.radians(60 - 60 * i / steps)
        pts.append((left + w * math.cos(th), cy - w * math.sin(th)))
    pts += [(right, base)]
    return pts

def draw_arch(img, scale=1.0):
    S = img.size[0]
    w = 0.371 * S * scale                 # arch width
    leg = 0.137 * S * scale               # straight leg below the spring line
    cx = S / 2
    apex_off = w * math.sqrt(3) / 2
    cy = S / 2 + (apex_off - leg) / 2     # vertically centre the whole shape
    d = ImageDraw.Draw(img)
    d.polygon(arch_points(cx, cy, w, leg), fill=GOLD)
    return img

def niche(size, scale=1.0, inner=0.62, bg=None):
    """Gold mihrab arch with the centre cut away, leaving a solid niche frame."""
    base = bg.copy() if bg else Image.new("RGBA", (size, size), (0, 0, 0, 0))
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw_arch(layer, scale)
    cut = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw_arch(cut, scale * inner)
    mask = Image.new("L", (size, size), 0)
    mask.paste(255, (0, 0), cut)
    layer.putalpha(Image.composite(Image.new("L", (size, size), 0), layer.split()[3], mask))
    base.alpha_composite(layer)
    return base

# icon.png — full square artwork
icon = niche(1024, 1.0, bg=gradient(1024).convert("RGBA"))
icon.convert("RGB").save(f"{OUT}/icon.png")

# adaptive icon background
gradient(1024).save(f"{OUT}/icon-background.png")

# adaptive icon foreground — smaller, so Android's circular mask never clips it
niche(1024, 0.80).save(f"{OUT}/icon-foreground.png")

# splash screens
for name in ("splash.png", "splash-dark.png"):
    sp = niche(2732, 0.34, bg=gradient(2732).convert("RGBA"))
    sp.convert("RGB").save(f"{OUT}/{name}")

print("wrote:", sorted(os.listdir(OUT)))
