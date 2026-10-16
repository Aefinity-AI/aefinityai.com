#!/usr/bin/env python3
"""Static site generator for aefinityai.com (v3).

Python 3 standard library only. Run from anywhere:  python3 build/build.py

Inputs (the sources of truth):
  content/labs.json   structured lab records (results, quotes, URLs, caveats)
  content/CONTENT.md  all narrative copy (parsed by anchors and field labels)
  build/pages/site_copy.py  layout copy derived from the two files above and
                            from the v2 pilot page
  build/assets/       site.css and site.js, copied to public/assets/

Output: every page under public/. Two runs give byte-identical output.
"""
import hashlib
import html
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
PUBLIC = ROOT / "public"
ASSETS_SRC = ROOT / "build" / "assets"
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "build" / "pages"))
sys.path.insert(0, str(ROOT / "build"))
import site_copy as C  # noqa: E402
import explainer as XP  # noqa: E402

KEEP = {"favicon.svg", "og.png", "robots.txt"}  # hand-made files in public/
HELD_BACK_FILES = ("oscost_ANALYSIS", "MECH11", "mech2_")
WRITTEN = []  # relative paths written this run


# --------------------------------------------------------------------------
# text helpers
# --------------------------------------------------------------------------
def esc(s):
    return html.escape(str(s), quote=True)


def norm(s):
    return re.sub(r"\s+", " ", s or "").strip()


def prose(s):
    """Rewrite machine nicknames and banned phrasings in prose (never quotes)."""
    for old, new in C.NICKNAME_PHRASES + C.PROSE_PHRASES:
        s = s.replace(old, new)
    m = re.search(C.NICKNAME_RE, s)
    if m:
        raise SystemExit(f"nickname left in prose: {m.group(0)!r} in {s[:160]!r}")
    return s


def short_url(u):
    m = re.match(r"https://github\.com/([^/]+)/([^/]+)/(?:blob|tree)/[^/]+/(.+)$", u)
    if m:
        return f"{m.group(2)} / {m.group(3).split('/')[-1]}"
    m = re.match(r"https://github\.com/([^/]+)/([^/]+)/commit/([0-9a-f]{7})", u)
    if m:
        return f"{m.group(2)} / commit {m.group(3)}"
    m = re.match(r"https://github\.com/([^/]+)/([^/]+)/?$", u)
    if m:
        return f"github.com/{m.group(1)}/{m.group(2)}"
    m = re.match(r"https://github\.com/([^/]+)/?$", u)
    if m:
        return f"github.com/{m.group(1)}"
    m = re.match(r"https://huggingface\.co/datasets/([^/]+)/([^/]+)(?:/blob/[^/]+/(.+))?$", u)
    if m:
        return f"Hugging Face / {m.group(2)}" + (f" / {m.group(3)}" if m.group(3) else "")
    return re.sub(r"^https?://", "", u).rstrip("/")


def link(href, text, cls=None):
    if href.startswith("#lab-"):
        href = f"/labs/{href[5:]}/"
    c = f' class="{cls}"' if cls else ""
    if href.startswith("http"):
        cl = f' class="ext{(" " + cls) if cls else ""}"'
        return f'<a{cl} href="{esc(href)}">{text}</a>'
    return f'<a{c} href="{esc(href)}">{text}</a>'


INLINE = re.compile(r"`([^`]+)`|\*\*(.+?)\*\*|\[([^\]]+)\]\(([^)\s]+)\)|(https?://[^\s)]+)")


def md(s, rewrite=True):
    """Tiny inline-markdown renderer: code, bold, links, bare URLs."""
    if rewrite:
        s = prose(s)
    out, pos = [], 0
    for m in INLINE.finditer(s):
        out.append(esc(s[pos:m.start()]))
        if m.group(1) is not None:
            out.append(f"<code>{esc(m.group(1))}</code>")
        elif m.group(2) is not None:
            out.append(f"<strong>{md(m.group(2), False)}</strong>")
        elif m.group(3) is not None:
            out.append(link(m.group(4), esc(m.group(3))))
        else:
            url = m.group(5)
            tail = ""
            while url and url[-1] in ".,;:":
                tail = url[-1] + tail
                url = url[:-1]
            out.append(link(url, esc(short_url(url))) + esc(tail))
        pos = m.end()
    out.append(esc(s[pos:]))
    return "".join(out)


# --------------------------------------------------------------------------
# parse CONTENT.md
# --------------------------------------------------------------------------
LAB_FIELDS = ["Question.", "Why it matters.", "Method, step by step.", "Method as recorded.",
              "Results (exact, sourced).", "What it does NOT show.", "Scope and caveats, as recorded.",
              "Outcome.", "What we learned.", "Check it yourself."]


def split_h2(text):
    parts = re.split(r"^## (.+)$", text, flags=re.M)
    return {parts[i].strip(): parts[i + 1] for i in range(1, len(parts), 2)}


def lab_fields(sec):
    idx = []
    for f in LAB_FIELDS:
        m = re.search(r"^\*\*" + re.escape(f) + r"\*\*", sec, re.M)
        if not m:
            raise SystemExit(f"field {f} missing")
        idx.append((m.start(), m.end(), f))
    idx.sort()
    out = {}
    for i, (s, e, f) in enumerate(idx):
        end = idx[i + 1][0] if i + 1 < len(idx) else len(sec)
        out[f] = sec[e:end].strip()
    return out


def blocks(text):
    """Split markdown into blocks: ('code', str) | ('list', [items]) | ('ol', [..]) | ('p', str)."""
    out, lines, i = [], text.strip().split("\n"), 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            j = i + 1
            buf = []
            while not lines[j].startswith("```"):
                buf.append(lines[j])
                j += 1
            out.append(("code", "\n".join(buf)))
            i = j + 1
        elif ln.startswith("- "):
            items = []
            while i < len(lines) and (lines[i].startswith("- ") or lines[i].startswith("  ")):
                if lines[i].startswith("- "):
                    items.append(lines[i][2:])
                else:
                    items[-1] += "\n" + lines[i]
                i += 1
            out.append(("list", items))
        elif re.match(r"^\d+\. ", ln):
            items = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                items.append(re.sub(r"^\d+\. ", "", lines[i]))
                i += 1
            out.append(("ol", items))
        elif ln.strip() == "":
            i += 1
        else:
            buf = [ln]
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].startswith(("- ", "```")):
                buf.append(lines[i])
                i += 1
            out.append(("p", " ".join(buf)))
    return out


def parse_content():
    text = (CONTENT / "CONTENT.md").read_text()
    h2 = split_h2(text)
    data = {}
    m = re.search(r"\n\n(We are not another.*?)\n\n\*\*Aspiration\.\*\* (.*?) (This is an aspiration, not a claim\.)", h2["Mission"], re.S)
    data["mission"], data["aspiration"], data["aspiration_note"] = m.group(1).strip(), m.group(2).strip(), m.group(3)
    data["how_to_read"] = [b for b in blocks(h2["How to read this site"]) if b[0] == "list"][0][1]

    qs = []
    hq = h2["The hard questions"]
    for qm in re.finditer(r"^### (\d+)\. (.+?)\n(.*?)(?=^### |\Z)", hq, re.M | re.S):
        body = qm.group(3)
        labs = re.findall(r"\(#lab-([a-z0-9-]+)\)", body.split("\n\n")[0] if body.strip().startswith("Labs:") else body)
        found = re.search(r"\*\*What we found so far\.\*\* (.*?)(?:\n\n|\Z)", body, re.S).group(1).strip()
        still = re.search(r"\*\*Still open\.\*\* (.*?)(?:\n\n|\Z)", body, re.S).group(1).strip()
        labline = re.search(r"^Labs: (.*)$", body, re.M).group(1)
        qs.append({"n": int(qm.group(1)), "q": qm.group(2).strip(),
                   "labs": re.findall(r"\(#lab-([a-z0-9-]+)\)", labline),
                   "found": found, "still": still})
        del labs
    data["questions"] = qs

    oq = blocks(h2["Open questions we have not tested yet"])
    data["open_intro"] = oq[0][1]
    data["open"] = [re.match(r"\*\*(.+?)\*\* (.+)", it, re.S).groups() for it in oq[1][1]]

    # labs
    labs_text = text[text.index('<a id="lab-'):text.index("\n## Our test standard")]
    parts = re.split(r'<a id="lab-([a-z0-9-]+)"></a>', labs_text)
    labs = {}
    for i in range(1, len(parts), 2):
        slug, sec = parts[i], parts[i + 1]
        title = re.search(r"^### (.+)$", sec, re.M).group(1).strip()
        meta = re.search(r"^\*Date: (.*?) \| Outcome: (.*?) \| (Run by us; no unaffiliated reproduction\.)\*$", sec, re.M)
        f = lab_fields(sec)
        steps = [b for b in blocks(f["Method, step by step."]) if b[0] == "ol"][0][1]
        res_blocks = blocks(f["Results (exact, sourced)."])
        res_claims = []
        res_note = None
        for b in res_blocks:
            if b[0] == "list":
                res_claims = [it.split("\n")[0] for it in b[1]]
            elif b[0] == "p":
                res_note = b[1]
        caveats = [b for b in blocks(f["Scope and caveats, as recorded."]) if b[0] == "list"][0][1]
        labs[slug] = {
            "title": title, "date_txt": meta.group(1), "outcome_txt": meta.group(2),
            "question": f["Question."], "why": f["Why it matters."], "steps": steps,
            "method": f["Method as recorded."], "claims": res_claims, "results_note": res_note,
            "not_show": f["What it does NOT show."], "caveats": caveats,
            "outcome_line": f["Outcome."], "learned": f["What we learned."],
            "check": blocks(f["Check it yourself."]),
        }
    data["labs"] = labs

    # standard
    st = h2["Our test standard"]
    data["std_intro"] = blocks(st)[0][1]
    def sub(label):
        s = st[st.index(f"**{label}**") + len(label) + 4:]
        return [b for b in blocks(s) if b[0] == "list"][0][1]
    data["std_practices"] = sub("The practices")
    data["std_quotes"] = [re.match(r'^"(.*)" \((https?://[^)]+)\)$', q).groups() for q in sub("In the repository's own words")]
    data["std_cannot"] = sub("What the standard cannot prove")
    data["std_details"] = re.search(r"^Details: (.*)$", st, re.M).group(1)

    # lessons
    le = h2["What we have learned"]
    data["lessons_intro"] = blocks(le)[0][1]
    lessons = []
    for lm in re.finditer(r"^(\d+)\. \*\*(.+?)\*\* (.*?) Labs: (.*)$", le, re.M):
        lessons.append({"n": int(lm.group(1)), "lead": lm.group(2), "body": lm.group(3),
                        "labs": re.findall(r"\(#lab-([a-z0-9-]+)\)", lm.group(4))})
    data["lessons"] = lessons

    # projects
    pr = h2["Projects"]
    projects = []
    for pm in re.finditer(r"^### (.+?)\n(.*?)(?=^### |\Z)", pr, re.M | re.S):
        projects.append({"name": pm.group(1).strip(), "blocks": blocks(pm.group(2))})
    data["projects"] = projects
    return data


# --------------------------------------------------------------------------
# load and cross-check
# --------------------------------------------------------------------------
def load():
    j = json.loads((CONTENT / "labs.json").read_text())
    data = parse_content()
    labs = sorted(j["labs"], key=lambda l: l["order"])
    assert len(labs) == 33, len(labs)
    olabels = {k: (lab, d) for k, lab, d in C.OUTCOMES}
    for l in labs:
        c = data["labs"][l["slug"]]
        assert norm(c["title"]) == norm(l["title"]), l["slug"]
        assert norm(c["method"]) == norm(l["method"]), ("method", l["slug"])
        assert [norm(x) for x in c["caveats"]] == [norm(x) for x in l["caveats"]], ("caveats", l["slug"])
        assert norm(c["learned"]) == norm(l["learned"]), ("learned", l["slug"])
        assert [norm(x) for x in c["claims"]] == [norm(r["claim"]) for r in l["results"]], ("claims", l["slug"])
        lab, d = olabels[l["outcome"]]
        assert c["outcome_txt"].startswith(lab), (l["slug"], c["outcome_txt"])
        if l["date"]:
            assert c["date_txt"] == l["date"], l["slug"]
        else:
            assert c["date_txt"] == "undated in the source", l["slug"]
        # held-back files never reach the site
        blob = json.dumps(l) + json.dumps(c)
        assert not any(h in blob for h in HELD_BACK_FILES), l["slug"]
        l["c"] = c
    # lab -> hard questions
    qmap = {}
    for q in data["questions"]:
        for s in q["labs"]:
            qmap.setdefault(s, []).append(q["n"])
    for i, l in enumerate(labs):
        l["no"] = i + 1
        l["code"] = f"L{i + 1:02d}"
        l["qs"] = qmap.get(l["slug"], [])
    return j, data, labs


def check_figures(labs):
    by = {l["slug"]: l for l in labs}
    for slug, fig in C.FIGURES.items():
        l = by[slug]
        hay = norm(" ".join([l["title"], l["c"]["question"]] + [r["claim"] + " " + r["quote"] for r in l["results"]] + l["caveats"]))
        for tok in fig["check"]:
            assert tok in hay, (slug, tok)


# --------------------------------------------------------------------------
# page shell
# --------------------------------------------------------------------------
def asset_ver(name):
    return hashlib.sha256((ASSETS_SRC / name).read_bytes()).hexdigest()[:10]


ICON_SUN = '<svg class="i-sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
ICON_MOON = '<svg class="i-moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>'
MARK = ('<svg class="mark" viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="8"/>'
        '<path d="M8.6 24.2 16 7.6l7.4 16.6M12.4 17.4h7.2M11 21h10"/></svg>')
ARROW = '<span class="arr" aria-hidden="true">&rarr;</span>'


def header(active):
    items = []
    for href, label in C.NAV:
        cur = ' aria-current="page"' if active == href else ""
        items.append(f'<li><a href="{href}"{cur}>{label}</a></li>')
    for href, label in C.NAV_MORE:  # mobile menu only; footer on desktop
        cur = ' aria-current="page"' if active == href else ""
        items.append(f'<li class="nav-more"><a href="{href}"{cur}>{label}</a></li>')
    pcur = ' aria-current="page"' if active == C.NAV_CTA[0] else ""
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap hdr">
    <a class="brand" href="/" aria-label="Aefinity AI, home">{MARK}<span class="wm">Aefinity <span>AI</span></span></a>
    <nav id="site-nav" class="nav" aria-label="Primary">
      <ul>{"".join(items)}</ul>
      <a class="nav-cta" href="{C.NAV_CTA[0]}"{pcur}>{C.NAV_CTA[1]}</a>
    </nav>
    <div class="hdr-tools">
      <button class="icon-btn theme-btn" type="button" data-theme-toggle aria-label="Switch colour theme">{ICON_SUN}{ICON_MOON}</button>
      <button class="icon-btn menu-btn" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Menu"><span></span><span></span></button>
    </div>
  </div>
</header>"""


def footer():
    nav = "".join(f'<li><a href="{h}">{t}</a></li>' for h, t in C.FOOT_NAV)
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="foot-grid">
      <div class="foot-about">
        <a class="brand" href="/" aria-label="Aefinity AI, home">{MARK}<span class="wm">Aefinity <span>AI</span></span></a>
        <p>We are not another AI platform or cloud service.</p>
        <p class="foot-prov">Every result on this site: run by us; no unaffiliated reproduction.</p>
      </div>
      <nav aria-label="Site"><h2>Site</h2><ul class="foot-nav">{nav}</ul></nav>
      <nav aria-label="Open materials"><h2>Open materials</h2><ul>
        <li><a class="ext" href="https://github.com/Aefinity-AI/cis2-spec">CIS-2 on GitHub</a></li>
        <li><a class="ext" href="https://huggingface.co/datasets/aefinityAIINC/cis2-conformance">Conformance dataset</a></li>
        <li><a class="ext" href="{C.PARTNER_PATH}">Design Partner Adoption Path</a></li>
        <li><a class="ext" href="{C.SITE_SOURCE}">Site source</a></li>
      </ul></nav>
      <div><h2>Contact</h2><ul>
        <li><a href="mailto:{C.EMAIL}">{C.EMAIL}</a></li>
        <li><a href="tel:{C.PHONE_TEL}">{C.PHONE_DISPLAY}</a></li>
        <li>{C.CITY}</li>
      </ul></div>
    </div>
    <div class="foot-bottom"><span>&copy; 2026 {C.COMPANY} &middot; {C.CITY}</span></div>
  </div>
</footer>"""


def page(path, title, desc, body, active=None, canonical=None, og_image=None):
    canon = C.SITE + (canonical if canonical is not None else path)
    full_title = title if title.startswith("Aefinity AI") else f"{title} · Aefinity AI"
    # Google Search Console ownership proof for the home page; never remove it.
    gsv = '<meta name="google-site-verification" content="utJ_SxVkTZLvmS1LT0q6WjuKvv7GzHwIRvjA3aaqshk">\n' if path == "/" else ""
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{gsv}<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{esc(canon)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Aefinity AI">
<meta property="og:title" content="{esc(full_title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(canon)}">
<meta property="og:image" content="{C.SITE}{og_image or '/og.png'}">
<meta name="twitter:card" content="summary_large_image">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&amp;family=Geist+Mono:wght@400;500&amp;family=Instrument+Serif:ital@0;1&amp;display=swap">
<link rel="stylesheet" href="/assets/site.css?v={asset_ver('site.css')}">
<script>(function(){{var d=document.documentElement;d.classList.add('js');try{{var t=localStorage.getItem('aefinity-theme');if(t==='light'||t==='dark')d.setAttribute('data-theme',t);}}catch(e){{}}}})();</script>
<script src="/assets/site.js?v={asset_ver('site.js')}" defer></script>
</head>
<body>
{header(active)}
<main id="main" tabindex="-1">
{body}
</main>
{footer()}
</body>
</html>
"""
    write(path, doc)


def write(path, doc):
    if path.endswith("/"):
        rel = path.lstrip("/") + "index.html"
    elif path.endswith((".html", ".xml", ".txt")):
        rel = path.lstrip("/")
    else:
        rel = path.lstrip("/") + ".html"
    out = PUBLIC / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc)
    WRITTEN.append(rel)


def write_file(rel, text):
    out = PUBLIC / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    WRITTEN.append(rel)


# --------------------------------------------------------------------------
# components
# --------------------------------------------------------------------------
OUT = {k: (lab, d) for k, lab, d in C.OUTCOMES}


def badge(outcome, big=False):
    lab = OUT[outcome][0]
    return f'<span class="badge o-{outcome}{" badge-lg" if big else ""}"><i aria-hidden="true"></i>{lab}</span>'


def date_txt(l):
    return l["date"] if l["date"] else "Undated in the source"


def time_el(l):
    if l["date"]:
        return f'<time datetime="{l["date"]}">{l["date"]}</time>'
    return '<span class="undated">Undated in the source</span>'


def finding(l):
    # The full "What we learned" text: a shortened version dropped qualifiers.
    return prose(l["learned"])


def lab_card(l, heading="h3", show_q=True):
    qs = " ".join(str(q) for q in l["qs"])
    qtxt = ""
    if show_q and l["qs"]:
        qtxt = '<p class="lc-q">' + " ".join(f'<span>Q{q}</span>' for q in l["qs"]) + "</p>"
    return f"""<li class="lab-card o-{l['outcome']}" data-outcome="{l['outcome']}" data-q="{qs}">
  <div class="lc-top"><span class="lc-no">{l['code']}</span>{time_el(l)}</div>
  {badge(l['outcome'])}
  <{heading} class="lc-title"><a href="/labs/{l['slug']}/">{esc(l['title'])}</a></{heading}>
  <p class="lc-find">{esc(finding(l))}</p>
  {qtxt}
</li>"""


def ledger(labs, compact=False, current=None):
    groups = []
    for k, lab, d in C.OUTCOMES:
        ls = [l for l in labs if l["outcome"] == k]
        if not ls:
            continue
        cells = "".join(
            f'<li><a class="cell{" is-cur" if current == l["slug"] else ""}" href="/labs/{l["slug"]}/" '
            f'aria-label="{l["code"]}, {lab}: {esc(l["title"])}" title="{l["code"]} · {esc(l["title"])}"></a></li>'
            for l in ls)
        groups.append(f'<div class="lg o-{k}" style="--n:{len(ls)}"><ol class="lg-cells">{cells}</ol>'
                      f'<p class="lg-lab"><b>{len(ls)}</b> {lab}</p></div>')
    return f'<div class="ledger{" ledger-compact" if compact else ""}">{"".join(groups)}</div>'


def code_block(cmd, ident):
    return f"""<div class="term">
  <div class="term-bar"><span>shell</span><button class="copy-btn" type="button" data-copy="{ident}">Copy</button></div>
  <pre tabindex="0"><span class="pr" aria-hidden="true">$ </span><code id="{ident}">{esc(cmd)}</code></pre>
</div>"""


def section_head(num, title, intro=None, hid=None, level="h2"):
    idattr = f' id="{hid}"' if hid else ""
    intro_html = f'<p class="sec-intro">{intro}</p>' if intro else ""
    n = f'<span class="sec-n">{num}</span>' if num else ""
    return f'<header class="sec-head">{n}<{level} class="sec-title"{idattr}>{title}</{level}>{intro_html}</header>'


def quote_is_mono(q):
    return bool(re.search(r"[|`=]|^\*\*|^#|\n|\{|->|→|Δ", q))


def quote_html(q):
    # Verbatim text; the source's own **bold** markup is rendered, not shown.
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", esc(q))


def evidence(r, i):
    q = r["quote"]
    mono = quote_is_mono(q)
    cls = "ev-mono" if mono else "ev-prose"
    if not mono and q.lstrip()[:1] in ('"', "\u201c"):
        cls += " ev-own-q"  # the quote carries its own quotation marks
    body = esc(q) if mono else quote_html(q)
    return f"""<li class="result">
  <p class="r-claim"><span class="r-n">R{i}</span>{md(r['claim'])}</p>
  <figure class="evidence {cls}">
    <blockquote cite="{esc(r['url'])}"><p>{body}</p></blockquote>
    <figcaption><span class="ev-lab">Verbatim source</span> {link(r['url'], esc(short_url(r['url'])))}</figcaption>
  </figure>
</li>"""


# --------------------------------------------------------------------------
# figures
# --------------------------------------------------------------------------
def figure(slug):
    f = C.FIGURES.get(slug)
    if not f:
        return ""
    rows = []
    if f["kind"] in ("bars", "ratio"):
        for row in f["rows"]:
            if f["kind"] == "bars":
                label, v, txt = row
                frac = v / f["max"]
            else:
                label, n, d = row
                frac, txt = n / d, f"{n} / {d}"
            w = round(frac * 100, 2)
            bar = (f'<rect x="0" y="0" width="{w}" height="10" rx="1.5" class="bar"/>' if w > 0
                   else '<rect x="0" y="0" width="0.6" height="10" class="bar-zero"/>')
            rows.append(f'<div class="fr"><span class="fr-l">{esc(label)}</span>'
                        f'<svg class="fr-svg" viewBox="0 0 100 10" preserveAspectRatio="none" aria-hidden="true">'
                        f'<rect x="0" y="0" width="100" height="10" class="track"/>{bar}</svg>'
                        f'<span class="fr-v">{esc(txt)}</span></div>')
        body = "".join(rows)
        alt = "; ".join((r[0] + ": " + (r[2] if f["kind"] == "bars" else f"{r[1]} of {r[2]}")) for r in f["rows"])
    elif f["kind"] == "log":
        import math
        top = 6.0
        bx = round(math.log10(f["bar"]) / top * 100, 2)
        for label, v in f["rows"]:
            w = round(math.log10(v) / top * 100, 2)
            vtxt = f"{v:g}" if v < 1000 else f"{v:,}".replace(".0", "")
            rows.append(f'<div class="fr"><span class="fr-l">{esc(label)}</span>'
                        f'<svg class="fr-svg" viewBox="0 0 100 10" preserveAspectRatio="none" aria-hidden="true">'
                        f'<rect x="0" y="0" width="100" height="10" class="track"/>'
                        f'<rect x="0" y="0" width="{w}" height="10" rx="1.5" class="bar{" bar-pass" if v <= f["bar"] else ""}"/>'
                        f'<line x1="{bx}" x2="{bx}" y1="-2" y2="12" class="ref"/></svg>'
                        f'<span class="fr-v">{vtxt} ULP</span></div>')
        ticks = "".join(f'<span style="left:{round(i / top * 100, 2)}%">{t}</span>'
                        for i, t in enumerate(["1", "10", "100", "1k", "10k", "100k", "1M"]))
        rows.append(f'<div class="fr fr-axis"><span class="fr-l"></span><div class="axis">{ticks}'
                    f'<em class="ref-lab" style="left:{bx}%">2 ULP bar</em></div><span class="fr-v"></span></div>')
        body = "".join(rows)
        alt = "; ".join(f"{label}: {v:g} ULP" for label, v in f["rows"]) + "; bar: 2 ULP"
    else:  # waffle
        sq, i = [], 0
        for key, n, label in f["cells"]:
            for _ in range(n):
                x = (i % 8) * 13
                y = (i // 8) * 13
                sq.append(f'<rect x="{x}" y="{y}" width="11" height="11" rx="2" class="w-{key}"/>')
                i += 1
        legend = "".join(f'<li><i class="w-{k}"></i><b>{n}</b> {esc(lab)}</li>' for k, n, lab in f["cells"])
        body = (f'<div class="waffle"><svg viewBox="0 0 102 24" aria-hidden="true">{"".join(sq)}</svg>'
                f'<ul class="w-legend">{legend}</ul></div>')
        alt = "; ".join(f"{lab}: {n}" for k, n, lab in f["cells"])
    return f"""<figure class="fig" role="group" aria-label="{esc(f['title'])}">
  <figcaption class="fig-title">{esc(f['title'])}</figcaption>
  <div class="fig-body">{body}</div>
  <p class="sr-only">{esc(alt)}</p>
  <p class="fig-note">{esc(f['note'])} Figure drawn from the sourced results below.</p>
</figure>"""


# --------------------------------------------------------------------------
# pages
# --------------------------------------------------------------------------
def rail_items(l, kind):
    # Hand-set labels; each must be backed by text in this lab's own record.
    raw = " ".join([l["method"]] + list(l["caveats"]) + [r["claim"] for r in l["results"]])
    out = []
    for label, ev in C.RAIL[l["slug"]][kind]:
        if ev not in raw:
            raise SystemExit(f"RAIL evidence not in lab record: {l['slug']} {kind}: {ev!r}")
        out.append(label)
    return out


def q_short_links(qs):
    return "<br>".join(f'<a href="/questions/#q{q}">Q{q} {esc(C.QUESTION_SHORT[q])}</a>' for q in qs)


def render_check(l):
    out, links = [], []
    for kind, val in l["c"]["check"]:
        if kind == "p":
            v = val
            if v.startswith("Public pages:"):
                v = v[len("Public pages:"):].strip()
                if not v:
                    continue
            out.append(f"<p>{md(v)}</p>")
        elif kind == "list":
            for it in val:
                u = it.strip()
                if u.startswith("http"):
                    links.append(f'<li>{link(u, esc(short_url(u)))}<span class="u-full">{esc(u)}</span></li>')
                else:
                    links.append(f"<li>{md(u)}</li>")
        elif kind == "code":
            out.append(code_block(val.strip(), f"cmd-{l['slug']}"))
    lk = f'<ul class="check-links">{"".join(links)}</ul>' if links else ""
    return lk + "".join(out)


# --------------------------------------------------------------------------
# picture explainers
# --------------------------------------------------------------------------
EX_FIELDS = ("question", "why", "headline", "result", "meaning")


def explainer_of(l):
    """The lab's explainer with prose rules applied; checks its shape."""
    ex = l.get("explainer")
    assert ex, ("no explainer", l["slug"])
    out = {k: prose(ex[k]) for k in EX_FIELDS}
    out["steps"] = [prose(x) for x in ex["steps"]]
    out["icons"] = list(ex["icons"])
    out["analogy"] = prose(ex["analogy"]) if ex.get("analogy") else None
    out["sources"] = list(ex["sources"])
    assert 2 <= len(out["steps"]) <= 5 and len(out["icons"]) == len(out["steps"]), l["slug"]
    assert all(i in XP.ICONS for i in out["icons"]), l["slug"]
    if l["outcome"] == "held":
        assert not out["sources"] and not re.search(r"\d", out["headline"] + out["result"]), "held-back lab must carry no numbers"
    return out


def explainer_words(l, ex):
    steps = "".join(f"<li>{esc(x)}</li>" for x in ex["steps"])
    if ex["sources"]:
        src = '<ul class="check-links">' + "".join(f"<li>{link(u, esc(short_url(u)))}</li>" for u in ex["sources"]) + "</ul>"
    else:
        src = "<p>Nothing is published for this lab: the result is held back, so there is no source to link.</p>"
    an = f"<dt>Everyday comparison</dt><dd>{esc(ex['analogy'])}</dd>" if ex["analogy"] else ""
    return f"""<div class="ex-words">
  <h3>The same picture, in words</h3>
  <dl>
    <dt>Question</dt><dd>{esc(ex['question'])}</dd>
    <dt>Why it matters</dt><dd>{esc(ex['why'])}</dd>
    <dt>How the test works</dt><dd><ol>{steps}</ol></dd>
    <dt>What we found</dt><dd class="ex-res"><strong>{esc(ex['headline'])}.</strong> {esc(ex['result'])}</dd>
    <dt>What it means</dt><dd>{esc(ex['meaning'])}</dd>
    {an}
    <dt>Where the facts come from</dt><dd>{src}</dd>
  </dl>
</div>"""


def explainer_section(l, site_css):
    """Inline picture (wide and phone versions), its words, and the shareable files."""
    ex = explainer_of(l)
    lab = OUT[l["outcome"]][0]
    meta = {"code": l["code"], "title": l["title"]}
    title = f"{l['title']}: the test explained in one picture"
    desc = (f"Question: {ex['question']} How we tested: " + " ".join(f"{i + 1}. {x}" for i, x in enumerate(ex["steps"]))
            + f" What we found ({lab}): {ex['headline']}. {ex['result']} What it means: {ex['meaning']}")
    try:
        wh, hh, hb = XP.horizontal(l["slug"], ex, lab, meta)
        wv, hv, vb = XP.vertical(l["slug"], ex, lab, meta)
    except ValueError as e:
        raise SystemExit(f"explainer layout: {l['slug']}: {e}")
    h_svg = XP.inline(wh, hh, hb, title, desc, "ex-h", l["outcome"])
    v_svg = XP.inline(wv, hv, vb, title, desc, "ex-v", l["outcome"])
    file_svg = XP.standalone(wh, hh, hb, title, desc, l["outcome"], site_css)
    write_file(f"labs/{l['slug']}/explainer.svg", file_svg)
    png_rel = f"labs/{l['slug']}/explainer.png"
    has_png = (PUBLIC / png_rel).exists()
    if has_png:
        WRITTEN.append(png_rel)
    share = (f'<p class="ex-share">Share this picture: <a href="/labs/{l["slug"]}/explainer.svg">SVG</a>'
             + (f' &middot; <a href="/labs/{l["slug"]}/explainer.png">PNG (1200 x 630)</a>' if has_png else "") + "</p>")
    sec = f"""<section class="explainer" aria-labelledby="ex-h">
  <div class="wrap">
    <h2 id="ex-h">The test in one picture</h2>
    <p class="ex-sub-lede">Question, method, result and meaning, in plain words. The sourced detail is further down the page.</p>
    <figure class="ex-fig o-{l['outcome']}">{h_svg}{v_svg}</figure>
    {explainer_words(l, ex)}
    {share}
  </div>
</section>"""
    return sec, (f"/{png_rel}" if has_png else None)


def glance_section(labs):
    """'All labs at a glance': mini pictures grouped by hard question."""
    groups = {}
    for l in labs:
        groups.setdefault(l["qs"][0] if l["qs"] else 0, []).append(l)
    out = []
    for q in sorted(groups):
        cards = []
        for l in groups[q]:
            ex = explainer_of(l)
            lab = OUT[l["outcome"]][0]
            mini = XP.mini(ex, l["outcome"])
            cards.append(f"""<li class="glance-card o-{l['outcome']}"><a href="/labs/{l['slug']}/">
  <span class="gc-mini"><svg viewBox="0 0 240 48" role="img" aria-label="{esc(l['code'])}: {esc(len(ex['steps']))} steps, then {esc(lab)}" focusable="false">{mini}</svg></span>
  <span class="gc-head">{esc(ex['headline'])}</span>
  <span class="gc-meta">{l['code']} &middot; {esc(lab)}</span>
  <span class="gc-title">{esc(l['title'])}</span>
</a></li>""")
        name = f"Q{q} &middot; {esc(C.QUESTION_SHORT[q])}" if q else "Other"
        out.append(f'<div class="glance-group"><h3>{name}</h3><ul class="glance-grid">{"".join(cards)}</ul></div>')
    return f"""<section class="wrap glance" aria-labelledby="glance-h">
  <h2 id="glance-h">All labs at a glance</h2>
  <p class="glance-video"><a href="/cis2/explainer/">Watch the 4-minute CIS-2 explainer {ARROW}</a></p>
  <p class="ex-sub-lede">Each lab as a small picture: the question, the steps of the test, then the verdict. Grouped by the hard question it belongs to. Open any card for the full picture and the sourced detail.</p>
  {"".join(out)}
</section>"""


def lab_page(l, labs, data):
    c = l["c"]
    idx = l["no"] - 1
    prev_l = labs[idx - 1] if idx > 0 else None
    next_l = labs[idx + 1] if idx + 1 < len(labs) else None
    models = rail_items(l, "models")
    hw = rail_items(l, "hardware")
    qlinks = q_short_links(l["qs"]) or "None listed"
    eq = "".join(f' <a class="eb-q" href="/questions/#q{q}">Q{q} &middot; {esc(C.QUESTION_SHORT[q])}</a>' for q in l["qs"])
    nsrc = len(set([r["url"] for r in l["results"]] + l["public_urls"]))
    rail_rows = [("Lab", f'{l["code"]} <span class="muted">of 33</span>'),
                 ("Date", esc(date_txt(l))),
                 ("Outcome", badge(l["outcome"])),
                 ("Hard question", qlinks)]
    if models:
        rail_rows.append(("Models", "<br>".join(esc(m) for m in models)))
    if hw:
        rail_rows.append(("Hardware", "<br>".join(esc(h) for h in hw)))
    rail_rows.append(("Public sources", str(nsrc) if nsrc else "None (held back)"))
    rail_rows.append(("Reproduction", "Run by us; no unaffiliated reproduction"))
    rail = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in rail_rows)

    toc = [("ex-h", "The test in one picture"), ("why", "Why it matters"), ("method", "Method"), ("results", "Results"),
           ("not-show", "What it does NOT show"), ("scope", "Scope and caveats"),
           ("outcome", "Outcome"), ("learned", "What we learned"), ("check", "Check it yourself")]
    toc_html = "".join(f'<li><a href="#{a}">{t}</a></li>' for a, t in toc)

    steps = "".join(f"<li>{md(s)}</li>" for s in c["steps"])
    if l["results"]:
        results = '<ol class="results">' + "".join(evidence(r, i + 1) for i, r in enumerate(l["results"])) + "</ol>"
    else:
        results = f'<div class="held-note">{badge("held")}<p>{md(c["results_note"])}</p></div>'
    caveats = "".join(f"<li>{md(x)}</li>" for x in l["caveats"])
    olab, odef = OUT[l["outcome"]]

    related = []
    for o in labs:
        if o["slug"] != l["slug"] and set(o["qs"]) & set(l["qs"]):
            related.append(o)
    if len(related) < 3:
        for o in (prev_l, next_l):
            if o and o not in related:
                related.append(o)
    related = related[:3]
    rel_html = "".join(lab_card(o) for o in related)
    pn = '<nav class="prevnext" aria-label="Previous and next lab">'
    pn += (f'<a class="pn-prev" href="/labs/{prev_l["slug"]}/"><span>&larr; {prev_l["code"]}</span>{esc(prev_l["title"])}</a>'
           if prev_l else "<span></span>")
    pn += (f'<a class="pn-next" href="/labs/{next_l["slug"]}/"><span>{next_l["code"]} &rarr;</span>{esc(next_l["title"])}</a>'
           if next_l else "<span></span>")
    pn += "</nav>"

    ex_sec, og_png = explainer_section(l, (ASSETS_SRC / "site.css").read_text())
    body = f"""<article class="lab o-{l['outcome']}">
<header class="lab-head">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="/">Home</a></li><li><a href="/labs/">Labs</a></li><li aria-current="page">{l['code']}</li></ol></nav>
    <p class="eyebrow"><span class="lc-no">{l['code']}</span> {time_el(l)} {badge(l['outcome'])}{eq}</p>
    <h1 class="lab-title">{esc(l['title'])}</h1>
    <p class="lab-q"><span>Question</span>{md(c['question'])}</p>
    <p class="prov"><span class="prov-dot" aria-hidden="true"></span>Run by us; no unaffiliated reproduction</p>
  </div>
</header>
{ex_sec}
<div class="wrap lab-grid">
  <div class="lab-body prose-col">
    <section id="why" aria-labelledby="why-h"><h2 id="why-h"><span class="sn">01</span>Why it matters</h2><p class="lead">{md(c['why'])}</p></section>
    <section id="method" aria-labelledby="method-h"><h2 id="method-h"><span class="sn">02</span>Method, step by step</h2>
      <ol class="steps">{steps}</ol>
      <div class="recorded"><p class="rec-k">Method as recorded</p><p>{md(l['method'])}</p></div>
    </section>
    <section id="results" aria-labelledby="results-h"><h2 id="results-h"><span class="sn">03</span>Results, exact and sourced</h2>
      {figure(l['slug'])}
      {results}
    </section>
    <section id="not-show" class="not-show" aria-labelledby="ns-h"><h2 id="ns-h"><span class="sn">04</span>What it does NOT show</h2><p>{md(c['not_show'])}</p></section>
    <section id="scope" aria-labelledby="scope-h"><h2 id="scope-h"><span class="sn">05</span>Scope and caveats</h2><ul class="caveats">{caveats}</ul></section>
    <section id="outcome" aria-labelledby="out-h"><h2 id="out-h"><span class="sn">06</span>Outcome</h2>
      <div class="outcome-box">{badge(l['outcome'], big=True)}<p>{esc(odef)}</p></div></section>
    <section id="learned" aria-labelledby="learn-h"><h2 id="learn-h"><span class="sn">07</span>What we learned</h2><p class="learned">{md(l['learned'])}</p></section>
    <section id="check" aria-labelledby="check-h"><h2 id="check-h"><span class="sn">08</span>Check it yourself</h2>{render_check(l)}</section>
  </div>
  <aside class="rail" aria-labelledby="rail-h">
    <h2 class="rail-h" id="rail-h">Lab record</h2>
    <dl class="rail-dl">{rail}</dl>
    <div class="rail-ledger"><p class="rail-k">Position among all 33 labs</p>{ledger(labs, compact=True, current=l['slug'])}</div>
    <nav class="toc" aria-label="On this page"><p class="rail-k">On this page</p><ol>{toc_html}</ol></nav>
  </aside>
</div>
<section class="wrap related" aria-labelledby="rel-h">
  <h2 id="rel-h" class="related-h">Related labs</h2>
  <ul class="lab-grid-cards">{rel_html}</ul>
  {pn}
</section>
</article>"""
    desc = f"{prose(c['question'])} Outcome: {olab}. Run by us; no unaffiliated reproduction."
    page(f"/labs/{l['slug']}/", l["title"], desc, body, active="/labs/", og_image=og_png)


def labs_index(labs, data):
    counts = {k: sum(1 for l in labs if l["outcome"] == k) for k, _, _ in C.OUTCOMES}
    ochips = ['<button type="button" class="chip" data-f="outcome" data-v="all" aria-pressed="true">All <b>33</b></button>']
    for k, lab, d in C.OUTCOMES:
        ochips.append(f'<button type="button" class="chip o-{k}" data-f="outcome" data-v="{k}" aria-pressed="false"><i aria-hidden="true"></i>{lab} <b>{counts[k]}</b></button>')
    qchips = ['<button type="button" class="chip" data-f="q" data-v="all" aria-pressed="true">All questions</button>']
    for q in data["questions"]:
        qchips.append(f'<button type="button" class="chip" data-f="q" data-v="{q["n"]}" aria-pressed="false" title="{esc(q["q"])}"><span class="chip-n">Q{q["n"]}</span>{esc(C.QUESTION_SHORT[q["n"]])}</button>')
    cards = "".join(lab_card(l) for l in labs)
    body = f"""<section class="page-head">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="/">Home</a></li><li aria-current="page">Labs</li></ol></nav>
    <p class="kicker">The labs</p>
    <h1 class="display">Thirty-three labs. <em>Every outcome shown.</em></h1>
    <p class="lede">Failures, nulls, retractions and corrections of our own work are listed with the successes. Every result is run by us. No unaffiliated party has reproduced any of it yet.</p>
    {ledger(labs)}
  </div>
</section>
{glance_section(labs)}
<section class="wrap labs-index" aria-labelledby="all-h">
  <h2 class="sr-only" id="all-h">All labs</h2>
  <div class="filters" role="group" aria-label="Filter labs">
    <div class="f-row"><span class="f-k" id="f-o">Outcome</span><div class="chips" role="group" aria-labelledby="f-o">{"".join(ochips)}</div></div>
    <div class="f-row"><span class="f-k" id="f-q">Hard question</span><div class="chips chips-scroll" role="group" aria-labelledby="f-q">{"".join(qchips)}</div></div>
    <p class="f-count" aria-live="polite" data-count>Showing 33 of 33 labs</p>
  </div>
  <ul class="lab-grid-cards" data-labs>{cards}</ul>
  <p class="f-empty" data-empty hidden>No lab matches both filters. <button type="button" class="linkish" data-reset>Clear filters</button></p>
</section>"""
    page("/labs/", "Labs", "All 33 labs run by Aefinity AI, with positive, mixed, negative, null and held-back outcomes, each with sourced results.", body, active="/labs/")


def home(labs, data):
    by = {l["slug"]: l for l in labs}
    mission = data["mission"]
    first, rest = mission.split(". ", 1)
    assert first + "." == C.HERO["mission_note"], first
    hw = "".join(f'<li><span class="hw-n">{i + 1:02d}</span><h3>{esc(t)}</h3><p>{esc(d)}</p></li>' for i, (t, d) in enumerate(C.HOW_WE_WORK))
    qlist = "".join(
        f'<li><a href="/questions/#q{q["n"]}"><span class="q-n">{q["n"]:02d}</span><span class="q-t">{esc(q["q"])}</span>'
        f'<span class="q-c">{len(q["labs"])} lab{"s" if len(q["labs"]) != 1 else ""}</span></a></li>' for q in data["questions"])
    assert sorted(by[s]["outcome"] for s in C.HOME_LABS) == ["mixed", "mixed", "negative", "negative", "positive", "positive"]
    hl = "".join(lab_card(by[s]) for s in C.HOME_LABS)
    les = {x["n"]: x for x in data["lessons"]}
    lessons = "".join(f'<li><a href="/learned/#lesson-{n}"><span class="ls-n">{n:02d}</span><span>{esc(les[n]["lead"])}</span></a></li>' for n in C.HOME_LESSONS)
    practices = "".join(f"<li>{md(p)}</li>" for p in data["std_practices"])
    mq = [q for q in data["std_quotes"] if q[0].startswith("Open the PR")][0]
    projects = ""
    for p in data["projects"]:
        if p["name"] == "Elsewhere":
            continue
        desc = [b[1] for b in p["blocks"] if b[0] == "p"][0]
        projects += f'<li class="proj"><h3><a href="/projects/#{slugify(p["name"])}">{esc(p["name"])}</a></h3><p>{md(desc)}</p></li>'
    body = f"""<section class="hero" aria-labelledby="hero-h">
  <div class="wrap hero-grid">
   <div>
    <p class="kicker kicker-acc">{esc(C.HERO["kicker"])}</p>
    <h1 class="hero-h hero-h-biz" id="hero-h">{C.HERO["h1"]}</h1>
    <p class="hero-lede">{esc(C.HERO["lede"])}</p>
    <div class="cta-row"><a class="btn btn-lg" href="{C.NAV_CTA[0]}">{C.NAV_CTA[1]} {ARROW}</a><a class="btn btn-ghost" href="#of-h">What we offer</a></div>
    {video_card("video-cta video-cta-sm")}
    <p class="hero-mission">{esc(first)}. <a href="/mission/">Our mission {ARROW}</a> <span aria-hidden="true">&middot;</span> <a href="/labs/">All 33 labs {ARROW}</a></p>
   </div>
   <div class="hero-ledger">
    <div class="hl-head"><p class="kicker">The record so far</p><p class="hl-note">Each mark is one lab, grouped by outcome. Select a mark to open the lab.</p></div>
    {ledger(labs)}
   </div>
  </div>
</section>

{home_biz()}

<section class="section" aria-labelledby="how-h">
  <div class="wrap">
    {section_head("", "How we work", hid="how-h")}
    <ol class="how">{hw}</ol>
  </div>
</section>

<section class="section alt" aria-labelledby="hq-h">
  <div class="wrap split">
    {section_head("", "The hard questions", "Ten questions AI raises that we can test, each with what we found so far and what is still open.", hid="hq-h")}
    <ol class="qlist">{qlist}</ol>
  </div>
</section>

<section class="section" aria-labelledby="hl-h">
  <div class="wrap">
    {section_head("", "Six labs, good and bad", "Chosen for balance: two positive, two mixed, two negative. The outcome label on every lab is ours, and the other 27 are one click away.", hid="hl-h")}
    <ul class="lab-grid-cards">{hl}</ul>
    <p class="more"><a href="/labs/">All 33 labs {ARROW}</a></p>
  </div>
</section>

<section class="section alt" aria-labelledby="ls-h">
  <div class="wrap split">
    {section_head("", "What we have learned", "Each lesson cites the labs it comes from. All are from our own runs, at the scopes stated in those labs.", hid="ls-h")}
    <div><ol class="lessons-mini">{lessons}</ol><p class="more"><a href="/learned/">All 12 lessons {ARROW}</a></p></div>
  </div>
</section>

<section class="section" aria-labelledby="st-h">
  <div class="wrap split">
    {section_head("", "Our test standard", esc(data["std_intro"]), hid="st-h")}
    <div>
      <ul class="ticks">{practices}</ul>
      <figure class="pull"><blockquote cite="{esc(mq[1])}"><p>{esc(mq[0])}</p></blockquote><figcaption>{link(mq[1], esc(short_url(mq[1])))}</figcaption></figure>
      <p class="more"><a href="/standard/">The standard, and what it cannot prove {ARROW}</a></p>
    </div>
  </div>
</section>

<section class="section alt" aria-labelledby="pj-h">
  <div class="wrap">
    {section_head("", "Projects", hid="pj-h")}
    <ul class="proj-grid">{projects}</ul>
  </div>
</section>

{cta_band(C.BRIEFING["title"], esc(C.BRIEFING["body"]) + ' Running inference already? <a href="/pilot">See the replay pilot</a>.', cls="cta-band cta-lite")}

<section class="aspiration" aria-labelledby="asp-h">
  <div class="wrap">
    <h2 class="kicker" id="asp-h">Our aspiration</h2>
    <p class="asp-text">{esc(data["aspiration"])}</p>
    <p class="asp-note">{esc(data["aspiration_note"])}</p>
  </div>
</section>"""
    page("/", "Aefinity AI: hard questions about AI, tested in the open",
         "We take the hard questions AI raises and study, experiment and test as rigorously as we can. 33 labs, every outcome shown, every result run by us.",
         body, active="/", canonical="/")


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def simple_head(crumb, kicker, h1, lede_html):
    return f"""<section class="page-head">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="/">Home</a></li><li aria-current="page">{crumb}</li></ol></nav>
    <p class="kicker">{kicker}</p>
    <h1 class="display">{h1}</h1>
    {lede_html}
  </div>
</section>"""


def mission_page(labs, data):
    counts = {k: sum(1 for l in labs if l["outcome"] == k) for k, _, _ in C.OUTCOMES}
    legend = "".join(
        f'<li class="lg-row o-{k}">{badge(k)}<p>{esc(d)}</p><a href="/labs/?outcome={k}">{counts[k]} lab{"s" if counts[k] != 1 else ""}</a></li>'
        for k, lab, d in C.OUTCOMES)
    first, rest = data["mission"].split(". ", 1)
    read = "".join(
        '<li>Outcome labels are ours; <a href="#leg-h">the five definitions are below</a>.</li>'
        if x.startswith("Outcome labels are ours:") else f"<li>{md(x)}</li>"
        for x in data["how_to_read"])
    body = f"""{simple_head("Mission", "Our mission", esc(first) + ".", f'<p class="lede">{esc(rest)}</p>')}
<section class="section" aria-labelledby="are-h">
  <div class="wrap">
    {section_head("", "What we are, and are not", hid="are-h")}
    <div class="are-grid">
      <div class="are not"><p class="are-k">We are not</p><p class="are-t">Another AI platform or cloud service.</p></div>
      <div class="are yes"><p class="are-k">We are</p><p class="are-t">People who take the hard questions AI raises about the future of humanity, and study, experiment and test as rigorously as we can.</p></div>
    </div>
  </div>
</section>
<section class="section alt" aria-labelledby="who-h">
  <div class="wrap">
    {section_head("", "Who we are", "AEFINITY AI INC. is a Texas corporation in Orange, Texas, founded and run by two co-founders.", hid="who-h")}
    <div class="are-grid">
      <div class="are yes"><p class="are-k">Co-founder and CEO</p><p class="are-t">Justin Thompson</p><p>Leads the research and the technical work.</p><p><a href="mailto:justin@aefinityai.com">justin@aefinityai.com</a></p></div>
      <div class="are yes"><p class="are-k">Co-founder and Vice President</p><p class="are-t">Shannon Heslop</p><p>Runs business and operations, and speaks for the company.</p><p><a href="mailto:shannon@aefinityai.com">shannon@aefinityai.com</a></p></div>
    </div>
  </div>
</section>
<section class="aspiration in-page" aria-labelledby="asp-h">
  <div class="wrap">
    <h2 class="kicker" id="asp-h">Our aspiration</h2>
    <p class="asp-text">{esc(data["aspiration"])}</p>
    <p class="asp-note">{esc(data["aspiration_note"])}</p>
  </div>
</section>
<section class="section" aria-labelledby="read-h">
  <div class="wrap split">
    {section_head("", "How to read this site", hid="read-h")}
    <ul class="ticks">{read}</ul>
  </div>
</section>
<section class="section alt" aria-labelledby="leg-h">
  <div class="wrap split">
    {section_head("", "Outcome labels", "Every lab carries one of five labels. The labels are ours, and each is shown with the same weight.", hid="leg-h")}
    <ul class="legend">{legend}</ul>
  </div>
</section>"""
    page("/mission/", "Mission", "Our mission, our aspiration, what we are and are not, and what each outcome label means.", body, active="/mission/")


def lab_chip(l):
    return f'<li><a class="lab-chip o-{l["outcome"]}" href="/labs/{l["slug"]}/"><i aria-hidden="true"></i><span class="lc-no">{l["code"]}</span><span class="lch-t">{esc(l["title"])}</span><span class="lch-o"><span class="sr-only">, </span>{OUT[l["outcome"]][0]}</span></a></li>'


def questions_page(labs, data):
    by = {l["slug"]: l for l in labs}
    items = []
    for q in data["questions"]:
        chips = "".join(lab_chip(by[s]) for s in q["labs"])
        items.append(f"""<li class="hq" id="q{q['n']}">
  <div class="hq-n" aria-hidden="true">{q['n']:02d}</div>
  <div class="hq-body">
    <h2 class="hq-q"><span class="sr-only">Question {q['n']}: </span>{esc(q['q'])}</h2>
    <div class="hq-cols">
      <div><p class="hq-k">What we found so far</p><p>{md(q['found'])}</p></div>
      <div><p class="hq-k">Still open</p><p>{md(q['still'])}</p></div>
    </div>
    <p class="hq-k">Labs that address it</p>
    <ul class="lab-chips">{chips}</ul>
  </div>
</li>""")
    toc = "".join(f'<li><a href="#q{q["n"]}"><span>{q["n"]:02d}</span>{esc(C.QUESTION_SHORT[q["n"]])}</a></li>' for q in data["questions"])
    oq = "".join(f'<li><h3>{esc(a)}</h3><p>{md(b)}</p></li>' for a, b in data["open"])
    body = f"""{simple_head("Questions", "The hard questions", "Ten questions. <em>What we found, and what is still open.</em>", '<p class="lede">Each finding is from our own runs, at the scopes stated in the labs it links to.</p>')}
<div class="wrap q-layout">
  <nav class="q-toc" aria-label="Questions"><ol>{toc}</ol></nav>
  <ol class="hq-list">{''.join(items)}</ol>
</div>
<section class="section alt" aria-labelledby="oq-h">
  <div class="wrap split">
    {section_head("", "Open questions we have not tested yet", esc(data["open_intro"]), hid="oq-h")}
    <ul class="open-q">{oq}</ul>
  </div>
</section>"""
    page("/questions/", "The hard questions", "Ten hard questions about AI, what our labs found so far, what is still open, and the questions we have not tested yet.", body, active="/questions/")


def standard_page(labs, data):
    pr = "".join(f'<li><span class="pr-n">{i + 1:02d}</span><p>{md(p)}</p></li>' for i, p in enumerate(data["std_practices"]))
    qs = "".join(f'<li><figure class="evidence ev-prose"><blockquote cite="{esc(u)}"><p>{quote_html(q)}</p></blockquote>'
                 f'<figcaption><span class="ev-lab">Verbatim source</span> {link(u, esc(short_url(u)))}</figcaption></figure></li>'
                 for q, u in data["std_quotes"])
    cannot = "".join(f"<li>{md(x)}</li>" for x in data["std_cannot"])
    body = f"""{simple_head("Standard", "Our test standard", "A standard we state, <em>and its limits.</em>", f'<p class="lede">{esc(data["std_intro"])}</p>')}
<section class="section" aria-labelledby="pr-h">
  <div class="wrap">
    {section_head("", "The practices", hid="pr-h")}
    <ol class="practices">{pr}</ol>
  </div>
</section>
<section class="section alt" aria-labelledby="ow-h">
  <div class="wrap split">
    {section_head("", "In the repository's own words", "Quoted verbatim from the public cis2-spec repository.", hid="ow-h")}
    <ul class="quotes">{qs}</ul>
  </div>
</section>
<section class="section" aria-labelledby="cp-h">
  <div class="wrap split">
    {section_head("", "What the standard cannot prove", hid="cp-h")}
    <div class="not-show"><ul class="caveats">{cannot}</ul></div>
  </div>
</section>
<section class="section alt" aria-labelledby="dt-h">
  <div class="wrap split">
    {section_head("", "Details", hid="dt-h")}
    <p class="lead">{md(data["std_details"])}</p>
  </div>
</section>"""
    page("/standard/", "Our test standard", "How we test: pass marks before runs, a public hash-chained ledger, provenance on every number, numbered errata, and what the standard cannot prove.", body, active="/standard/")


def learned_page(labs, data):
    by = {l["slug"]: l for l in labs}
    items = "".join(f"""<li class="lesson" id="lesson-{x['n']}">
  <div class="ls-num" aria-hidden="true">{x['n']:02d}</div>
  <div><h2 class="ls-lead"><span class="sr-only">Lesson {x['n']}: </span>{esc(x['lead'])}</h2><p>{md(x['body'])}</p>
  <p class="hq-k">From the labs</p><ul class="lab-chips">{''.join(lab_chip(by[s]) for s in x['labs'])}</ul></div>
</li>""" for x in data["lessons"])
    body = f"""{simple_head("Learned", "What we have learned", "Twelve lessons, <em>each tied to its labs.</em>", f'<p class="lede">{esc(data["lessons_intro"])}</p>')}
<section class="wrap" aria-label="Lessons"><ol class="lessons">{items}</ol></section>"""
    page("/learned/", "What we have learned", "Twelve lessons from our own labs, each linked to the labs it comes from, at the scopes stated there.", body, active="/learned/")


def projects_page(labs, data):
    by = {l["slug"]: l for l in labs}
    out = []
    for p in data["projects"]:
        pid = slugify(p["name"])
        parts, chips = [], ""
        for kind, val in p["blocks"]:
            if kind == "p" and val.startswith("Labs:"):
                chips = "".join(lab_chip(by[s]) for s in re.findall(r"\(#lab-([a-z0-9-]+)\)", val))
            elif kind == "p" and val.strip() == "Reproduce it:":
                parts.append('<h3 class="pj-sub">Reproduce it</h3>')
            elif kind == "p":
                parts.append(f"<p>{md(val)}</p>")
            elif kind == "list":
                lis = []
                for it in val:
                    m = re.match(r"^(.+?): (https?://\S+)$", it)
                    if m:
                        lis.append(f'<li><span class="pl-k">{esc(m.group(1))}</span>{link(m.group(2), esc(short_url(m.group(2))))}</li>')
                    else:
                        lis.append(f"<li>{md(it)}</li>")
                parts.append(f'<ul class="pj-links">{"".join(lis)}</ul>')
            elif kind == "code":
                parts.append(code_block(val.strip(), f"cmd-{pid}"))
        labs_html = f'<p class="hq-k">Labs</p><ul class="lab-chips">{chips}</ul>' if chips else ""
        out.append(f"""<section class="project" id="{pid}" aria-labelledby="{pid}-h">
  <div class="pj-name"><h2 id="{pid}-h">{esc(p['name'])}</h2></div>
  <div class="pj-body">{''.join(parts)}{labs_html}</div>
</section>""")
    body = f"""{simple_head("Projects", "Projects", "Open work <em>you can check.</em>", '<p class="lede">CIS-2, ALICE and RANGER are public repositories. Each lists the labs that tested it.</p>')}
<div class="wrap projects">{''.join(out)}</div>"""
    page("/projects/", "Projects", "CIS-2, ALICE and RANGER: open specifications, engines and research notes, with the labs that tested each and the command to reproduce CIS-2.", body, active="/projects/")


def pilot_page():
    P = C.PILOT
    glance = "".join(f"<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>" for k, v in P["glance"])
    rep = "".join(f'<li><span class="r">{r}</span><span class="{"m" if ok else "x"}">{"match" if ok else "differs"}</span><span class="s">{esc(s)}</span></li>' for r, ok, s in P["report_rows"])
    who = "".join(f"<li><h3>{esc(a)}</h3><p>{esc(b)}</p></li>" for a, b in P["who"])
    steps = "".join(f'<li><span class="hw-n">{i + 1:02d}</span><h3>{esc(a)}</h3><p>{esc(b)}</p></li>' for i, (a, b) in enumerate(P["steps"]))
    get = "".join(f"<li><h3>{esc(a)}</h3><p>{esc(b)}</p></li>" for a, b in P["get"])
    nots = "".join(f"<li><h3>{esc(a)}</h3><p>{esc(b)}</p></li>" for a, b in P["not"])
    lines = "".join(f"<li>{esc(x)}</li>" for x in P["lines"])
    start = esc(P["start"]).replace(C.EMAIL, f'<a href="{P["mailto_short"]}">{C.EMAIL}</a>')
    body = f"""<section class="page-head pilot-head">
  <div class="wrap pilot-hero">
    <div>
      <nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="/">Home</a></li><li aria-current="page">Paid pilots</li></ol></nav>
      <p class="kicker">Paid pilots</p>
      <h1 class="display">Paid pilots: do your receipts replay <em>bit for bit</em> elsewhere?</h1>
      <p class="lede">{esc(P["lede"])}</p>
      <div class="cta-row"><a class="btn" href="{P['mailto_short']}">Email us about a pilot</a><a class="btn btn-ghost" href="#before">Start with the self-check</a></div>
    </div>
    <aside class="glance" aria-labelledby="gl-h">
      <h2 class="rail-h" id="gl-h">At a glance</h2>
      <dl class="rail-dl">{glance}</dl>
      <figure class="report-mini">
        <div class="rm-bar" aria-hidden="true"><span>mismatch report</span><span class="rm-tag">Illustration</span></div>
        <ol aria-hidden="true">{rep}</ol>
        <figcaption>{esc(P["report_caption"])}</figcaption>
      </figure>
    </aside>
  </div>
</section>
<section class="section" id="who" aria-labelledby="who-h"><div class="wrap">{section_head("01", "Who it is for", hid="who-h")}<ul class="cards3">{who}</ul></div></section>
<section class="section alt" id="process" aria-labelledby="pr-h"><div class="wrap">{section_head("02", "What happens", esc(P["steps_intro"]), hid="pr-h")}<ol class="how">{steps}</ol></div></section>
<section class="section" id="get" aria-labelledby="get-h"><div class="wrap split">{section_head("03", "What you get", hid="get-h")}<ul class="cards-list ok">{get}</ul></div></section>
<section class="section alt" id="not" aria-labelledby="not-h"><div class="wrap split">{section_head("04", "What it is not", hid="not-h")}<ul class="cards-list no">{nots}</ul></div></section>
<section class="section" id="before" aria-labelledby="bf-h"><div class="wrap split">{section_head("05", "Before you write", esc(P["before"]), hid="bf-h")}
  <div>{code_block(C.SELFCHECK_CMD, "cmd-pilot")}<p class="fine">{esc(P["before_fine"]).replace("The README", '<a class="ext" href="https://github.com/Aefinity-AI/cis2-spec">The README</a>', 1)}</p></div></div></section>
<section class="section alt" id="start" aria-labelledby="st-h"><div class="wrap split">
  <header class="sec-head"><span class="sec-n">06</span><h2 class="sec-title" id="st-h">How to start</h2><p class="sec-intro">{start}</p>
  <p class="fine">{esc(P["about"])} Phone <a href="tel:{C.PHONE_TEL}">{C.PHONE_DISPLAY}</a>.</p></header>
  <div class="email-tpl">
    <div class="et-head"><span><b>To</b>{C.EMAIL}</span><span><b>Subject</b>CIS-2 pilot</span></div>
    <ol>{lines}</ol>
    <div class="et-foot"><a class="btn" href="{esc(P['mailto'])}">Open this email</a><a class="btn btn-ghost ext" href="https://github.com/Aefinity-AI/cis2-spec">CIS-2 on GitHub</a></div>
  </div>
</div></section>"""
    page("/pilot", "Paid pilots", "Paid pilots: we replay your CIS-2 receipts on a machine separate from yours and report every mismatch.", body, active="/pilot", canonical="/pilot")


def not_found():
    body = f"""{simple_head("Not found", "404", "This page <em>is not here.</em>", '<p class="lede">The address may have changed. These pages are:</p>')}
<section class="section"><div class="wrap"><ul class="nf-links">{''.join(f'<li><a href="{h}">{t} {ARROW}</a></li>' for h, t in [("/", "Home")] + C.FOOT_NAV)}</ul></div></section>"""
    page("/404.html", "Page not found", "This page is not here.", body, canonical="/404")


# --------------------------------------------------------------------------
# commercial pages
# --------------------------------------------------------------------------
# 24x24 stroke icons, drawn for this site. currentColor; sized by CSS.
ICONS = {
    "alice": '<rect x="3.5" y="3.5" width="17" height="17" rx="3"/><rect x="8" y="8" width="8" height="8" rx="1.5"/><path d="M10 3.5V1.8M14 3.5V1.8M10 22.2v-1.7M14 22.2v-1.7M3.5 10H1.8M3.5 14H1.8M22.2 10h-1.7M22.2 14h-1.7"/>',
    "cis": '<path d="M4 7h16M4 12h16M4 17h16"/><circle cx="8" cy="7" r="1.6"/><circle cx="15" cy="12" r="1.6"/><circle cx="10" cy="17" r="1.6"/>',
    "lock": '<rect x="4.5" y="10.5" width="15" height="10" rx="2.2"/><path d="M8 10.5V7.6a4 4 0 0 1 8 0v2.9M12 14.5v2.4"/>',
    "ops": '<circle cx="12" cy="12" r="3.2"/><path d="M12 2.8v2.6M12 18.6v2.6M2.8 12h2.6M18.6 12h2.6M5.5 5.5l1.8 1.8M16.7 16.7l1.8 1.8M5.5 18.5l1.8-1.8M16.7 7.3l1.8-1.8"/>',
    "airgap": '<path d="M3 12h6M15 12h6"/><path d="M9 8v8M15 8v8"/><path d="M11 10.5l2 3M13 10.5l-2 3" opacity=".9"/>',
    "server": '<rect x="4" y="4" width="16" height="6.5" rx="1.6"/><rect x="4" y="13.5" width="16" height="6.5" rx="1.6"/><path d="M7.5 7.25h.01M7.5 16.75h.01M11 7.25h5M11 16.75h5"/>',
    "receipt": '<path d="M6 2.8h12v18.4l-2.4-1.6-2.4 1.6-1.2-.8-1.2.8-2.4-1.6L6 21.2z"/><path d="M9 8h6M9 11.5h6M9 15h3.5"/>',
    "nocloud": '<path d="M7 18.5h9.5a4 4 0 0 0 .6-7.95A5.5 5.5 0 0 0 6.6 9.6 4.5 4.5 0 0 0 7 18.5z"/><path d="M4 3.5l16 17"/>',
    "target": '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.5"/><circle cx="12" cy="12" r="1"/>',
    "laptop": '<rect x="5" y="5" width="14" height="10" rx="1.5"/><path d="M2.5 19h19l-2-4h-15z"/>',
    "hospital": '<rect x="4" y="3.5" width="16" height="17" rx="2.5"/><path d="M12 8v8M8 12h8"/>',
    "scales": '<path d="M12 3.5v17M7 20.5h10M5 6.5h14"/><path d="M5 6.5l-2.5 6a2.8 2.8 0 0 0 5 0zM19 6.5l-2.5 6a2.8 2.8 0 0 0 5 0z"/>',
    "shield": '<path d="M12 2.8l7.5 3v5.6c0 4.6-3.2 8.4-7.5 9.8-4.3-1.4-7.5-5.2-7.5-9.8V5.8z"/><path d="M8.8 12l2.2 2.2 4.4-4.4"/>',
    "bank": '<path d="M3 9.5L12 4l9 5.5M4.5 20h15M6 10.5v7M10 10.5v7M14 10.5v7M18 10.5v7"/>',
    "bolt": '<path d="M13 2.8L5 13.5h6l-1 7.7 8-10.7h-6z"/>',
    "flask": '<path d="M9.5 3h5M10.5 3v6L4.8 18.6A1.6 1.6 0 0 0 6.2 21h11.6a1.6 1.6 0 0 0 1.4-2.4L13.5 9V3"/><path d="M7.5 15h9"/>',
    "compass": '<circle cx="12" cy="12" r="8.5"/><path d="M15.5 8.5l-2 5-5 2 2-5z"/>',
    "folder": '<path d="M3.5 7.5a2 2 0 0 1 2-2h4l2 2.5h7a2 2 0 0 1 2 2v7.5a2 2 0 0 1-2 2h-13a2 2 0 0 1-2-2z"/><path d="M10 14.5h4v3h-4zM10.8 14.5v-1a1.2 1.2 0 0 1 2.4 0v1"/>',
    "harness": '<rect x="3.5" y="3.5" width="17" height="17" rx="2.5"/><path d="M3.5 15.5h17"/><path d="M7 12l3-3.5 3 2.5 4-4.5"/>',
    "chip": '<rect x="6" y="6" width="12" height="12" rx="2"/><path d="M9.5 2.8V6M14.5 2.8V6M9.5 18v3.2M14.5 18v3.2M2.8 9.5H6M2.8 14.5H6M18 9.5h3.2M18 14.5h3.2"/><path d="M9.8 12.2l1.6 1.6 3-3.2"/>',
    "chain": '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1.2 1.2"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1.2-1.2"/>',
    "replay": '<path d="M4 12a8 8 0 1 0 2.4-5.7"/><path d="M4 3.5v4.5h4.5"/><path d="M10.5 9v6l4.5-3z"/>',
    "eye": '<path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="3"/>',
    "inbox": '<path d="M3.5 13.5l2.6-8a1.5 1.5 0 0 1 1.4-1h9a1.5 1.5 0 0 1 1.4 1l2.6 8v5a1.5 1.5 0 0 1-1.5 1.5h-14A1.5 1.5 0 0 1 3.5 18.5z"/><path d="M3.5 13.5h5l1.5 2.5h4l1.5-2.5h5"/>',
    "headset": '<path d="M4 14v-2a8 8 0 0 1 16 0v2"/><rect x="3" y="13.5" width="4" height="6" rx="1.5"/><rect x="17" y="13.5" width="4" height="6" rx="1.5"/><path d="M19 19.5c0 1.4-2 2-5 2"/>',
    "data": '<ellipse cx="12" cy="5.5" rx="7.5" ry="2.7"/><path d="M4.5 5.5v13c0 1.5 3.4 2.7 7.5 2.7s7.5-1.2 7.5-2.7v-13M4.5 12c0 1.5 3.4 2.7 7.5 2.7s7.5-1.2 7.5-2.7"/>',
    "gate": '<path d="M4 21V5M20 21V5M4 9h16M4 15h16"/><circle cx="12" cy="12" r="2"/>',
    "log": '<rect x="4.5" y="3" width="15" height="18" rx="2"/><path d="M8 7.5h8M8 11h8M8 14.5h8M8 18h4"/>',
    "check": '<circle cx="12" cy="12" r="8.5"/><path d="M8.2 12.2l2.6 2.6 5-5.4"/>',
    "stop": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7v5"/><path d="M8.5 9.5a5 5 0 1 0 7 0" opacity="0"/><rect x="9" y="9" width="6" height="6" rx="1"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3.5 6.5l8.5 6.5 8.5-6.5"/>',
    "phone": '<path d="M5 3.5h3.5l1.8 4.6-2.3 1.4a11 11 0 0 0 6.5 6.5l1.4-2.3 4.6 1.8V19a1.5 1.5 0 0 1-1.5 1.5A16.5 16.5 0 0 1 3.5 5 1.5 1.5 0 0 1 5 3.5z"/>',
    "pin": '<path d="M12 21s-6.5-6-6.5-11a6.5 6.5 0 0 1 13 0c0 5-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.3"/>',
}
ICONS["stop"] = '<circle cx="12" cy="12" r="8.5"/><rect x="9" y="9" width="6" height="6" rx="1"/>'
ICONS["play"] = '<path d="M9 6.5v11l9-5.5z"/>'


def icon(name, cls="ic"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


def check_proof(labs):
    """Every number in the proof strip must come from labs.json."""
    by = {l["slug"]: l for l in labs}
    assert C.PROOF[0]["big"] == str(len(labs)), "lab count changed"
    for p in C.PROOF:
        for key in ("check", "check2"):
            if p.get(key):
                slug, tok = p[key]
                l = by[slug]
                hay = " ".join([l["title"], l["method"]] + [r["claim"] + " " + r["quote"] for r in l["results"]] + l["caveats"])
                assert tok in hay, (slug, tok)
    for m in ("AVX2", "scalar", "aarch64"):
        assert m in by["cis2-cross-machine-digest"]["method"], m


def biz_head(crumb, kicker, h1, lead, art="", ctas=None):
    ctas = ctas if ctas is not None else [(C.NAV_CTA[0], C.NAV_CTA[1], "btn btn-lg")]
    btns = "".join(f'<a class="{c}" href="{esc(h)}">{t}{" " + ARROW if c.startswith("btn btn-lg") else ""}</a>' for h, t, c in ctas)
    return f"""<section class="biz-head">
  <div class="wrap biz-hero{" has-art" if art else ""}">
    <div class="bh-text">
      <nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="/">Home</a></li><li aria-current="page">{crumb}</li></ol></nav>
      <p class="kicker kicker-acc">{kicker}</p>
      <h1 class="biz-h">{h1}</h1>
      <p class="biz-lead">{esc(lead)}</p>
      <div class="cta-row">{btns}</div>
    </div>
    {art}
  </div>
</section>"""


def biz_section(title, body, kicker=None, hid=None, cls="", intro=None):
    k = f'<p class="kicker kicker-acc">{kicker}</p>' if kicker else ""
    i = f'<p class="bs-intro">{intro}</p>' if intro else ""
    return f"""<section class="bsec {cls}" aria-labelledby="{hid}">
  <div class="wrap">
    <header class="bs-head">{k}<h2 class="bs-title" id="{hid}">{title}</h2>{i}</header>
    {body}
  </div>
</section>"""


def engage_flow(steps):
    lis = "".join(f'<li><span class="ef-n">{i + 1}</span><h3>{esc(a)}</h3><p>{esc(b)}</p></li>' for i, (a, b) in enumerate(steps))
    return f'<ol class="eflow" style="--n:{len(steps)}">{lis}</ol>'


def cta_band(title, body, extra="", cls="cta-band"):
    return f"""<section class="{cls}" aria-labelledby="cb-h">
  <div class="wrap cb-grid">
    <div><p class="kicker">Book a briefing</p><h2 class="cb-title" id="cb-h">{esc(title)}</h2><p class="cb-body">{body}</p></div>
    <div class="cb-actions">
      <a class="btn btn-lg btn-inv" href="{C.NAV_CTA[0]}">{C.NAV_CTA[1]} {ARROW}</a>
      <a class="cb-line" href="mailto:{C.EMAIL}">{icon("mail")}<span>{C.EMAIL}</span></a>
      <a class="cb-line" href="tel:{C.PHONE_TEL}">{icon("phone")}<span>{C.PHONE_DISPLAY}</span></a>
      {extra}
    </div>
  </div>
</section>"""


def digest_strip(seed, n=32):
    """A deterministic bit pattern, the same on every row: an illustration of one digest."""
    h = hashlib.sha256(seed.encode()).digest()
    bits = "".join(f"{b:08b}" for b in h)[:n]
    return "".join(f'<i class="{"b1" if c == "1" else "b0"}"></i>' for c in bits)


def machines_figure():
    strip = digest_strip("aefinity-cis2-illustration")
    rows = "".join(f'<li><span class="mf-m">{esc(m)}</span><span class="mf-bits" aria-hidden="true">{strip}</span><span class="mf-ok">{icon("check")}<span>same</span></span></li>' for m in C.MACHINES)
    return f"""<figure class="mfig" aria-label="One digest across five kinds of hardware">
  <div class="mf-bar"><span>digest by machine</span><span class="mf-tag">Illustration</span></div>
  <ol>{rows}</ol>
  <figcaption>Same digest on AVX2, scalar x86, an AVX-512-capable CPU (generic build, self-check only), an aarch64 phone and a Tesla P100 GPU, in our own runs. The bit pattern is drawn for illustration.</figcaption>
</figure>"""


def alice_art():
    return f"""<figure class="aart" aria-hidden="true">
  <svg viewBox="0 0 360 300" class="aart-svg">
    <rect x="18" y="40" width="236" height="232" rx="18" class="a-wall"/>
    <text x="38" y="70" class="a-lab">YOUR BUILDING</text>
    <rect x="46" y="96" width="76" height="76" rx="10" class="a-box"/>
    <rect x="66" y="116" width="36" height="36" rx="5" class="a-core"/>
    <path d="M74 96v-10M94 96v-10M74 182v-10M94 182v-10M46 124h-10M46 144h-10M132 124h-10M132 144h-10" class="a-pin"/>
    <text x="46" y="198" class="a-cap">ALICE</text>
    <rect x="150" y="104" width="80" height="22" rx="5" class="a-row"/>
    <rect x="150" y="134" width="80" height="22" rx="5" class="a-row"/>
    <rect x="150" y="164" width="56" height="22" rx="5" class="a-row a-row-acc"/>
    <text x="150" y="214" class="a-cap">YOUR DATA</text>
    <path d="M46 236h176" class="a-dash"/>
    <text x="46" y="256" class="a-small">on premises · your hardware</text>
    <path d="M254 150h34" class="a-cut"/>
    <path d="M300 136l16 28M316 136l-16 28" class="a-x"/>
    <path d="M296 104h40a14 14 0 0 0 0-28 20 20 0 0 0-38-4 12 12 0 0 0-2 32z" class="a-cloud"/>
    <text x="290" y="196" class="a-small">offline</text>
  </svg>
</figure>"""


def ops_loop():
    steps = C.OPS["loop"]
    n = len(steps)
    import math
    cx, cy, r = 170, 150, 106
    nodes, arcs = [], []
    for i, s in enumerate(steps):
        a = -math.pi / 2 + i * 2 * math.pi / n
        x, y = round(cx + r * math.cos(a), 1), round(cy + r * math.sin(a), 1)
        nodes.append(f'<g class="ol-node"><circle cx="{x}" cy="{y}" r="34"/><text x="{x}" y="{y + 4.5}" text-anchor="middle">{esc(s)}</text></g>')
        a2 = -math.pi / 2 + (i + 1) * 2 * math.pi / n
        da = 0.40
        x1, y1 = round(cx + r * math.cos(a + da), 1), round(cy + r * math.sin(a + da), 1)
        x2, y2 = round(cx + r * math.cos(a2 - da), 1), round(cy + r * math.sin(a2 - da), 1)
        arcs.append(f'<path d="M{x1} {y1}A{r} {r} 0 0 1 {x2} {y2}" class="ol-arc" marker-end="url(#ol-ar)"/>')
    return f"""<figure class="oloop" aria-label="The loop the workflow runs: {", ".join(steps)}, with people signing off on money, credentials, outreach and anything public">
  <svg viewBox="0 0 340 300" aria-hidden="true">
    <defs><marker id="ol-ar" viewBox="0 0 8 8" refX="6" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L8 4L0 8z" class="ol-head"/></marker></defs>
    {"".join(arcs)}
    <circle cx="{cx}" cy="{cy}" r="44" class="ol-gate"/>
    <text x="{cx}" y="{cy - 3}" text-anchor="middle" class="ol-gt">Human</text>
    <text x="{cx}" y="{cy + 15}" text-anchor="middle" class="ol-gt">sign-off</text>
    {"".join(nodes)}
  </svg>
</figure>"""


def offer_cards():
    out = []
    for o in C.OFFERINGS:
        badge_html = f'<span class="of-badge">{icon("lock", "ic ic-xs")}{esc(o["badge"])}</span>' if o.get("badge") else ""
        out.append(f"""<li class="offer{" offer-locked" if o.get("badge") else ""}">
  <div class="of-top">{icon(o["icon"], "ic ic-lg")}{badge_html}</div>
  <p class="of-kind">{esc(o["kind"])}</p>
  <h3 class="of-tag"><a href="{o["href"]}">{esc(o["tag"])}</a></h3>
  <p class="of-body">{esc(o["body"])}</p>
  <span class="of-cta" aria-hidden="true">{esc(o["cta"])} {ARROW}</span>
</li>""")
    return f'<ul class="offers">{"".join(out)}</ul>'


def proof_strip():
    out = f"<!-- {C.LEDGER_SOURCE} (the 84) -->" + "".join(f'<li><span class="ps-big">{esc(p["big"])}</span><span class="ps-lab">{esc(p["label"])}</span></li>' for p in C.PROOF)
    return f'<ul class="proof-strip">{out}</ul>'


def home_biz():
    return f"""<section class="offer-band" aria-labelledby="of-h">
  <div class="wrap">
    <header class="ob-head"><p class="kicker kicker-acc">What we offer</p><h2 class="ob-title" id="of-h">{esc(C.OFFER_TITLE)}</h2></header>
    {offer_cards()}
    <div class="ob-proof"><p class="kicker">On the public record</p>{proof_strip()}</div>
  </div>
</section>
<section class="ops-band" aria-labelledby="opb-h">
  <div class="wrap opb-grid">
    <div>
      <p class="kicker">{esc(C.OPS_BAND["kicker"])}</p>
      <h2 class="opb-title" id="opb-h">{esc(C.OPS_BAND["title"])}</h2>
      <p class="opb-body">{esc(C.OPS_BAND["body"])}</p>
      <div class="cta-row"><a class="btn btn-lg btn-inv" href="/operations/">See how we run it {ARROW}</a><a class="btn btn-ghost-inv" href="{C.NAV_CTA[0]}">{C.NAV_CTA[1]}</a></div>
    </div>
    {ops_loop()}
  </div>
</section>"""


def alice_page(labs):
    A = C.ALICE
    caps = "".join(f'<li>{icon(i)}<span>{esc(t)}</span></li>' for i, t in A["caps"])
    def uc(u, cls):
        i, who, need, give = u
        return f"""<li class="{cls}">
  {icon(i, "ic ic-lg")}
  <h3>{esc(who)}</h3>
  <p class="uc-need">{esc(need)}</p>
  <p class="uc-give">{esc(give)}</p>
</li>"""
    feat, more = A["uses"][:3], A["uses"][3:]
    assert [u[0] for u in feat] == ["hospital", "scales", "shield"]
    uses = (f'<ul class="ucs ucs-feat">{"".join(uc(u, "uc uc-feat") for u in feat)}</ul>'
            f'<ul class="ucs ucs-more">{"".join(uc(u, "uc") for u in more)}</ul>')
    body = biz_head("ALICE", "ALICE &middot; Private AI", A["h1"], A["lead"], alice_art())
    body += f'<section class="cap-band" aria-label="Capabilities"><div class="wrap"><ul class="caps">{caps}</ul></div></section>'
    body += biz_section("Built for places where <em>data cannot leave.</em>", uses, "Target use cases", "uc-h")
    body += biz_section("How we engage", engage_flow(A["engage"]) + f'<p class="stage-line">{esc(A["stage"])}</p>', None, "en-h", "alt")
    body += cta_band(C.BRIEFING["title"], esc(C.BRIEFING["body"]))
    page("/alice/", A["title"], A["lead"], body, active="/alice/")


def cis_page(labs):
    X = C.CIS
    by = {l["slug"]: l for l in labs}
    links = "".join(f'<li><a class="ext" href="{esc(u)}">{esc(t)}</a></li>' for t, u in X["cis2_links"])
    links += '<li><a href="/standard/">Our test standard</a></li>'
    chips = "".join(lab_chip(by[s]) for s in X["cis2_labs"])
    cis2 = f"""<div class="cis2-grid">
  <div>
    <p class="cis2-p">{esc(X["cis2"])}</p>
    <ul class="link-list">{links}</ul>
    {video_card()}
  </div>
  <div>
    <p class="hq-k">The labs behind it</p>
    <ul class="lab-chips">{chips}</ul>
    <p class="more"><a href="/labs/?q=1">All labs on this question {ARROW}</a></p>
  </div>
</div>"""
    cis3 = f"""<section class="cis3" id="cis-3" aria-labelledby="cis3-h">
  <div class="wrap cis3-grid">
    <div class="cis3-lock" aria-hidden="true">{icon("lock", "ic")}</div>
    <div>
      <p class="kicker">{esc(X["cis3_kicker"])}</p>
      <h2 class="cis3-h" id="cis3-h">{esc(X["cis3_h"])}</h2>
      <p class="cis3-b">{esc(X["cis3_body"])}</p>
      <div class="cta-row"><a class="btn btn-lg btn-inv" href="{C.mailto(X["cis3_subject"])}">{esc(X["cis3_cta"])} {ARROW}</a></div>
    </div>
  </div>
</section>"""
    uses = []
    for i, t, b, ls in X["uses"]:
        lk = ""
        if ls:
            lk = '<p class="uc-labs">' + " ".join(f'<a href="/labs/{s}/">{by[s]["code"]} &middot; {esc(by[s]["title"])}</a>' for s in ls) + "</p>"
        uses.append(f'<li class="uc">{icon(i, "ic ic-lg")}<h3>{esc(t)}</h3><p class="uc-give">{esc(b)}</p>{lk}</li>')
    body = biz_head("CIS", "CIS &middot; Checkable inference", X["h1"], X["lead"], machines_figure(),
                    [("#cis-2", "CIS-2 &middot; open standard", "btn btn-lg"), ("#cis-3", "CIS-3 &middot; LLM edition", "btn btn-ghost")])
    body += biz_section("CIS-2 &middot; <em>open standard</em>", cis2, "Apache-2.0", "cis-2", "cis2-sec")
    body += cis3
    body += biz_section(esc(X["uses_title"]), f'<ul class="ucs ucs-3">{"".join(uses)}</ul>', "Licensing use cases", "fx-h")
    body += cta_band(X["cta"], esc(X["licensing"]))
    page("/cis/", X["title"], X["lead"], body, active="/cis/")


def ops_art():
    rows = "".join(
        f'<li class="lg-{st}">{icon(i)}<span class="lg-t">{esc(t)}</span><span class="lg-s">{icon("gate" if st == "gate" else "check", "ic ic-xs")}{esc(s)}</span></li>'
        for i, t, s, st in C.OPS["log"])
    return f"""<figure class="oplog">
  <div class="mf-bar"><span>Workflow log</span><span class="mf-tag">Example</span></div>
  <ol>{rows}</ol>
  <figcaption>Routine steps run and are logged. Money, outreach and anything public wait for a named person.</figcaption>
</figure>"""


def operations_page(labs):
    O = C.OPS
    proof = f"""<section class="proof-dark" aria-labelledby="pf-h">
  <div class="wrap">
    <div class="pd-grid">
      <div>
        <p class="kicker">{esc(O["proof_kicker"])}</p>
        <h2 class="pd-title" id="pf-h">{esc(O["proof_h"])}</h2>
        <p class="pd-body">{esc(O["proof_body"])}</p>
      </div>
      {ops_loop()}
    </div>
    <ul class="pd-stats">
      <!-- {C.LEDGER_SOURCE} -->
      <li><span class="ps-big">{C.LEDGER_REGISTERED}</span><span class="ps-lab">registered experiments on our public, hash-chained ledger</span></li>
      <li><span class="ps-big">{len(labs)}</span><span class="ps-lab">published labs, each with sources and verbatim quotes</span></li>
      <li class="pd-site"><span class="ps-lab">{esc(O["site_fact"])}</span></li>
    </ul>
    <p class="pd-links"><a href="/standard/">Our test standard {ARROW}</a><a href="/labs/">All {len(labs)} labs {ARROW}</a><a href="/operations/how-we-run/">How this lab is run {ARROW}</a></p>
  </div>
</section>"""
    auto = "".join(f'<li class="uc">{icon(i, "ic ic-lg")}<h3>{esc(t)}</h3><p class="uc-give">{esc(b)}</p></li>' for i, t, b in O["automate"])
    std = "".join(f'<li><span class="os-n">{n + 1:02d}</span>{icon(i)}<h3>{esc(t)}</h3><p>{esc(b)}</p></li>' for n, (i, t, b) in enumerate(O["standard"]))
    body = biz_head("Operations", "Autonomous Operations &middot; Services", O["h1"], O["lead"], ops_art(),
                    [(C.NAV_CTA[0], C.NAV_CTA[1], "btn btn-lg"), ("#pf-h", "See the proof", "btn btn-ghost")])
    body += proof
    body += biz_section("What we automate", f'<ul class="ucs ucs-4">{auto}</ul>', None, "au-h")
    body += biz_section("Our operating standard", f'<ol class="ostd">{std}</ol>', None, "os-h", "alt")
    body += biz_section("How we engage", engage_flow(O["engage"]) + f'<p class="stage-line">{esc(O["models"])}</p>', None, "oe-h")
    body += cta_band(C.BRIEFING["title"], esc(C.BRIEFING["body"]))
    page("/operations/", O["title"], O["lead"], body, active="/operations/")


HOW = [
    ("What the AI operator does on its own", """<ul>
<li>Runs registered experiments on the lab's machines and on free cloud GPU time.</li>
<li>Keeps the experiment ledger and the lab board.</li>
<li>Drafts documents, emails and grant applications for human review.</li>
<li>Opens pull requests.</li>
<li>Watches the inbox and answers questions from the company's own records.</li>
<li>Keeps the machines fed and healthy.</li></ul>"""),
    ("What never happens without a human", """<ul>
<li>Spending or moving money.</li>
<li>Legal commitments and signatures.</li>
<li>Logins, credentials and security settings.</li>
<li>Sending email to a new named contact.</li>
<li>Deploying this website.</li>
<li>Merging anything into the public specification repository without review.</li>
<li>Publishing a claim that is not in the ledger.</li></ul>"""),
    ("How every action is logged", """<p>Two records. A private operations log lists every send, push, deploy and decision, with ids. The public experiment ledger lives in the <a class="ext" href="https://github.com/Aefinity-AI/cis2-spec/tree/main/ledger">cis2-spec repository</a>; it is hash-chained, and a timestamp proof made with OpenTimestamps (<code>LEDGER.tsv.ots</code>) dates the file as a whole. The private log is not public.</p>"""),
    ("Who is accountable", """<p>Justin Thompson, Chief Executive Officer, for everything the operator does.</p>"""),
    ("Which model", """<!-- JUSTIN REVIEW: names the model vendor; the site guard normally bans it -->
<p data-model-statement>The lab's operator is a commercially licensed frontier language model, used under its provider's standard terms. The model's provider is not a partner of AEFINITY AI INC. and has not endorsed this work.</p>"""),
    ("Incidents", """<!-- JUSTIN REVIEW -->
<p><strong>2026-10-15</strong> &mdash; Email sent from a founder's account by a second AI assistant, without the operator's review, overstated our standing: it described intended engagements as existing ones and a verification by an outside party that had not taken place. A correction went to the NIST recipient the same day; the other messages are listed in the public errata of the cis2-spec repository (docs/ERRATA.md). That assistant's access is being restricted.</p>"""),
]


def how_we_run_page():
    secs = "".join(f'<h3>{esc(t)}</h3>{b}' for t, b in HOW)
    body = f"""{simple_head("How we run", "Autonomous Operations", "How this lab is <em>run.</em>", '<p class="lede">What the AI operator does, what needs a person, and how it is recorded.</p>')}
<section class="section" aria-labelledby="how-t">
  <div class="wrap prose">
    <h2 id="how-t">How this lab is run</h2>
    {secs}
    <p><a href="/operations/">Back to Autonomous Operations {ARROW}</a></p>
  </div>
</section>"""
    page("/operations/how-we-run/", "How this lab is run", "What the AI operator does on its own, what never happens without a human, how actions are logged, and who is accountable.", body, active="/operations/")


def contact_page():
    K = C.CONTACT
    cards = []
    for i, t, line, subj, extra in K["cards"]:
        ex = f'<a class="cc-extra" href="{extra[0]}">{esc(extra[1])} {ARROW}</a>' if extra else ""
        cards.append(f"""<li class="ccard">
  {icon(i, "ic ic-lg")}
  <h2 class="cc-t">{esc(t)}</h2>
  <p>{esc(line)}</p>
  <a class="btn" href="{C.mailto(subj)}">Email about this {ARROW}</a>
  {ex}
</li>""")
    body = f"""<section class="biz-head contact-head">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="/">Home</a></li><li aria-current="page">Contact</li></ol></nav>
    <p class="kicker kicker-acc">Contact</p>
    <h1 class="biz-h">{K["h1"]}</h1>
    <p class="biz-lead">{esc(K["lead"])}</p>
    <div class="direct">
      <a class="dl" href="mailto:{C.EMAIL}">{icon("mail", "ic ic-lg")}<span class="dl-k">Email</span><span class="dl-v">{C.EMAIL}</span></a>
      <a class="dl" href="tel:{C.PHONE_TEL}">{icon("phone", "ic ic-lg")}<span class="dl-k">Phone</span><span class="dl-v">{C.PHONE_DISPLAY}</span></a>
      <div class="dl dl-static">{icon("pin", "ic ic-lg")}<span class="dl-k">Location</span><span class="dl-v">{C.CITY}</span></div>
    </div>
  </div>
</section>
<section class="bsec" aria-labelledby="cc-h">
  <div class="wrap"><div class="bs-head"><p class="kicker kicker-acc">Topics</p><h2 class="bs-title" id="cc-h">Pick a topic, or just write.</h2></div><ul class="ccards">{"".join(cards)}</ul></div>
</section>"""
    page("/contact/", K["title"], K["lead"], body, active="/contact/")


def commercial_guard():
    site_re = re.compile(r"\b(" + "|".join(C.SITE_BANNED) + r")\b", re.I)
    biz_re = re.compile(r"\b(" + "|".join(C.COMMERCIAL_BANNED) + r")", re.I)
    biz_pages = {"alice/index.html", "cis/index.html", "operations/index.html", "contact/index.html"}
    for rel in WRITTEN:
        if not rel.endswith(".html"):
            continue
        t = (PUBLIC / rel).read_text()
        bare = re.sub(r"<blockquote.*?</blockquote>", "", t, flags=re.S)
        if rel == "operations/how-we-run/index.html":  # the mandated model statement names the vendor
            bare = re.sub(r"<p data-model-statement>.*?</p>", "", bare, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)\b.*?</\1>", "", bare, flags=re.S)))
        m = site_re.search(text)
        assert not m, (rel, m.group(0))
        if rel in biz_pages or rel == "index.html":
            # The shared footer links the public "Design Partner Adoption Path"
            # document by its title; the guard covers the page content.
            region = html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<footer\b.*?</footer>", "", re.sub(r"<(script|style)\b.*?</\1>", "", bare, flags=re.S), flags=re.S)))
            if rel == "index.html":  # the hero, offerings and operations bands
                a = t.index('<section class="hero"')
                b = t.index('<section class="section"', a)
                region = html.unescape(re.sub(r"<[^>]+>", " ", t[a:b]))
            m = biz_re.search(region)
            assert not m, (rel, m.group(0), region[max(0, m.start() - 60):m.end() + 60])
    # CIS-3 is named with its purpose only: no numbers beyond its own name.
    t = (PUBLIC / "cis/index.html").read_text()
    sec = t[t.index('<section class="cis3"'):t.index("</section>", t.index('<section class="cis3"'))]
    sec_text = re.sub(r"<[^>]+>", " ", sec)
    sec_text = re.sub(r"CIS-[23]", "", sec_text).replace("CIS-3%20", "")
    assert not re.search(r"\d", re.sub(r"mailto:[^\"]+", "", sec_text)), "CIS-3 section carries a number"


VIDEO_SRC = ROOT / "static" / "media" / "cis2"
VIDEO_FILES = ("cis2-explainer.mp4", "cis2-explainer.webm", "poster.jpg", "captions.vtt")
VIDEO_TRANSCRIPT = ROOT / "content" / "cis2-transcript.md"
GH = "https://github.com/Aefinity-AI/cis2-spec/blob/main/"
VIDEO_SOURCES = [
    ("What CIS-2 is, what it pins, and the order-of-addition point", [("README", GH + "README.md"), ("Specification v0.3b", GH + "docs/CIS2_SPEC_v0.3b.md"), ("Apache-2.0 licence", GH + "LICENSE")]),
    ("The receipt: one SHA-256 stream over the weights, prompt and every step's full logit vector", [("Specification v0.3b, section 12", GH + "docs/CIS2_SPEC_v0.3b.md")]),
    ("Pinned test vector and digest (SmolLM2-135M, 16 greedy tokens)", [("EXPECTED_DIGESTS.md", GH + "EXPECTED_DIGESTS.md")]),
    ("Builds from the spec text alone, and the write-up error they caught", [("README", GH + "README.md"), ("C clean-room result", GH + "docs/E15j_CLEANROOM_C_RESULT.md")]),
    ("Same digest on other chips: cloud CPU run and Tesla P100 GPU", [("Cloud CPU self-check", GH + "docs/results/2026-09-25-LIGHTNING-STUDIO-SELFCHECK.md"), ("GPU result", GH + "docs/GPU_RESULT.md")]),
    ("One-command self-check; a changed model file is refused", [("README", GH + "README.md"), ("Continuous validation", GH + "docs/results/2026-09-27-CONTINUOUS-VALIDATION.md")]),
    ("Corruption tests on a separate, larger model (our own runs)", [("Bit-flip head-to-head", GH + "docs/results/2026-09-13-BITFLIP-HEADTOHEAD.md"), ("Embedding-row head-to-head", GH + "docs/results/2026-09-17-EMBED-SUBSTITUTION-HEADTOHEAD.md")]),
    ("Limits, and the public challenge", [("README", GH + "README.md"), ("CHALLENGE.md", GH + "CHALLENGE.md"), ("Hall of Divergence", GH + "HALL-OF-DIVERGENCE.md")]),
    ("Where to get it", [("CIS-2 on GitHub", "https://github.com/Aefinity-AI/cis2-spec"), ("Conformance vectors on Hugging Face", "https://huggingface.co/datasets/aefinityAIINC/cis2-conformance")]),
]


def video_transcript_html():
    out, para = [], []
    def flush():
        if para:
            out.append("<p>" + esc(" ".join(para)) + "</p>")
            para.clear()
    for line in VIDEO_TRANSCRIPT.read_text().splitlines():
        if line.startswith("# "):
            continue
        if line.startswith("Links:"):
            flush()
            continue
        m = re.match(r"## (.+?)\s+\((\d+:\d\d)\)\s*$", line)
        if m:
            flush()
            out.append(f'<h3 class="vt-h">{esc(m.group(1))} <span class="vt-t">{m.group(2)}</span></h3>')
        elif line.strip():
            para.append(line.strip())
        else:
            flush()
    flush()
    return "".join(out)


def video_card(cls="video-cta"):
    return f"""<a class="{cls}" href="/cis2/explainer/">
  <span class="vc-thumb"><img src="/media/cis2/poster.jpg" alt="" width="320" height="180" loading="lazy"><span class="vc-play" aria-hidden="true">{icon("play", "ic")}</span></span>
  <span class="vc-text"><span class="vc-k">Video &middot; 4 minutes</span><span class="vc-t">Watch the 4-minute explainer {ARROW}</span><span class="vc-d">What CIS-2 checks, how anyone can verify it, and what it does not prove.</span></span>
</a>"""


def video_page():
    for f in VIDEO_FILES:
        out = PUBLIC / "media" / "cis2" / f
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(VIDEO_SRC / f, out)
        WRITTEN.append(f"media/cis2/{f}")
    src = "".join(f'<li><span class="vs-c">{esc(c)}</span> ' + ", ".join(f'<a class="ext" href="{esc(u)}">{esc(t)}</a>' for t, u in ls) + "</li>" for c, ls in VIDEO_SOURCES)
    head = simple_head("CIS-2 explainer", "CIS-2 &middot; Video", "CIS-2 in four minutes",
                       '<p class="lede">A 4-minute explainer: what CIS-2 checks, how anyone can verify it, and what it does not prove.</p>')
    body = f"""{head}
<section class="wrap video-sec" aria-labelledby="vid-h">
  <h2 class="sr-only" id="vid-h">The video</h2>
  <div class="video-frame">
    <video controls preload="metadata" playsinline poster="/media/cis2/poster.jpg" width="1280" height="720">
      <source src="/media/cis2/cis2-explainer.webm" type="video/webm">
      <source src="/media/cis2/cis2-explainer.mp4" type="video/mp4">
      <track kind="captions" srclang="en" label="English" src="/media/cis2/captions.vtt" default>
      Your browser cannot play this video. The full transcript is below.
    </video>
  </div>
  <p class="video-credit">Narration: Piper TTS, LJ Speech voice (public domain). The voice is synthetic.</p>
  <p class="more"><a href="/cis/#cis-2">Back to CIS-2 {ARROW}</a></p>
</section>
<section class="wrap video-sec" aria-labelledby="tr-h">
  <h2 id="tr-h">Transcript</h2>
  <div class="vt prose-col">{video_transcript_html()}</div>
</section>
<section class="wrap video-sec" aria-labelledby="src-h">
  <h2 id="src-h">Sources for every claim</h2>
  <p class="ex-sub-lede">Every link is public. The corruption tests were run by us on a separate, larger model, and no outside party has reproduced CIS-2 yet.</p>
  <ul class="vsrc">{src}</ul>
</section>"""
    page("/cis2/explainer/", "CIS-2 explainer video", "A 4-minute explainer: what CIS-2 checks, how anyone can verify it, and what it does not prove.",
         body, active="/cis/", og_image="/media/cis2/poster.jpg")


def sitemap(labs):
    # /pilot is served from public/pilot.html; the host maps the extensionless path.
    urls = ["/", "/mission/", "/questions/", "/labs/"] + [f"/labs/{l['slug']}/" for l in labs] + ["/learned/", "/standard/", "/projects/", "/pilot",
            "/alice/", "/cis/", "/cis2/explainer/", "/operations/", "/operations/how-we-run/", "/contact/"]
    body = "".join(f"  <url><loc>{C.SITE}{u}</loc></url>\n" for u in urls)
    write("/sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}</urlset>\n')
    return urls


# --------------------------------------------------------------------------
def main():
    j, data, labs = load()
    check_figures(labs)
    check_proof(labs)
    # assets
    (PUBLIC / "assets").mkdir(parents=True, exist_ok=True)
    for name in ("site.css", "site.js"):
        shutil.copyfile(ASSETS_SRC / name, PUBLIC / "assets" / name)
        WRITTEN.append(f"assets/{name}")
    home(labs, data)
    mission_page(labs, data)
    questions_page(labs, data)
    labs_index(labs, data)
    for l in labs:
        lab_page(l, labs, data)
    standard_page(labs, data)
    learned_page(labs, data)
    projects_page(labs, data)
    pilot_page()
    alice_page(labs)
    cis_page(labs)
    video_page()
    operations_page(labs)
    how_we_run_page()
    contact_page()
    not_found()
    urls = sitemap(labs)
    # remove stale files from earlier builds
    keep = set(WRITTEN) | KEEP
    for f in sorted(PUBLIC.rglob("*")):
        if f.is_file() and str(f.relative_to(PUBLIC)) not in keep:
            f.unlink()
    for d in sorted((p for p in PUBLIC.rglob("*") if p.is_dir()), reverse=True):
        if not any(d.iterdir()):
            d.rmdir()
    # final guard: no nickname outside quote blocks, no held-back file links
    for rel in WRITTEN:
        if not rel.endswith(".html"):
            continue
        t = (PUBLIC / rel).read_text()
        assert not any(h in t for h in HELD_BACK_FILES), rel
        bare = re.sub(r"<blockquote.*?</blockquote>", "", t, flags=re.S)
        m = re.search(C.NICKNAME_RE, bare)
        assert not m, (rel, m.group(0))
    commercial_guard()
    site_re = re.compile(r"\b(" + "|".join(C.SITE_BANNED) + r")\b", re.I)
    for rel in WRITTEN:  # the shareable pictures carry the same text as the pages
        if rel.endswith(".svg"):
            m = site_re.search(html.unescape(re.sub(r"<style>.*?</style>|<[^>]+>", " ", (PUBLIC / rel).read_text(), flags=re.S)))
            assert not m, (rel, m.group(0))
    pages = sum(1 for r in WRITTEN if r.endswith(".html"))
    print(f"built {pages} pages, {len(urls)} sitemap URLs, {len(WRITTEN)} files")


if __name__ == "__main__":
    main()
