"""Builds the Restore Remake Studio branding HTML files. Render each one as a screenshot."""

FONTS = """
@font-face{font-family:Anton;src:url(fonts/Anton-Regular.ttf)}
@font-face{font-family:Mont;src:url(fonts/Montserrat.ttf);font-weight:100 900}
"""

# Shared SVG defs: rust texture, metal, clean side, glow.
DEFS = """
<filter id="rust" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.045" numOctaves="5" seed="7"/>
  <feColorMatrix values="1.3 0 0 0 0.05  0.55 0 0 0 0.0  0.12 0 0 0 0.0  0 0 0 0 1"/>
</filter>
<filter id="rustbig" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.009" numOctaves="6" seed="11"/>
  <feColorMatrix values="1.35 0 0 0 0.02  0.55 0 0 0 -0.02  0.12 0 0 0 0  0 0 0 0 1"/>
</filter>
<filter id="rustdark" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="5" seed="3"/>
  <feColorMatrix values="0.95 0 0 0 -0.05  0.38 0 0 0 -0.03  0.1 0 0 0 0  0 0 0 0 1"/>
</filter>
<linearGradient id="metal" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#94A3B8"/><stop offset="0.35" stop-color="#F8FAFC"/>
  <stop offset="0.55" stop-color="#CBD5E1"/><stop offset="1" stop-color="#64748B"/>
</linearGradient>
<radialGradient id="clean" cx="0.75" cy="0.75" r="0.9">
  <stop offset="0" stop-color="#22D3EE"/><stop offset="0.45" stop-color="#0E7490"/><stop offset="1" stop-color="#082F49"/>
</radialGradient>
<linearGradient id="gold" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#FDE68A"/><stop offset="0.5" stop-color="#F59E0B"/><stop offset="1" stop-color="#B45309"/>
</linearGradient>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
  <feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
  <feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="#000" flood-opacity="0.6"/>
</filter>
"""

SPARK = '<path d="M0,-1 L0.22,-0.22 L1,0 L0.22,0.22 L0,1 L-0.22,0.22 L-1,0 L-0.22,-0.22Z" fill="#fff"/>'

def sparkle(x, y, s):
    return f'<g transform="translate({x},{y}) scale({s})" filter="url(#glow)">{SPARK}</g>'

def emblem(p):
    """400x400 emblem: a wrench half rusty, half restored, over a split circle. p = unique id prefix."""
    wrench = """
      <circle cx="200" cy="112" r="64"/>
      <rect x="180" y="150" width="40" height="190" rx="20"/>
      <circle cx="200" cy="330" r="34"/>"""
    holes = """
      <rect x="180" y="30" width="40" height="88" rx="6"/>
      <circle cx="200" cy="330" r="13"/>"""
    return f"""
<defs>
  <clipPath id="{p}c"><circle cx="200" cy="200" r="186"/></clipPath>
  <clipPath id="{p}tl"><polygon points="0,0 400,0 0,400"/></clipPath>
  <clipPath id="{p}br"><polygon points="400,0 400,400 0,400"/></clipPath>
  <mask id="{p}w" maskUnits="userSpaceOnUse" x="0" y="0" width="400" height="400">
    <g fill="#fff" transform="rotate(-45 200 200)">{wrench}</g>
    <g fill="#000" transform="rotate(-45 200 200)">{holes}</g>
  </mask>
</defs>
<g filter="url(#shadow)">
<circle cx="200" cy="200" r="198" fill="url(#gold)"/>
<g clip-path="url(#{p}c)">
  <rect width="400" height="400" fill="url(#clean)"/>
  <g clip-path="url(#{p}tl)"><rect width="400" height="400" filter="url(#rustdark)"/>
    <rect width="400" height="400" fill="#000" opacity="0.25"/></g>
  <line x1="-10" y1="410" x2="410" y2="-10" stroke="#FDE68A" stroke-width="7" filter="url(#glow)"/>
  <g mask="url(#{p}w)" filter="url(#shadow)">
    <rect width="400" height="400" fill="url(#metal)" transform="rotate(-45 200 200)"/>
    <g clip-path="url(#{p}tl)"><rect width="400" height="400" filter="url(#rust)"/></g>
  </g>
  {sparkle(315, 175, 20)}{sparkle(215, 345, 13)}{sparkle(360, 265, 9)}
</g>
<circle cx="200" cy="200" r="186" fill="none" stroke="#1C1917" stroke-width="5"/>
</g>"""

def page(w, h, body, extra_css="", bg="#111"):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{FONTS}
html,body{{margin:0;width:{w}px;height:{h}px;overflow:hidden;background:{bg}}}{extra_css}</style></head>
<body>{body}</body></html>"""

def svg(w, h, inner, vb=None, style=""):
    vb = vb or f"0 0 {w} {h}"
    return f'<svg width="{w}" height="{h}" viewBox="{vb}" style="{style}" xmlns="http://www.w3.org/2000/svg"><defs>{DEFS}</defs>{inner}</svg>'

# ---- Logo (800x800) ----
logo_bg = '<rect width="800" height="800" fill="#0C0A09"/><circle cx="400" cy="400" r="400" fill="#1C1917"/>'
open("logo.html", "w").write(page(800, 800, svg(800, 800,
    logo_bg + f'<g transform="translate(8,8) scale(1.96)">{emblem("l")}</g>'), bg="#0C0A09"))

# ---- Watermark (300x300, transparent) ----
open("watermark.html", "w").write(page(300, 300, svg(300, 300,
    f'<g transform="translate(6,6) scale(0.72)">{emblem("w")}</g>'), bg="transparent"))

# ---- Split background: rusty "before" left, clean "after" right ----
def split_bg(w, h, x_top, x_bot, p):
    sparks = "".join(sparkle(x_bot + (w - x_bot) * fx, h * fy, s)
                     for fx, fy, s in [(.25, .3, 18), (.6, .22, 26), (.82, .62, 20), (.45, .78, 14), (.9, .3, 12), (.35, .55, 9)])
    return f"""
<defs><radialGradient id="{p}clean" cx="0.85" cy="0.5" r="0.8">
  <stop offset="0" stop-color="#22D3EE"/><stop offset="0.4" stop-color="#0E7490"/><stop offset="1" stop-color="#042F3E"/></radialGradient>
  <radialGradient id="{p}vig" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#000" stop-opacity="0.6"/>
  <stop offset="0.6" stop-color="#000" stop-opacity="0.35"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
  <clipPath id="{p}L"><polygon points="0,0 {x_top},0 {x_bot},{h} 0,{h}"/></clipPath></defs>
<rect width="{w}" height="{h}" fill="url(#{p}clean)"/>
<g clip-path="url(#{p}L)"><rect width="{w}" height="{h}" filter="url(#rustbig)"/>
  <rect width="{w}" height="{h}" fill="#1C0A00" opacity="0.45"/></g>
<line x1="{x_top}" y1="-20" x2="{x_bot}" y2="{h+20}" stroke="#FDE68A" stroke-width="10" filter="url(#glow)"/>
{sparks}
<ellipse cx="{w/2}" cy="{h/2}" rx="{w*0.42}" ry="{h*0.32}" fill="url(#{p}vig)"/>"""

CSS = """
.wrap{position:absolute;display:flex;align-items:center;justify-content:center}
.title{font-family:Anton;line-height:.92;letter-spacing:2px;background:linear-gradient(#FFF7D6,#FBBF24 55%,#D97706);
  -webkit-background-clip:text;color:transparent;filter:drop-shadow(0 6px 0 #451A03) drop-shadow(0 14px 18px rgba(0,0,0,.7))}
.studio{font-family:Mont;font-weight:800;color:#fff;letter-spacing:.42em;text-shadow:0 4px 12px rgba(0,0,0,.8)}
.pill{display:inline-block;font-family:Mont;font-weight:800;color:#1C1917;background:linear-gradient(#FDE68A,#F59E0B);
  border-radius:999px;box-shadow:0 6px 18px rgba(0,0,0,.5)}
.tag{position:absolute;font-family:Anton;color:#fff;letter-spacing:6px;padding:6px 26px;border:5px solid #fff;
  text-shadow:0 3px 8px rgba(0,0,0,.6);box-shadow:0 0 20px rgba(0,0,0,.4)}
"""

# ---- YouTube banner (2560x1440, safe area 1546x423 in the middle) ----
banner = f"""
<div style="position:absolute;inset:0">{svg(2560, 1440, split_bg(2560, 1440, 1420, 1140, "b"))}</div>
<div class="tag" style="left:150px;top:690px;font-size:56px;transform:rotate(-6deg);background:rgba(120,40,0,.55)">BEFORE</div>
<div class="tag" style="right:150px;top:690px;font-size:56px;transform:rotate(6deg);background:rgba(8,90,110,.55)">AFTER</div>
<div class="wrap" style="left:507px;top:509px;width:1546px;height:423px;gap:56px">
  {svg(390, 390, emblem("b"), vb="0 0 400 400")}
  <div><div class="title" style="font-size:168px">RESTORE REMAKE</div>
  <div class="studio" style="font-size:58px;margin:10px 0 22px 6px">STUDIO</div>
  <div class="pill" style="font-size:34px;padding:12px 34px">🔧 NEW RESTORATION EVERY WEEK</div></div>
</div>"""
open("banner.html", "w").write(page(2560, 1440, banner, CSS))

# ---- Facebook cover (1640x624) ----
fb = f"""
<div style="position:absolute;inset:0">{svg(1640, 624, split_bg(1640, 624, 900, 760, "f"))}</div>
<div class="tag" style="left:70px;top:70px;font-size:38px;transform:rotate(-6deg);background:rgba(120,40,0,.55)">BEFORE</div>
<div class="tag" style="right:70px;top:70px;font-size:38px;transform:rotate(6deg);background:rgba(8,90,110,.55)">AFTER</div>
<div class="wrap" style="inset:0;gap:44px">
  {svg(300, 300, emblem("f"), vb="0 0 400 400")}
  <div><div class="title" style="font-size:126px">RESTORE REMAKE</div>
  <div class="studio" style="font-size:44px;margin:8px 0 18px 4px">STUDIO</div>
  <div class="pill" style="font-size:26px;padding:10px 28px">🔧 NEW RESTORATION EVERY WEEK</div></div>
</div>"""
open("fb_cover.html", "w").write(page(1640, 624, fb, CSS))
