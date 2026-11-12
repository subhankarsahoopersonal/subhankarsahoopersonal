"""Builds every graphic in the Subhankar Sahoo GitHub profile README."""
import base64
import io
import os
import re
from html import escape

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from PIL import Image
import logging
logging.getLogger('fontTools').setLevel(logging.ERROR)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
OUT = os.path.join(ROOT, "assets")

# Custom palette - Emerald Green Theme
GREEN = "#10b981"  
INK = "#0b0c10"
CREAM = "#f7f0dc"
INDIGO = "#2a1b72"
INDIGO_DEEP = "#1e1670"
PINK = "#f472b6"
VIOLET = "#a855f7"
CYAN = "#22d3ee"

THEMES = {
    "dark": dict(bg="#0e0f14", card="#13141b", card2="#181a23", line="rgba(255,255,255,0.09)",
                 text="#f7f0dc", muted="#9aa0ad", chip="#1d1f2a", chiptext="#d9dbe2", tile="#1b1d27"),
    "light": dict(bg="#fbf8f1", card="#ffffff", card2="#f6f1e4", line="rgba(11,12,16,0.10)",
                  text="#0b0c10", muted="#5d6270", chip="#f2ecdd", chiptext="#2a2d36", tile="#f4efe3"),
}

# Embedded missing icons
BUILTIN_ICONS = {
    "kotlin": "M24 24H0V0h24L12 12Z",
    "android": "M17.5 15.34c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1m-11 0c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1m13.78-7.58l1.9-3.28c.11-.19.04-.44-.15-.55-.19-.11-.43-.04-.54.15l-1.93 3.34c-2.12-.96-4.49-1.49-7.05-1.49-2.55 0-4.92.53-7.04 1.49l-1.94-3.34c-.11-.19-.35-.26-.54-.15-.19.11-.26.36-.15.55l1.91 3.28C2.26 9.61 0 13.9 0 18.79h24c0-4.89-2.26-9.18-5.72-11.03z",
    "docker": "M13.98 11.08h2.12a.19.19 0 0 0 .19-.19V9.01a.19.19 0 0 0-.19-.19h-2.12a.18.18 0 0 0-.18.18v1.9c0 .1.08.18.18.18m-2.95-5.43h2.12a.19.19 0 0 0 .18-.18V3.57a.19.19 0 0 0-.18-.18h-2.12a.19.19 0 0 0-.18.18v1.9c0 .1.08.18.18.18m-2.95 2.71h2.12a.19.19 0 0 0 .18-.18V6.28a.19.19 0 0 0-.18-.18h-2.12a.19.19 0 0 0-.18.18v1.9c0 .1.08.18.18.18m-2.96 0h2.12a.19.19 0 0 0 .19-.18V6.28a.19.19 0 0 0-.19-.18H5.12a.19.19 0 0 0-.19.18v1.9c0 .1.09.18.19.18m2.96 2.72h2.12a.19.19 0 0 0 .18-.19V9.01a.19.19 0 0 0-.18-.19h-2.12a.18.18 0 0 0-.18.19v1.9c0 .1.08.19.18.19m-2.96 0h2.12a.19.19 0 0 0 .19-.19V9.01a.19.19 0 0 0-.19-.19H5.12a.19.19 0 0 0-.19.19v1.9c0 .1.09.19.19.19m-2.96 0h2.12a.19.19 0 0 0 .19-.19V9.01a.19.19 0 0 0-.19-.19H2.16a.19.19 0 0 0-.19.19v1.9c0 .1.09.19.19.19m0-2.72h2.12a.19.19 0 0 0 .19-.18V6.28a.19.19 0 0 0-.19-.18H2.16a.19.19 0 0 0-.19.18v1.9c0 .1.09.18.19.18m17.59 1.45c-.24 0-.48.04-.72.1a7.83 7.83 0 0 0-3.3-1.63 1.95 1.95 0 0 0-1.89-1.28c-1.07 0-1.95.88-1.95 1.95v.35H1.47a.78.78 0 0 0-.78.78v.83c0 4.19 3.4 7.6 7.6 7.6h1.22c2.81 0 5.46-1.57 6.84-4.08h2.09c1.93 0 3.49-1.56 3.49-3.49s-1.56-3.49-3.49-3.49zm-.57 5.8h-2.61l-.22.42a8.68 8.68 0 0 1-6.14 3.23H7.6a6.83 6.83 0 0 1-6.82-6.82v-.05h13.93c0-1.8 1.45-3.26 3.26-3.26s3.26 1.46 3.26 3.26c0 1.76-1.4 3.19-3.15 3.22z",
    "arduino": "M23.82 12a5.78 5.78 0 0 0-1.58-4.09 5.87 5.87 0 0 0-8.29-.1l-1.95 1.95-1.95-1.95a5.87 5.87 0 0 0-8.29.1A5.78 5.78 0 0 0 .18 12a5.78 5.78 0 0 0 1.58 4.09 5.87 5.87 0 0 0 8.29.1l1.95-1.95 1.95 1.95a5.87 5.87 0 0 0 8.29-.1 5.78 5.78 0 0 0 1.58-4.09zm-8.86 2.37v-1.39h-1.38V11.6h1.38v-1.4h1.4v1.4h1.38v1.38h-1.38v1.39h-1.4zm-9.33-1.39h4.15V11.6H5.63v1.38zm6.37-6.38a4.01 4.01 0 0 1 5.67-.07 3.96 3.96 0 0 1 1.09 2.8 3.97 3.97 0 0 1-1.09 2.81 4.01 4.01 0 0 1-5.67.07l-2.58-2.58 2.58-2.61a.95.95 0 0 0 0-1.4.95.95 0 0 0-1.4 0zm0 0a4.01 4.01 0 0 1-5.67.07l-2.58 2.61 2.58 2.58a4.01 4.01 0 0 1 5.67-.07 3.96 3.96 0 0 1 1.09-2.8 3.97 3.97 0 0 1-1.09-2.81zm-3.23 2.15a1.21 1.21 0 0 1 1.2 1.21 1.21 1.21 0 0 1-1.2 1.2 1.21 1.21 0 0 1-1.2-1.2 1.21 1.21 0 0 1 1.2-1.21z",
    "github": "M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12",
    "git": "M23.546 10.93 13.067.452a2.98 2.98 0 0 0-4.214 0L.45 8.854a2.98 2.98 0 0 0 0 4.214l10.478 10.478a2.98 2.98 0 0 0 4.214 0l8.403-8.402a2.98 2.98 0 0 0 0-4.214zM10.96 17.502a1.86 1.86 0 0 1-3.719 0 1.86 1.86 0 0 1 3.719 0zm0-7.79a1.86 1.86 0 0 1-3.719 0 1.86 1.86 0 0 1 3.719 0zm6.543 3.031a1.86 1.86 0 0 1-3.72 0 1.86 1.86 0 0 1 3.72 0z"
}

FONT_SRC = {
    "geist": os.path.join(TOOLS, "fonts", "Geist.ttf"),
    "mono": os.path.join(TOOLS, "fonts", "GeistMono.ttf"),
    "oxanium": os.path.join(TOOLS, "fonts", "Oxanium.ttf"),
}
_static = {}

def static_font(key, weight):
    k = (key, weight)
    if k not in _static:
        f = TTFont(FONT_SRC[key])
        _static[k] = instancer.instantiateVariableFont(f, {"wght": weight})
    return _static[k]

def text_width(s, key, weight, size, spacing=0.0):
    f = static_font(key, weight)
    cmap = f.getBestCmap()
    hmtx = f["hmtx"]
    upm = f["head"].unitsPerEm
    w = 0
    for ch in s:
        g = cmap.get(ord(ch))
        w += hmtx[g][0] if g else upm * 0.5
    return w * size / upm + spacing * len(s)

def font_face(key, weight, family, chars):
    f = static_font(key, weight)
    buf = io.BytesIO()
    f.save(buf)
    buf.seek(0)
    sub = TTFont(buf)
    opts = subset.Options()
    opts.flavor = "woff"
    opts.layout_features = ["kern", "liga"]
    s = subset.Subsetter(opts)
    s.populate(text="".join(sorted(set(chars))) + " ")
    s.subset(sub)
    out = io.BytesIO()
    sub.flavor = "woff"
    sub.save(out)
    b64 = base64.b64encode(out.getvalue()).decode()
    return f"@font-face{{font-family:'{family}';src:url(data:font/woff;base64,{b64}) format('woff');}}"

FAMILIES = {
    "G4": ("geist", 400), "G5": ("geist", 500), "G6": ("geist", 600), "G8": ("geist", 800),
    "M5": ("mono", 500), "X7": ("oxanium", 700),
}

class Svg:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.parts, self.defs, self.css = [], []
        self.used = {}

    def add(self, s):
        self.parts.append(s)

    def text(self, x, y, s, fam, size, fill, anchor="start", spacing=0, extra="", cls=""):
        self.used.setdefault(fam, set()).update(s)
        ls = f' letter-spacing="{spacing}"' if spacing else ""
        c = f' class="{cls}"' if cls else ""
        self.add(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" fill="{fill}" '
                 f'text-anchor="{anchor}"{ls}{c} {extra}>{escape(s)}</text>')

    def render(self):
        faces = "".join(font_face(*FAMILIES[f], f, chars) for f, chars in self.used.items())
        return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                f'width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">'
                f'<defs><style>{faces}{"".join(self.css)}</style>{"".join(self.defs)}</defs>'
                f'{"".join(self.parts)}</svg>')

def save(svg, *path):
    p = os.path.join(OUT, *path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    data = svg.render() if isinstance(svg, Svg) else svg
    with open(p, "w") as fh:
        fh.write(data)
    return len(data)

def find_image(slug):
    dirs_to_check = [
        os.path.join(ROOT, "images"),
        os.path.join(TOOLS, "images"),
        os.path.join(OUT, "images"),
        ROOT,
    ]
    exts_to_check = [".webp", ".png", ".jpg", ".jpeg", ""]
    for d in dirs_to_check:
        for ext in exts_to_check:
            p = os.path.join(d, f"{slug}{ext}")
            if os.path.exists(p) and os.path.isfile(p):
                return p
            if ext != "":
                p_double = os.path.join(d, f"{slug}.webp{ext}")
                if os.path.exists(p_double) and os.path.isfile(p_double):
                    return p_double
    return None

def img_uri(slug, w, h=None, crop=None, fmt="JPEG", q=82, cover=True):
    path = find_image(slug)
    if path:
        try:
            im = Image.open(path)
        except Exception:
            im = Image.new("RGB", (w, h or w), "#1b1d27")
    else:
        im = Image.new("RGB", (w, h or w), "#1b1d27")
        
    im = im.convert("RGBA" if fmt in ("PNG", "WEBP") else "RGB")
    if crop:
        im = im.crop(crop)
    if h:
        if cover:
            sc = max(w / im.width, h / im.height)
            im = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
            l, t = (im.width - w) // 2, 0
            im = im.crop((l, t, l + w, t + h))
        else:
            im.thumbnail((w, h), Image.LANCZOS)
    else:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, fmt, quality=q, method=6) if fmt == "WEBP" else im.save(buf, fmt, quality=q, optimize=True)
    mime = {"JPEG": "jpeg", "PNG": "png", "WEBP": "webp"}[fmt]
    return f"data:image/{mime};base64,{base64.b64encode(buf.getvalue()).decode()}", im.size

def icon_path(name):
    if name in BUILTIN_ICONS:
        return BUILTIN_ICONS[name]
    src = open(os.path.join(TOOLS, "icons", f"{name}.svg")).read()
    return re.search(r'<path d="([^"]+)"', src).group(1)

def icon(name, x, y, size, fill):
    s = size / 24
    return f'<path transform="translate({x} {y}) scale({s})" d="{icon_path(name)}" fill="{fill}"/>'

GLOBE = ("M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Zm6.9 6h-2.95a15.7 15.7 0 0 0-1.38-3.56A8.03 8.03 0 0 1 "
         "18.9 8ZM12 4.04c.83 1.2 1.48 2.53 1.91 3.96h-3.82c.43-1.43 1.08-2.76 1.91-3.96ZM4.26 14a8.2 8.2 0 0 1 "
         "0-4h3.38a16.5 16.5 0 0 0 0 4H4.26Zm.84 2h2.95c.32 1.25.78 2.45 1.38 3.56A7.99 7.99 0 0 1 5.1 16Zm2.95-8"
         "H5.1a7.99 7.99 0 0 1 4.33-3.56A15.7 15.7 0 0 0 8.05 8ZM12 19.96A14.1 14.1 0 0 1 10.09 16h3.82A14.1 14.1 0 "
         "0 1 12 19.96ZM14.34 14H9.66a14.7 14.7 0 0 1 0-4h4.68a14.7 14.7 0 0 1 0 4Zm.25 5.56c.6-1.11 1.06-2.31 1.38"
         "-3.56h2.95a8.03 8.03 0 0 1-4.33 3.56ZM16.36 14a16.5 16.5 0 0 0 0-4h3.38a8.2 8.2 0 0 1 0 4h-3.38Z")

def raw_icon(d, x, y, size, fill):
    return f'<path transform="translate({x} {y}) scale({size / 24})" d="{d}" fill="{fill}"/>'

def wrap(s, key, weight, size, maxw):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_width(t, key, weight, size) > maxw and cur:
            lines.append(cur)
            cur = w
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines

def hero():
    W, H = 1280, 560
    s = Svg(W, H)
    s.defs.append(f'''
<clipPath id="frame"><rect width="{W}" height="{H}" rx="28"/></clipPath>
<radialGradient id="gIndigo" cx="0.22" cy="0.05" r="0.75"><stop offset="0" stop-color="#3b22b8" stop-opacity="0.95"/>
 <stop offset="0.45" stop-color="{INDIGO_DEEP}" stop-opacity="0.55"/><stop offset="1" stop-color="{INK}" stop-opacity="0"/></radialGradient>
<radialGradient id="gGreen" cx="0.62" cy="1.05" r="0.55"><stop offset="0" stop-color="{GREEN}" stop-opacity="0.75"/>
 <stop offset="0.5" stop-color="#047857" stop-opacity="0.25"/><stop offset="1" stop-color="{INK}" stop-opacity="0"/></radialGradient>
<radialGradient id="gHalo" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{GREEN}" stop-opacity="0.55"/>
 <stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></radialGradient>
<linearGradient id="gName" x1="0" x2="1"><stop offset="0" stop-color="{GREEN}"/><stop offset="0.55" stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>
<pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse"><path d="M48 0H0V48" fill="none" stroke="#ffffff" stroke-opacity="0.045"/></pattern>
<linearGradient id="fadeBottom" x1="0" y1="0" x2="0" y2="1"><stop offset="0.72" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<mask id="photoMask"><rect width="{W}" height="{H}" fill="url(#fadeBottom)"/></mask>''')
    s.css.append('.up{opacity:0;animation:up .9s cubic-bezier(.2,.7,.2,1) forwards}'
                 '@keyframes up{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}'
                 '.float{animation:float 6s ease-in-out infinite}'
                 '@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}'
                 '.pulse{animation:pulse 2s ease-out infinite;transform-origin:center;transform-box:fill-box}'
                 '@keyframes pulse{0%{opacity:.8;transform:scale(1)}100%{opacity:0;transform:scale(2.6)}}'
                 '.blink{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}')
    
    s.add('<g clip-path="url(#frame)">')
    s.add(f'<rect width="{W}" height="{H}" fill="{INK}"/><rect width="{W}" height="{H}" fill="url(#grid)"/>')
    s.add(f'<rect width="{W}" height="{H}" fill="url(#gIndigo)"/><rect width="{W}" height="{H}" fill="url(#gGreen)"/>')
    
    s.add(f'<circle cx="1010" cy="330" r="260" fill="url(#gHalo)"/>')
    uri, (pw, ph) = img_uri("profile-pic", 470, fmt="WEBP", q=80)
    s.add(f'<image href="{uri}" x="{1240 - pw}" y="{H - ph + 40}" width="{pw}" height="{ph}" mask="url(#photoMask)"/>')
    
    chips = [("Kotlin", "kotlin", 770, 190, 0), ("Docker", "docker", 1120, 150, 1.5),
             ("Arduino", "arduino", 790, 400, 3), ("Next.js", "nextdotjs", 1090, 455, 4.5)]
    for label, ic, x, y, d in chips:
        w = text_width(label, "geist", 600, 17) + 58
        s.add(f'<g class="float" style="animation-delay:-{d}s">'
              f'<rect x="{x}" y="{y}" width="{w}" height="44" rx="22" fill="#ffffff" fill-opacity="0.08" stroke="#ffffff" stroke-opacity="0.18"/>'
              + icon(ic, x + 16, y + 12, 20, CREAM))
        s.text(x + 44, y + 28, label, "G6", 17, CREAM)
        s.add('</g>')
        
    s.text(56, 61, "SUBHANKAR SAHOO", "M5", 15, CREAM, spacing=3)
    s.text(56, 82, "subhankarsahoo.qzz.io", "M5", 13, "#b9b3c9")
    s.add(f'<g><rect x="936" y="44" width="296" height="40" rx="20" fill="#000" fill-opacity="0.35" stroke="#ffffff" stroke-opacity="0.15"/>'
          f'<circle cx="960" cy="64" r="5" fill="#25d366"/><circle class="pulse" cx="960" cy="64" r="5" fill="#25d366"/></g>')
    s.text(976, 69, "Available for hackathons & roles", "G5", 15, CREAM)
    
    s.add('<g class="up" style="animation-delay:.1s">')
    s.text(56, 158, "ANDROID & AI/ML DEVELOPER", "M5", 15, GREEN, spacing=3)
    s.add('</g><g class="up" style="animation-delay:.25s">')
    
    # ---------------------------------------------------------
    # FIXED: Reduced font sizes for the name block from 104 to 80
    # ---------------------------------------------------------
    s.text(52, 262, "Subhankar", "G8", 80, CREAM, spacing=-3)
    mx = 52 + text_width("Subhankar ", "geist", 800, 80, -3)
    s.text(mx, 262, "Sahoo", "G8", 80, "url(#gName)", spacing=-3)
    s.add('</g>')
    
    prefix = "I build "
    s.text(56, 322, prefix, "G5", 32, "#d6d2e4")
    px = 56 + text_width(prefix, "geist", 500, 32)
    phrases = ["offline-first Android apps", "custom IoT hardware", "AI-powered tools", "clean Next.js interfaces"]
    period, slot = 16, 4
    for i, ph in enumerate(phrases):
        widths = [text_width(ph[:k], "geist", 600, 32) for k in range(len(ph) + 1)]
        n = len(ph)
        t_type, t_hold, t_del = 1.6, 3.0, 3.6
        vals, keys = [], []
        for k in range(n + 1):
            vals.append(widths[k]); keys.append(t_type * k / n)
        vals.append(widths[n]); keys.append(t_hold)
        for k in range(n, -1, -1):
            vals.append(widths[k]); keys.append(t_hold + (t_del - t_hold) * (n - k) / n)
        vals.append(0); keys.append(period)
        kt = ";".join(f"{k / period:.4f}" for k in keys)
        vv = ";".join(f"{v:.1f}" for v in vals)
        s.defs.append(f'<clipPath id="tw{i}"><rect x="{px}" y="290" height="44" width="0">'
                      f'<animate attributeName="width" values="{vv}" keyTimes="{kt}" calcMode="discrete" dur="{period}s" begin="{i * slot}s" repeatCount="indefinite"/></rect></clipPath>')
        s.add(f'<g clip-path="url(#tw{i})">')
        s.text(px, 322, ph, "G6", 32, GREEN)
        s.add('</g>')
        cx = ";".join(f"{px + v + 3:.1f}" for v in vals)
        s.add(f'<rect x="-20" y="296" width="3" height="34" fill="{GREEN}" opacity="0">'
              f'<animate attributeName="x" values="{cx}" keyTimes="{kt}" calcMode="discrete" dur="{period}s" begin="{i * slot}s" repeatCount="indefinite"/>'
              f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;{t_del / period:.4f};{t_del / period + 0.001:.4f};1" calcMode="discrete" dur="{period}s" begin="{i * slot}s" repeatCount="indefinite"/></rect>')
        
    for j, ln in enumerate(["B.Tech CSE (AI & ML) undergrad translating complex problems into",
                            "seamless mobile experiences and connected hardware ecosystems."]):
        s.text(56, 374 + j * 30, ln, "G4", 20, "#b9b3c9")
        
    stats = [("3+", "YEARS CODING"), ("10+", "PROJECTS BUILT"), ("2K+", "GITHUB COMMITS"), ("3", "HACKATHONS")]
    for k, (n, lab) in enumerate(stats):
        x = 56 + k * 168
        s.add(f'<g class="up" style="animation-delay:{.5 + k * .12:.2f}s">')
        s.add(f'<rect x="{x}" y="446" width="152" height="80" rx="16" fill="#ffffff" fill-opacity="0.06" stroke="#ffffff" stroke-opacity="0.12"/>')
        s.text(x + 18, 488, n, "X7", 34, CREAM)
        s.text(x + 18, 512, lab, "M5", 11, "#b9b3c9", spacing=1.5)
        s.add('</g>')
    s.add('</g>')
    s.add(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="28" fill="none" stroke="#ffffff" stroke-opacity="0.10"/>')
    return s

def section(t, num, label, title, note):
    W, H = 1280, 116
    s = Svg(W, H)
    s.defs.append(f'<linearGradient id="ln" x1="0" x2="1"><stop offset="0" stop-color="{GREEN}"/><stop offset="0.35" stop-color="{GREEN}" stop-opacity="0.25"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></linearGradient>')
    s.text(4, 34, f"{num} / {label}", "M5", 15, GREEN, spacing=3)
    s.text(0, 86, title, "G8", 44, t["text"], spacing=-1)
    s.text(W - 4, 86, note, "G4", 18, t["muted"], anchor="end")
    s.add(f'<rect x="0" y="108" width="{W}" height="2" fill="url(#ln)"/>')
    return s

def card_frame(s, t, w, h, r=24):
    s.defs.append(f'<clipPath id="cf"><rect width="{w}" height="{h}" rx="{r}"/></clipPath>')
    s.add(f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="{r}" fill="{t["card"]}" stroke="{t["line"]}"/>')

def chip_row(s, t, x, y, items, size=13):
    for it in items:
        w = text_width(it, "mono", 500, size) + 22
        s.add(f'<rect x="{x}" y="{y}" width="{w}" height="28" rx="14" fill="{t["chip"]}"/>')
        s.text(x + 11, y + 19, it, "M5", size, t["chiptext"])
        x += w + 8
    return x

def product_card(t, name, img, tagline, chips, url_label, accent):
    W, H = 412, 560
    s = Svg(W, H)
    card_frame(s, t, W, H)
    uri, _ = img_uri(img, 618, 464)
    s.add(f'<g clip-path="url(#cf)"><image href="{uri}" x="0" y="0" width="{W}" height="309" preserveAspectRatio="xMidYMid slice"/></g>')
    s.add(f'<rect x="0" y="309" width="{W}" height="1" fill="{t["line"]}"/>')
    s.add(f'<rect x="28" y="336" width="8" height="30" rx="4" fill="{accent}"/>')
    s.text(48, 362, name, "X7", 32, t["text"], spacing=1)
    for j, ln in enumerate(wrap(tagline, "geist", 400, 17, W - 56)[:3]):
        s.text(28, 398 + j * 25, ln, "G4", 17, t["muted"])
    chip_row(s, t, 28, 470, chips)
    s.text(28, 532, url_label, "G6", 17, GREEN)
    s.add(f'<path d="M{W - 50} 520 l12 0 m0 0 l0 12 m0 -12 l-14 14" stroke="{GREEN}" stroke-width="2.4" fill="none" stroke-linecap="round"/>')
    return s

def work_card(t, title, kind, img):
    W, H = 412, 336
    s = Svg(W, H)
    card_frame(s, t, W, H, 22)
    uri, _ = img_uri(img, 618, 400, crop=None)
    s.add(f'<g clip-path="url(#cf)"><image href="{uri}" x="0" y="0" width="{W}" height="266" preserveAspectRatio="xMidYMin slice"/></g>')
    s.add(f'<rect x="0" y="266" width="{W}" height="1" fill="{t["line"]}"/>')
    s.text(24, 306, title, "G6", 20, t["text"])
    s.text(W - 24, 306, kind, "M5", 12, t["muted"], anchor="end", spacing=1)
    return s

def pill(t, label, ic):
    w = int(text_width(label, "geist", 600, 16) + 66)
    s = Svg(w, 46)
    s.add(f'<rect x="0.5" y="0.5" width="{w - 1}" height="45" rx="23" fill="{t["card"]}" stroke="{t["line"]}"/>')
    if ic == "globe":
        s.add(raw_icon(GLOBE, 18, 13, 20, GREEN))
    else:
        s.add(icon(ic, 18, 13, 20, GREEN))
    s.text(46, 29, label, "G6", 16, t["text"])
    return s

def now_strip(t):
    W, H = 1280, 76
    s = Svg(W, H)
    s.css.append('.pulse{animation:pulse 2s ease-out infinite;transform-origin:center;transform-box:fill-box}'
                 '@keyframes pulse{0%{opacity:.8;transform:scale(1)}100%{opacity:0;transform:scale(2.6)}}')
    s.add(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="38" fill="{t["card"]}" stroke="{t["line"]}"/>')
    s.add(f'<rect x="14" y="14" width="96" height="48" rx="24" fill="{GREEN}"/>')
    s.text(62, 44, "NOW", "M5", 16, "#ffffff", anchor="middle", spacing=3)
    s.add(f'<circle cx="140" cy="38" r="5" fill="#25d366"/><circle class="pulse" cx="140" cy="38" r="5" fill="#25d366"/>')
    msg = "Shipping LOFO and designing a standalone ESP32 home emergency system."
    s.text(160, 44, msg, "G5", 18, t["text"])
    return s

def stack(t):
    W, H = 1280, 150
    names = [("kotlin", "Kotlin"), ("android", "Android"), ("python", "Python"), ("nextdotjs", "Next.js"),
             ("arduino", "Arduino"), ("docker", "Docker"), ("git", "Git"), ("github", "GitHub"), ("firebase", "Firebase")]
    step = 132
    span = step * len(names)
    s = Svg(W, H)
    s.defs.append(f'<clipPath id="sc"><rect width="{W}" height="{H}" rx="24"/></clipPath>'
                  f'<linearGradient id="edge" x1="0" x2="1"><stop offset="0" stop-color="{t["card"]}"/><stop offset="0.07" stop-color="{t["card"]}" stop-opacity="0"/>'
                  f'<stop offset="0.93" stop-color="{t["card"]}" stop-opacity="0"/><stop offset="1" stop-color="{t["card"]}"/></linearGradient>')
    s.css.append(f'.mq{{animation:mq 30s linear infinite}}@keyframes mq{{from{{transform:translateX(0)}}to{{transform:translateX(-{span}px)}}}}')
    s.add(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="24" fill="{t["card"]}" stroke="{t["line"]}"/>')
    s.add('<g clip-path="url(#sc)"><g class="mq">')
    for rep in range(3):
        for k, (ic, lab) in enumerate(names):
            x = 30 + rep * span + k * step
            s.add(f'<rect x="{x}" y="26" width="64" height="64" rx="18" fill="{t["tile"]}" stroke="{t["line"]}"/>')
            s.add(icon(ic, x + 18, 44, 28, t["text"]))
            s.text(x + 32, 120, lab, "M5", 13, t["muted"], anchor="middle")
    s.add('</g></g>')
    s.add(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="24" fill="url(#edge)"/>')
    return s

def cta():
    W, H = 1280, 300
    s = Svg(W, H)
    s.defs.append(f'''<clipPath id="cc"><rect width="{W}" height="{H}" rx="28"/></clipPath>
<radialGradient id="ca" cx="0.15" cy="0" r="0.8"><stop offset="0" stop-color="#3b22b8" stop-opacity="0.9"/><stop offset="1" stop-color="{INK}" stop-opacity="0"/></radialGradient>
<radialGradient id="cb" cx="0.85" cy="1.1" r="0.7"><stop offset="0" stop-color="{GREEN}" stop-opacity="0.8"/><stop offset="1" stop-color="{INK}" stop-opacity="0"/></radialGradient>
<pattern id="cg" width="48" height="48" patternUnits="userSpaceOnUse"><path d="M48 0H0V48" fill="none" stroke="#fff" stroke-opacity="0.045"/></pattern>
<linearGradient id="cn" x1="0" x2="1"><stop offset="0" stop-color="{GREEN}"/><stop offset="0.55" stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>''')
    s.css.append('.sh{animation:sh 3.2s ease-in-out infinite}@keyframes sh{0%,100%{transform:translateX(0)}50%{transform:translateX(6px)}}')
    s.add(f'<g clip-path="url(#cc)"><rect width="{W}" height="{H}" fill="{INK}"/><rect width="{W}" height="{H}" fill="url(#cg)"/>'
          f'<rect width="{W}" height="{H}" fill="url(#ca)"/><rect width="{W}" height="{H}" fill="url(#cb)"/></g>')
    s.text(64, 92, "HAVE A PROJECT IN MIND?", "M5", 16, GREEN, spacing=3)
    s.text(60, 168, "Let's build it", "G8", 72, CREAM, spacing=-2)
    s.text(60 + text_width("Let's build it ", "geist", 800, 72, -2), 168, "together.", "G8", 72, "url(#cn)", spacing=-2)
    s.text(64, 222, "Open to collaborations, open-source work, and hackathon teams.", "G4", 20, "#c9c3d8")
    bx, by = 960, 196
    s.add(f'<g class="sh"><rect x="{bx}" y="{by}" width="256" height="60" rx="30" fill="{GREEN}"/>')
    s.text(bx + 34, by + 38, "Let's talk", "G6", 21, "#ffffff")
    s.add(f'<path d="M{bx + 206} {by + 24} l12 0 m0 0 l0 12 m0 -12 l-14 14" stroke="#fff" stroke-width="2.6" fill="none" stroke-linecap="round"/></g>')
    s.text(1216, 92, "subhankarsahoo.qzz.io", "M5", 15, "#c9c3d8", anchor="end")
    s.add(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="28" fill="none" stroke="#fff" stroke-opacity="0.1"/>')
    return s

SOFTWARE = [
    ("attendo", "AttenDO (v2.4)", "attendo-cover",
     "Attendance ecosystem with a Kotlin wrapper, Gemini RAG chatbot, Firebase Auth, and OTA updates.",
     ["Kotlin", "Firebase", "Gemini AI"], "GitHub", "#3b82f6"),
    ("fileease", "FileEase", "fileease-cover",
     "Offline Android file manager using Jetpack Compose, featuring optimistic UI and async coroutines.",
     ["Jetpack Compose", "Coroutines"], "GitHub", "#4ade80"),
    ("lofo", "LOFO", "lofo-cover",
     "Android app for managing lost and found item reports using Kotlin, Supabase, and Cloudflare R2.",
     ["Kotlin", "Supabase", "Cloudflare R2"], "GitHub", PINK),
]

HARDWARE = [
    ("sih26", "RELOCATION DSS AI", "SIH 2026", "sih26-cover"),
    ("esp32", "ESP32 Panic Button", "IOT SYSTEM", "esp32-cover"),
    ("bot", "Train Status Bot", "TELEGRAM BOT", "bot-cover"),
]

PILLS = [("site", "Portfolio", "globe"), ("linkedin", "LinkedIn", "linkedin"),
         ("github", "GitHub", "github"), ("instagram", "Instagram", "instagram")]

def main():
    sizes = {}
    sizes["hero.svg"] = save(hero(), "hero.svg")
    sizes["cta.svg"] = save(cta(), "cta.svg")
    for name, t in THEMES.items():
        sizes[f"{name}/now"] = save(now_strip(t), name, "now.svg")
        for key, label, title, note in [("01", "SOFTWARE", "Software & Apps", "Offline-first Android & AI"),
                                        ("02", "HARDWARE", "Hardware & Scripts", "IoT, ESP32 & Python Automation"),
                                        ("03", "STACK", "Tools I ship with", "Android, Web & Hardware"),
                                        ("04", "ACTIVITY", "Building in public", "Updated daily via Actions")]:
            sizes[f"{name}/s{key}"] = save(section(t, key, label, title, note), name, f"s{key}.svg")
        for slug, nm, img, tag, chips, url, acc in SOFTWARE:
            sizes[f"{name}/p-{slug}"] = save(product_card(t, nm, img, tag, chips, url, acc), name, f"p-{slug}.svg")
        for slug, title, kind, img in HARDWARE:
            sizes[f"{name}/w-{slug}"] = save(work_card(t, title, kind, img), name, f"w-{slug}.svg")
        for slug, label, ic in PILLS:
            sizes[f"{name}/l-{slug}"] = save(pill(t, label, ic), name, f"l-{slug}.svg")
        sizes[f"{name}/stack"] = save(stack(t), name, "stack.svg")
    total = sum(sizes.values())
    print(f"\n{len(sizes)} files generated ({total / 1e6:.2f} MB total).")

if __name__ == "__main__":
    main()