"""Picture explainers for the lab pages (standard library only).

Every function returns an SVG string. Colours come from the site's CSS tokens
(var(--surface), var(--ink), var(--o), ...), so the pictures follow light and
dark mode. The standalone files (public/labs/<slug>/explainer.svg) carry their
own <style> with the token values read from build/assets/site.css.

Text is wrapped by hand (SVG has no text flow). Widths are estimated with a
conservative average glyph width; a panel that cannot fit its text at the
smallest allowed size stops the build, so nothing is ever clipped silently.
"""
import html
import re

# 24x24 line icons (stroke only, drawn with currentColor-style classes).
ICONS = {
    "write": "M4 20l4-1 11-11-3-3L5 16z M14 7l3 3",
    "run": "M8 5l11 7-11 7z",
    "count": "M5 5v14 M10 5v14 M15 5v14 M3 17L21 7",
    "compare": "M4 8h13 M14 5l3 3-3 3 M20 16H7 M10 13l-3 3 3 3",
    "hash": "M9 4L7 20 M17 4l-2 16 M4 9h17 M3 15h17",
    "search": "M10 4a6 6 0 1 0 0 12a6 6 0 0 0 0-12z M14.5 14.5L20 20",
    "chip": "M7 7h10v10H7z M10 3v4 M14 3v4 M10 17v4 M14 17v4 M3 10h4 M3 14h4 M17 10h4 M17 14h4",
    "flip": "M8 20V5 M4 9l4-4 4 4 M16 4v15 M12 15l4 4 4-4",
    "doc": "M6 3h8l4 4v14H6z M14 3v4h4 M9 12h6 M9 16h6",
    "check": "M4 12l5 5L20 6",
    "wrench": "M14.5 4a4.5 4.5 0 0 0-4 6.3L4 16.8 7.2 20l6.5-6.5A4.5 4.5 0 0 0 20 9.5l-3 3-3-1-1-3 3-3z",
    "clock": "M12 4a8 8 0 1 0 0 16a8 8 0 0 0 0-16z M12 8v4l3 2",
    "chart": "M5 20V10 M12 20V4 M19 20v-7 M3 20h18",
    "loop": "M4 12a8 8 0 0 1 14-5 M18 3v4h-4 M20 12a8 8 0 0 1-14 5 M6 21v-4h4",
    "blocks": "M4 4h7v7H4z M13 4h7v7h-7z M4 13h7v7H4z M13 13h7v7h-7z",
    "warn": "M12 4l9 16H3z M12 10v4 M12 17v.5",
    "flag": "M6 21V4 M6 4h12l-3 4 3 4H6",
    "lock": "M6 11h12v9H6z M8 11V8a4 4 0 0 1 8 0v3",
    "list": "M9 6h11 M9 12h11 M9 18h11 M4 6h.5 M4 12h.5 M4 18h.5",
}

# Outcome glyphs for the small cards (24x24, same stroke style).
GLYPH = {
    "positive": "M6 12.5l4 4 8-9",
    "mixed": "M12 5a7 7 0 1 0 0 14z",
    "negative": "M7 7l10 10 M17 7L7 17",
    "null": "M6 12h12",
    "held": "M9 6v12 M15 6v12",
}

SVG_RULES_START = "/* explainer:start */"
SVG_RULES_END = "/* explainer:end */"

CW = 0.57   # average glyph width as a fraction of font size (regular)
CWB = 0.62  # bold


def esc(s):
    return html.escape(str(s), quote=True)


def wrap(text, width, fs, bold=False):
    f = fs * (CWB if bold else CW)
    maxc = max(1, int(width / f))
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if len(t) <= maxc or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if any(len(l) > maxc + 2 for l in lines):  # an unbreakable word wider than the box
        raise ValueError(f"word too wide for box ({width}px at {fs}): {text[:60]!r}")
    return lines


def fit(text, width, max_h, sizes, lh=1.35, bold=False):
    for fs in sizes:
        lines = wrap(text, width, fs, bold)
        h = len(lines) * fs * lh
        if h <= max_h:
            return fs, lines, h
    raise ValueError(f"text does not fit {width}x{max_h}: {text[:70]!r}")


def tx(lines, x, y, fs, cls, lh=1.35, extra=""):
    out = [f'<text class="{cls}" x="{x}" y="{y:.1f}" font-size="{fs}"{extra}>']
    for i, l in enumerate(lines):
        out.append(f'<tspan x="{x}" dy="{0 if i == 0 else round(fs * lh, 1)}">{esc(l)}</tspan>')
    out.append("</text>")
    return "".join(out)


def icon(name, x, y, size=22):
    s = size / 24
    return (f'<g transform="translate({x} {y}) scale({s:.3f})"><path class="ex-ic" d="{ICONS[name]}"/></g>')


def chevron(x, y, down=False):
    d = f"M{x - 5} {y - 6}l5 6-5 6" if not down else f"M{x - 6} {y - 5}l6 5 6-5"
    return f'<path class="ex-chev" d="{d}"/>'


def _label(x, y, n, text):
    return f'<text class="ex-lab" x="{x}" y="{y}" font-size="12">{n} &#183; {esc(text)}</text>'


def _sizes(*a):
    return list(a)


def horizontal(lab, ex, outcome_label, meta):
    """1200 x 630 landscape picture. Raises ValueError if text cannot fit."""
    W, H = 1200, 630
    ml, gap = 24, 26
    widths = [240, 330, 284, 220]
    xs, x = [], ml
    for w in widths:
        xs.append(x)
        x += w + gap
    py = 120
    foot_y = H - 34
    if ex.get("analogy"):
        afs, al, ah = fit(ex["analogy"], W - 2 * ml - 36, 40, _sizes(14, 13.5, 13, 12.5, 12), lh=1.3)
        strip_h = max(34, ah + 18)
        strip_y = foot_y - strip_h
        ph = strip_y - 12 - py
    else:
        ph = foot_y - py
    pad = 14
    parts = []
    # header line
    parts.append(f'<text class="ex-code" x="{ml}" y="38" font-size="15">{esc(meta["code"])}<tspan class="ex-dot" dx="10">{esc(outcome_label.upper())}</tspan></text>')
    tfs, tl, _ = fit(meta["title"], W - 2 * ml, 62, _sizes(24, 22, 20, 18), lh=1.25, bold=True)
    parts.append(tx(tl, ml, 68, tfs, "ex-title", lh=1.25))
    # panels
    for i in range(4):
        cls = "ex-panel ex-panel-r" if i == 2 else "ex-panel"
        parts.append(f'<rect class="{cls}" x="{xs[i]}" y="{py}" width="{widths[i]}" height="{ph}" rx="12"/>')
        if i:
            parts.append(chevron(xs[i] - gap / 2 + 2, py + ph / 2))
    # 1 question + why
    iw = widths[0] - 2 * pad
    avail = ph - 46 - 22 - 30
    qfs, ql, qh = fit(ex["question"], iw, avail * 0.58, _sizes(19, 18, 17, 16, 15), lh=1.3, bold=True)
    wfs, wl, wh = fit(ex["why"], iw, avail - qh - 14, _sizes(14, 13, 12.5, 12), lh=1.35)
    parts.append(_label(xs[0] + pad, py + 28, 1, "THE QUESTION"))
    y = py + 52 + qfs * 0.8
    parts.append(tx(ql, xs[0] + pad, y, qfs, "ex-q", lh=1.3))
    y2 = y + qh + 12
    parts.append(f'<line class="ex-rule" x1="{xs[0] + pad}" x2="{xs[0] + widths[0] - pad}" y1="{y2 - 8:.1f}" y2="{y2 - 8:.1f}"/>')
    parts.append(f'<text class="ex-lab" x="{xs[0] + pad}" y="{y2 + 10:.1f}" font-size="11">WHY IT MATTERS</text>')
    parts.append(tx(wl, xs[0] + pad, y2 + 30, wfs, "ex-t", lh=1.35))
    # 2 steps
    parts.append(_label(xs[1] + pad, py + 28, 2, "HOW WE TESTED IT"))
    sw = widths[1] - 2 * 12
    n = len(ex["steps"])
    tw = sw - 74
    area = ph - 46 - 12
    for sfs in _sizes(14, 13.5, 13, 12.5, 12):
        blocks = [wrap(s, tw, sfs) for s in ex["steps"]]
        hs = [max(48, len(b) * sfs * 1.32 + 20) for b in blocks]
        if sum(hs) + 10 * (n - 1) <= area:
            break
    else:
        raise ValueError("steps do not fit: " + lab)
    sy = py + 46
    extra = (area - sum(hs) - 10 * (n - 1)) / max(1, n) if sum(hs) + 10 * (n - 1) < area else 0
    extra = min(extra, 18)
    for k, (b, h) in enumerate(zip(blocks, hs)):
        h = h + extra
        sx = xs[1] + 12
        parts.append(f'<rect class="ex-sub" x="{sx}" y="{sy:.1f}" width="{sw}" height="{h:.1f}" rx="9"/>')
        cy = sy + h / 2
        parts.append(f'<circle class="ex-num" cx="{sx + 20}" cy="{cy:.1f}" r="11"/>')
        parts.append(f'<text class="ex-numt" x="{sx + 20}" y="{cy + 4.5:.1f}" font-size="13" text-anchor="middle">{k + 1}</text>')
        parts.append(icon(ex["icons"][k], sx + 38, cy - 11, 22))
        th = len(b) * sfs * 1.32
        parts.append(tx(b, sx + 70, cy - th / 2 + sfs * 0.95, sfs, "ex-t", lh=1.32))
        sy += h + 10
    # 3 result
    rx = xs[2]
    parts.append(f'<rect class="ex-bar" x="{rx}" y="{py + 18}" width="4" height="{ph - 36}" rx="2"/>')
    parts.append(_label(rx + pad + 4, py + 28, 3, "WHAT WE FOUND"))
    iw = widths[2] - 2 * pad - 4
    pill = outcome_label
    pw = int(len(pill) * 7.6 + 36)
    parts.append(f'<rect class="ex-pill" x="{rx + pad + 4}" y="{py + 42}" width="{pw}" height="26" rx="13"/>')
    parts.append(f'<circle class="ex-pdot" cx="{rx + pad + 18}" cy="{py + 55}" r="5"/>')
    parts.append(f'<text class="ex-pilt" x="{rx + pad + 30}" y="{py + 59.5}" font-size="12.5">{esc(pill.upper())}</text>')
    hfs, hl, hh = fit(ex["headline"], iw, 100, _sizes(30, 28, 26, 24, 22, 20), lh=1.12, bold=True)
    hy = py + 84 + hfs * 0.85
    parts.append(tx(hl, rx + pad + 4, hy, hfs, "ex-head", lh=1.12))
    ry = hy + hh + 10
    rfs, rl, rh = fit(ex["result"], iw, py + ph - 14 - ry, _sizes(15, 14.5, 14, 13.5, 13, 12.5, 12), lh=1.36)
    parts.append(tx(rl, rx + pad + 4, ry + rfs * 0.85, rfs, "ex-t", lh=1.36))
    # 4 meaning
    mx = xs[3]
    parts.append(_label(mx + pad, py + 28, 4, "WHAT IT MEANS"))
    iw = widths[3] - 2 * pad
    mfs, ml_, mh = fit(ex["meaning"], iw, ph - 46 - 16, _sizes(16, 15, 14.5, 14, 13.5, 13, 12.5), lh=1.38)
    parts.append(tx(ml_, mx + pad, py + 52 + mfs * 0.8, mfs, "ex-t", lh=1.38))
    # analogy strip
    if ex.get("analogy"):
        parts.append(f'<rect class="ex-strip" x="{ml}" y="{strip_y}" width="{W - 2 * ml}" height="{strip_h:.1f}" rx="9"/>')
        parts.append(tx(al, ml + 18, strip_y + strip_h / 2 - ah / 2 + afs * 0.92, afs, "ex-t ex-em", lh=1.3))
    parts.append(f'<text class="ex-foot" x="{ml}" y="{H - 14}" font-size="12">aefinityai.com/labs/{esc(lab)}/</text>')
    parts.append(f'<text class="ex-foot" x="{W - ml}" y="{H - 14}" font-size="12" text-anchor="end">Run by us; no unaffiliated reproduction</text>')
    return W, H, "".join(parts)


def vertical(lab, ex, outcome_label, meta):
    """Portrait picture (440 wide) for phones. Height follows the text."""
    W = 440
    m = 16
    iw = W - 2 * m
    pad = 14
    parts = []
    y = 0
    parts.append(f'<text class="ex-code" x="{m}" y="30" font-size="14">{esc(meta["code"])}<tspan class="ex-dot" dx="9">{esc(outcome_label.upper())}</tspan></text>')
    tfs, tl, th = fit(meta["title"], iw, 140, _sizes(19, 18, 17, 16), lh=1.25, bold=True)
    parts.append(tx(tl, m, 58, tfs, "ex-title", lh=1.25))
    y = 58 + th + 6

    def panel_open(label_n, label_t, h):
        nonlocal y
        parts.append(f'<rect class="ex-panel" x="{m}" y="{y:.1f}" width="{iw}" height="{h:.1f}" rx="12"/>')
        parts.append(_label(m + pad, y + 26, label_n, label_t))
        top = y
        y += h
        return top

    def between():
        nonlocal y
        parts.append(chevron(W / 2, y + 12, down=True))
        y += 24

    # 1 question + why
    qfs, ql, qh = fit(ex["question"], iw - 2 * pad, 400, _sizes(18, 17, 16), lh=1.3, bold=True)
    wfs, wl, wh = fit(ex["why"], iw - 2 * pad, 400, _sizes(14.5, 14), lh=1.38)
    h = 42 + qh + 30 + wh + 16
    top = panel_open(1, "THE QUESTION", h)
    parts.append(tx(ql, m + pad, top + 52 + qfs * 0.4, qfs, "ex-q", lh=1.3))
    y2 = top + 42 + qh + 14
    parts.append(f'<line class="ex-rule" x1="{m + pad}" x2="{W - m - pad}" y1="{y2:.1f}" y2="{y2:.1f}"/>')
    parts.append(f'<text class="ex-lab" x="{m + pad}" y="{y2 + 18:.1f}" font-size="11">WHY IT MATTERS</text>')
    parts.append(tx(wl, m + pad, y2 + 38, wfs, "ex-t", lh=1.38))
    between()
    # 2 steps
    sfs = 14.5
    tw = iw - 2 * 10 - 72
    blocks = [wrap(s, tw, sfs) for s in ex["steps"]]
    hs = [max(52, len(b) * sfs * 1.35 + 22) for b in blocks]
    h = 42 + sum(hs) + 10 * (len(hs) - 1) + 14
    top = panel_open(2, "HOW WE TESTED IT", h)
    sy = top + 42
    for k, (b, hh) in enumerate(zip(blocks, hs)):
        sx = m + 10
        parts.append(f'<rect class="ex-sub" x="{sx}" y="{sy:.1f}" width="{iw - 20}" height="{hh:.1f}" rx="9"/>')
        cy = sy + hh / 2
        parts.append(f'<circle class="ex-num" cx="{sx + 20}" cy="{cy:.1f}" r="11"/>')
        parts.append(f'<text class="ex-numt" x="{sx + 20}" y="{cy + 4.5:.1f}" font-size="13" text-anchor="middle">{k + 1}</text>')
        parts.append(icon(ex["icons"][k], sx + 38, cy - 11, 22))
        t_h = len(b) * sfs * 1.35
        parts.append(tx(b, sx + 70, cy - t_h / 2 + sfs * 0.95, sfs, "ex-t", lh=1.35))
        sy += hh + 10
    between()
    # 3 result
    iw2 = iw - 2 * pad - 4
    hfs, hl, hh = fit(ex["headline"], iw2, 120, _sizes(28, 26, 24, 22), lh=1.12, bold=True)
    rfs, rl, rh = fit(ex["result"], iw2, 500, _sizes(15, 14.5), lh=1.38)
    h = 46 + 26 + 14 + hh + 10 + rh + 16
    top = panel_open(3, "WHAT WE FOUND", h)
    parts.append(f'<rect class="ex-bar" x="{m}" y="{top + 16:.1f}" width="4" height="{h - 32:.1f}" rx="2"/>')
    pw = int(len(outcome_label) * 7.6 + 36)
    parts.append(f'<rect class="ex-pill" x="{m + pad + 4}" y="{top + 40:.1f}" width="{pw}" height="26" rx="13"/>')
    parts.append(f'<circle class="ex-pdot" cx="{m + pad + 18}" cy="{top + 53:.1f}" r="5"/>')
    parts.append(f'<text class="ex-pilt" x="{m + pad + 30}" y="{top + 57.5:.1f}" font-size="12.5">{esc(outcome_label.upper())}</text>')
    hy = top + 82 + hfs * 0.85
    parts.append(tx(hl, m + pad + 4, hy, hfs, "ex-head", lh=1.12))
    parts.append(tx(rl, m + pad + 4, hy + hh + 10 + rfs * 0.4, rfs, "ex-t", lh=1.38))
    between()
    # 4 meaning
    mfs, mlines, mh = fit(ex["meaning"], iw - 2 * pad, 500, _sizes(15.5, 15), lh=1.4)
    h = 42 + mh + 18
    top = panel_open(4, "WHAT IT MEANS", h)
    parts.append(tx(mlines, m + pad, top + 52 + mfs * 0.4, mfs, "ex-t", lh=1.4))
    y += 12
    if ex.get("analogy"):
        afs, al, ah = fit(ex["analogy"], iw - 28, 200, _sizes(14, 13.5), lh=1.35)
        hh_ = ah + 22
        parts.append(f'<rect class="ex-strip" x="{m}" y="{y:.1f}" width="{iw}" height="{hh_:.1f}" rx="9"/>')
        parts.append(tx(al, m + 14, y + 11 + afs * 0.92, afs, "ex-t ex-em", lh=1.35))
        y += hh_ + 12
    parts.append(f'<text class="ex-foot" x="{m}" y="{y + 14:.1f}" font-size="11.5">aefinityai.com/labs/{esc(lab)}/</text>')
    y += 34
    return W, int(y + 0.999), "".join(parts)


def mini(ex, outcome):
    """Small flow glyph for the index cards: question, step icons, verdict."""
    n = len(ex["icons"])
    parts = ['<circle class="ex-mq" cx="16" cy="24" r="12"/>',
             '<text class="ex-mqt" x="16" y="29" font-size="15" text-anchor="middle">?</text>']
    x0, x1 = 40, 190
    stride = (x1 - x0) / n
    for k, name in enumerate(ex["icons"]):
        cx = x0 + stride * k
        parts.append(f'<rect class="ex-msub" x="{cx + 2:.1f}" y="10" width="28" height="28" rx="7"/>')
        parts.append(icon(name, cx + 7, 15, 18))
    parts.append(f'<path class="ex-chev" d="M{x1 + 6} 18l5 6-5 6"/>')
    parts.append('<circle class="ex-mv" cx="218" cy="24" r="15"/>')
    parts.append(f'<g transform="translate(206 12)"><path class="ex-mg" d="{GLYPH[outcome]}"/></g>')
    return "".join(parts)


def css_rules(site_css):
    a = site_css.index(SVG_RULES_START) + len(SVG_RULES_START)
    b = site_css.index(SVG_RULES_END)
    return site_css[a:b].strip()


def tokens(site_css):
    """(light, dark) dicts of the --token values the pictures use."""
    want = ("surface", "bg", "bg-2", "ink", "ink-2", "muted", "line", "line-2", "accent", "accent-ink", "accent-soft",
            "o-positive", "o-mixed", "o-negative", "o-null", "o-held")
    def grab(block):
        return {k: v.strip() for k, v in re.findall(r"--([a-z0-9-]+):\s*([^;]+);", block) if k in want}
    light = grab(site_css[site_css.index(":root {"):site_css.index("@media (prefers-color-scheme: dark)")])
    i = site_css.index("@media (prefers-color-scheme: dark)")
    dark = grab(site_css[i:site_css.index("}", i)])
    return light, dark


def standalone(w, h, body, title, desc, outcome, site_css, mode="file"):
    """A complete .svg file. mode 'file' keeps var() + a dark media query;
    mode 'png' resolves every var() to the light value (for rasterising)."""
    light, dark = tokens(site_css)
    rules = css_rules(site_css)
    fam = '"Geist", ui-sans-serif, system-ui, -apple-system, "Segoe UI", "Helvetica Neue", Arial, sans-serif'
    mono = '"Geist Mono", ui-monospace, Menlo, Consolas, monospace'
    root = "".join(f"--{k}:{v};" for k, v in light.items()) + f"--o:var(--o-{outcome});--sans:{fam};--mono:{mono};"
    style = f".ex{{{root}}}\n"
    if mode == "file":
        dk = "".join(f"--{k}:{v};" for k, v in dark.items())
        style += f"@media (prefers-color-scheme: dark){{.ex{{{dk}}}}}\n"
    style += rules
    if mode == "png":
        def sub(m):
            return light.get(m.group(1), m.group(0))
        style = re.sub(r"var\(--o\)", light[f"o-{outcome}"], style)
        style = re.sub(r"var\(--(?!sans|mono)([a-z0-9-]+)\)", sub, style)
        style = style.replace("var(--sans)", fam).replace("var(--mono)", mono)
        style = style.replace(f"--o:{light['o-' + outcome]};", "")
        style = re.sub(r"--[a-z0-9-]+:[^;]+;", "", style)
    bg = f'<rect class="ex-bg" width="{w}" height="{h}"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" class="ex" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{esc(title)}">'
            f'<title>{esc(title)}</title><desc>{esc(desc)}</desc><style>{style}</style>{bg}{body}</svg>\n')


def inline(w, h, body, title, desc, cls, outcome):
    return (f'<svg class="{cls} o-{outcome}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}" focusable="false">'
            f'<title>{esc(title)}</title><desc>{esc(desc)}</desc>{body}</svg>')
