"""Render the GitHub social-preview card (1280x640) for n8n-mcp-workflow-setup.
Pillow-based so the text is pixel-perfect. Outputs images/social-preview.png."""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1280, 640
PAD = 84
OUT = os.path.join(os.path.dirname(__file__), "social-preview.png")

# palette
BG = (13, 17, 23)
PINK = (234, 75, 113)
PURPLE = (124, 131, 255)
ORANGE = (217, 119, 87)
TEAL = (45, 212, 191)
WHITE = (255, 255, 255)
GREY = (139, 148, 158)
LIGHT = (201, 209, 217)
BLUE = (88, 166, 255)
GREEN = (31, 122, 61)

FONTS = r"C:\Windows\Fonts"
def font(name, size):
    for n in (name,):
        p = os.path.join(FONTS, n)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

mono_b = lambda s: font("consolab.ttf", s)   # Consolas Bold (mono)
sans   = lambda s: font("segoeui.ttf", s)
sans_b = lambda s: font("segoeuib.ttf", s)
sans_sb= lambda s: font("seguisb.ttf", s)

def radial(size, power=1.4):
    g = Image.new("L", (size, size), 0)
    px = g.load()
    c = size / 2.0
    for y in range(size):
        for x in range(size):
            d = ((x - c) ** 2 + (y - c) ** 2) ** 0.5 / c
            px[x, y] = int(255 * max(0.0, 1 - d) ** power)
    return g

def glow(img, cx, cy, rad, color, strength):
    g = radial(220).resize((rad * 2, rad * 2))
    g = g.point(lambda v: int(v * strength))
    tint = Image.new("RGB", g.size, color)
    img.paste(tint, (cx - rad, cy - rad), g)

img = Image.new("RGB", (W, H), BG)
glow(img, int(W * 0.86), int(-20), 460, PINK, 0.20)
glow(img, int(W * 0.02), int(H * 1.04), 430, TEAL, 0.16)
d = ImageDraw.Draw(img)

def tw(draw, text, fnt):
    b = draw.textbbox((0, 0), text, font=fnt)
    return b[2] - b[0], b[3] - b[1]

# --- top pills ---
def pill(x, y, label, dot):
    f = sans_sb(23)
    tw_, th_ = tw(d, label, f)
    pw = 30 + 18 + tw_ + 22
    ph = 44
    d.rounded_rectangle([x, y, x + pw, y + ph], radius=22, fill=(22, 27, 34), outline=(48, 54, 61), width=1)
    d.ellipse([x + 18, y + ph / 2 - 6, x + 30, y + ph / 2 + 6], fill=dot)
    d.text((x + 30 + 14, y + ph / 2 - th_ / 2 - 3), label, font=f, fill=WHITE)
    return x + pw + 16

px = PAD
py = 70
px = pill(px, py, "n8n", PINK)
px = pill(px, py, "MCP server", PURPLE)
px = pill(px, py, "Claude", ORANGE)

# --- title ---
tf = mono_b(58)
ty = 196
d.text((PAD, ty), "dbDez/", font=tf, fill=GREY)
w1, _ = tw(d, "dbDez/", tf)
d.text((PAD + w1, ty), "n8n-mcp-workflow-setup", font=tf, fill=WHITE)

# --- tagline (manual two lines, bold spans) ---
def line(x, y, parts):
    cx = x
    for text, fnt, col in parts:
        d.text((cx, y), text, font=fnt, fill=col)
        cx += tw(d, text, fnt)[0]

r = sans(31); b = sans_b(31)
ly = 300
line(PAD, ly, [("Upload a workflow to n8n and let an ", r, LIGHT),
               ("MCP server configure & repair it", b, WHITE)])
line(PAD, ly + 44, [("— credentials, models, and the bugs that stop it running.", r, LIGHT)])
line(PAD, ly + 88, [("No manual editor clicking.", b, WHITE)])

# --- flow chips ---
def chip(x, y, label, fnt, fill, outline, txtcol, padx=22, h=52):
    tw_, th_ = tw(d, label, fnt)
    d.rounded_rectangle([x, y, x + padx * 2 + tw_, y + h], radius=12, fill=fill, outline=outline, width=1)
    d.text((x + padx, y + h / 2 - th_ / 2 - 3), label, font=fnt, fill=txtcol)
    return x + padx * 2 + tw_

cy = 478
mono = mono_b(24); sb = sans_sb(24)
x = chip(PAD, cy, "workflow.json", mono, (16, 20, 27), (52, 58, 66), LIGHT)
d.text((x + 16, cy + 12), "→", font=sans(30), fill=GREY); x += 16 + 34 + 16
x = chip(x, cy, "n8n-MCP  update_workflow", sb, (26, 28, 48), (78, 82, 150), WHITE)
d.text((x + 16, cy + 12), "→", font=sans(30), fill=GREY); x += 16 + 34 + 16
# green chip with a hand-drawn check (avoids missing-glyph tofu)
glabel = "runs green"; gf = sans_sb(24)
gtw, gth = tw(d, glabel, gf); gh = 52
gw = 22 + 24 + 12 + gtw + 22
d.rounded_rectangle([x, cy, x + gw, cy + gh], radius=12, fill=GREEN, outline=(46, 160, 84), width=1)
tx = x + 22; tcy = cy + gh / 2
d.line([(tx, tcy + 1), (tx + 8, tcy + 9), (tx + 23, tcy - 10)], fill=WHITE, width=4, joint="curve")
d.text((x + 22 + 24 + 12, cy + gh / 2 - gth / 2 - 3), glabel, font=gf, fill=WHITE)

# --- footer ---
fy = 568
d.text((PAD, fy), "github.com/dbDez/n8n-mcp-workflow-setup", font=mono_b(26), fill=BLUE)
mit_f = sans_sb(22)
mw, _ = tw(d, "MIT", mit_f)
d.text((W - PAD - mw, fy + 3), "MIT", font=mit_f, fill=GREY)

img.save(OUT)
print("Saved", OUT, img.size)
