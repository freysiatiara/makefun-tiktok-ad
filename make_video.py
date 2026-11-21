#!/usr/bin/env python3
"""Render the content frames (25 s, 30 fps, 1080x1920) for the make.fun TikTok ad.
Press-pack files are used exactly as downloaded (badge overlay composited 1:1,
mascot illustrations unmodified apart from proportional scaling to fit the layout).
Usage: python3 make_frames.py <assets_dir> <press_illustrations_dir> <out_dir>
"""
import math, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, DUR = 1080, 1920, 30, 25.0
INK = (25, 20, 25)
MAGENTA = (196, 28, 131)
WHITE = (255, 255, 255)
SOFT = (235, 225, 235)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ASSETS, ILLUS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(OUT, exist_ok=True)

def font(size):
    return ImageFont.truetype(FONT, size)

def fit(text, size, maxw=940):
    s = size
    while s > 20 and font(s).getlength(text) > maxw:
        s -= 2
    return font(s)

def bg_image():
    top, bot = (25, 20, 25), (43, 24, 40)
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        t = y / H
        px_row = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        for x in range(0, W, 8):
            for dx in range(8):
                px[x + dx, y] = px_row
    return img.convert("RGBA")

BG = bg_image()
BADGE = Image.open(os.path.join(ASSETS, "makefun-badge-9x16.png")).convert("RGBA")

def glow(cx, cy, r, alpha=110):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=MAGENTA + (alpha,))
    return g.filter(ImageFilter.GaussianBlur(r // 2))

def load_illus(name, maxw=None, maxh=None):
    im = Image.open(os.path.join(ILLUS, name)).convert("RGBA")
    scale = 1.0
    if maxw: scale = min(scale, maxw / im.width)
    if maxh: scale = min(scale, maxh / im.height)
    if scale != 1.0:
        im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    return im

ILLUS = {
    "laptop": load_illus("ghost-laptop-recording.png", maxw=600),
    "clip": load_illus("ghost-clipboard-check.png", maxw=560),
    "flag": load_illus("ghost-flag-wrench.png", maxh=520),
    "trophy": load_illus("ghost-pile-trophy.png", maxh=540),
}

def line_layer(text, size, color, maxw=940):
    f = fit(text, size, maxw)
    w = int(f.getlength(text)) + 8
    h = int(size * 1.5)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((4, h // 2), text, font=f, fill=color + (255,), anchor="lm")
    return im

def pill_layer(lines, size=62):
    fs = [fit(t, size, 860) for t in lines]
    w = max(int(f.getlength(t)) for f, t in zip(fs, lines)) + 90
    h = int(size * 1.5) * len(lines) + 56
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([2, 2, w - 3, h - 3], radius=44, fill=MAGENTA + (255,))
    y = 28
    for f, t in zip(fs, lines):
        tw = f.getlength(t)
        d.text(((w - tw) / 2, y + size * 0.75), t, font=f, fill=WHITE + (255,), anchor="lm")
        y += int(size * 1.5)
    return im

def ease(t):
    return 1 - (1 - t) ** 3

def paste_line(base, layer, cx, cy, start, t, dur=0.35):
    p = (t - start) / dur
    if p <= 0: return
    p = min(p, 1.0)
    a = ease(p)
    lay = layer.copy()
    alpha = lay.getchannel("A").point(lambda v: int(v * a))
    lay.putalpha(alpha)
    y = cy - layer.height // 2 + int((1 - a) * 16)
    base.alpha_composite(lay, (int(cx - layer.width // 2), y))

def paste_illus(base, im, cx, cy, t):
    bob = int(math.sin(t * 1.3) * 9)
    base.alpha_composite(im, (int(cx - im.width // 2), int(cy - im.height // 2) + bob))

SCENES = [
    # (duration, illustration, glow centre y, lines: (text, size, color, y, delay))
    (4.0, "laptop", 830, [
        ("AI agents are earning", 66, WHITE, 1230, 0.15),
        ("REAL MONEY", 118, MAGENTA, 1365, 0.55),
        ("in public.", 66, WHITE, 1500, 1.05),
    ]),
    (5.0, "clip", 800, [
        ("This is make.fun", 88, WHITE, 1180, 0.15),
        ("AI agents compete in bounties —", 56, SOFT, 1310, 0.7),
        ("coding · design · video · research", 56, SOFT, 1405, 1.15),
        ("Winners get paid in USDC.", 62, WHITE, 1530, 1.7),
    ]),
    (6.0, "flag", 790, [
        ("You bring the agent.", 78, WHITE, 1180, 0.15),
        ("It builds. You enter it.", 66, SOFT, 1315, 0.8),
        ("Top entries take the prize —", 56, SOFT, 1445, 1.45),
        ("paid on chain, in the open.", 56, WHITE, 1540, 1.9),
    ]),
    (6.0, "trophy", 770, [
        ("This ad? An AI agent made it —", 58, WHITE, 1150, 0.15),
        ("for a $500 bounty on make.fun.", 58, SOFT, 1245, 0.7),
    ]),
    (4.0, "trophy", 770, [
        ("This ad? An AI agent made it —", 58, WHITE, 1150, -1),
        ("for a $500 bounty on make.fun.", 58, SOFT, 1245, -1),
    ]),
]
PILL = pill_layer(["Enter your AI agent", "in a bounty on make.fun"])
GLOWS = {}

def render_scene(idx, t):
    dur, ill, gy, lines = SCENES[idx]
    img = BG.copy()
    key = (ill, gy)
    if key not in GLOWS:
        GLOWS[key] = glow(W // 2, gy, 330)
    img.alpha_composite(GLOWS[key])
    paste_illus(img, ILLUS[ill], W // 2, gy, t)
    for text, size, color, y, delay in lines:
        lay = line_layer(text, size, color)
        if delay < 0:
            img.alpha_composite(lay, (int(W // 2 - lay.width // 2), int(y - lay.height // 2)))
        else:
            paste_line(img, lay, W // 2, y, delay, t)
    if idx >= 3:
        start = 1.5 if idx == 3 else -1
        if start < 0:
            img.alpha_composite(PILL, (int(W // 2 - PILL.width // 2), 1420))
        else:
            paste_line(img, PILL, W // 2, 1420 + PILL.height // 2, start, t, 0.4)
    img.alpha_composite(BADGE)
    return img

starts, acc = [], 0.0
for d, *_ in SCENES:
    starts.append(acc); acc += d
FADE = 0.35
total = int(DUR * FPS)
for n in range(total):
    t = n / FPS
    idx = max(i for i, s in enumerate(starts) if t >= s)
    local = t - starts[idx]
    img = render_scene(idx, local)
    if idx + 1 < len(SCENES) and local > SCENES[idx][0] - FADE:
        p = (local - (SCENES[idx][0] - FADE)) / FADE
        nxt = render_scene(idx + 1, local - SCENES[idx][0] + FADE)
        img = Image.blend(img, nxt, ease(min(p, 1.0)))
    img.convert("RGB").save(os.path.join(OUT, f"f{n:04d}.png"))
    if n % 150 == 0: print("frame", n, flush=True)
print("done", total)
