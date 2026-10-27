#!/usr/bin/env python3
"""Dựng 1 file HTML giáo án từ lesson.json.

    python3 build_lesson.py bai.json -o bai.html

- Mọi chữ Hán đều được gắn pinyin phía trên (cỡ 2/3 chữ Hán) — tự động bằng pypinyin + lexicon.json,
  ghi đè thủ công bằng {汉字|pin yin}.
- Hình minh hoạ = emoji hoạt hình Twemoji (CC-BY 4.0), tải 1 lần về assets/icons rồi nhúng thẳng vào HTML.
- Từ vựng, hội thoại, bài luyện tập BẮT BUỘC có hình; thiếu là build báo lỗi (trừ khi --lenient).
"""
import argparse, html, json, os, re, sys, unicodedata, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
VENV_PY = ROOT / ".venv" / "bin" / "python"

try:
    from pypinyin import pinyin, Style
except ImportError:
    if VENV_PY.exists() and Path(sys.executable).resolve() != VENV_PY.resolve() and not os.environ.get("_GA_REEXEC"):
        os.environ["_GA_REEXEC"] = "1"
        os.execv(str(VENV_PY), [str(VENV_PY)] + sys.argv)
    sys.exit("Thiếu pypinyin. Chạy:  bash %s/setup.sh" % HERE)

LEX = json.loads((HERE / "lexicon.json").read_text("utf-8"))
WORDS = LEX["words"]
SINGLE = {k: v for k, v in LEX["single"].items() if k not in "着过"}
ER_REAL = set(LEX["er_real"])
POLY = set(LEX["polyphone_check"])
MAXW = max(len(w) for w in WORDS)
HAN = r"一-鿿㐀-䶿"
HAN_RUN = re.compile("([%s]+)" % HAN)
TOKEN = re.compile(r"(~~[^~]+~~|\{\{[^{}]+\}\}|\*\*|\{[^{}|]+\|[^{}]+\}|\[\[[^\]]+\]\]|_{3,}|\n)")
ICON_DIR = ROOT / "assets" / "icons"
CDN = "https://cdn.jsdelivr.net/gh/jdecked/twemoji@15.1.0/assets/svg/%s.svg"

WARN, ERR = [], []
POLY_SEEN = {}
ICONS = {}  # name -> (viewBox, inner)


# ---------------------------------------------------------------- pinyin
def tone_of(syl):
    for c in unicodedata.normalize("NFD", syl):
        t = {"̄": 1, "́": 2, "̌": 3, "̀": 4}.get(c)
        if t:
            return t
    return 5


def syllables(run):
    """Pinyin cho 1 cụm chữ Hán liên tục -> list (mỗi chữ 1 âm tiết)."""
    orig = [s[0] for s in pinyin(run, style=Style.TONE, errors="default")]
    syl = list(orig)
    locked = [False] * len(run)
    i = 0
    while i < len(run):  # lexicon: khớp từ dài nhất
        for n in range(min(MAXW, len(run) - i), 1, -1):
            w = run[i:i + n]
            if w in WORDS and len(WORDS[w].split()) == n:
                syl[i:i + n] = WORDS[w].split()
                for k in range(i, i + n):
                    locked[k] = True
                i += n - 1
                break
        i += 1
    for i, ch in enumerate(run):
        if locked[i]:
            continue
        nxt = tone_of(orig[i + 1]) if i + 1 < len(run) else None
        prev = run[i - 1] if i else ""
        nch = run[i + 1] if i + 1 < len(run) else ""
        if ch in SINGLE:
            syl[i] = SINGLE[ch]
        elif ch == "个" and prev and prev in "一二三四五六七八九十两几这那哪每多半":
            syl[i] = "ge"
        elif ch == "儿" and prev and (prev + "儿") not in ER_REAL:
            syl[i] = "r"
        elif ch == "不" and nxt == 4:
            syl[i] = "bú"
        elif ch == "一" and nxt:
            if prev and prev in "十二三四五六七八九零〇第周期":
                pass
            elif nch in "月号日" or (nch == "点" and run[i + 2:i + 3] != "儿"):
                pass
            elif nxt == 4:
                syl[i] = "yí"
            else:
                syl[i] = "yì"
        if ch in POLY and ch not in SINGLE:
            POLY_SEEN.setdefault(ch, set()).add(run)
    return syl


def ruby_chars(zh, syl):
    return "".join("<ruby>%s<rt>%s</rt></ruby>" % (html.escape(c), html.escape(s)) for c, s in zip(zh, syl))


def ruby_override(zh, py):
    s = py.split()
    if len(s) == len(zh):
        return '<span class="nw">%s</span>' % ruby_chars(zh, s)
    return '<ruby class="grp">%s<rt>%s</rt></ruby>' % (html.escape(zh), html.escape(py))


def annotate(text):
    out = []
    for part in HAN_RUN.split(text):
        if not part:
            continue
        if HAN_RUN.fullmatch(part):
            out.append('<span class="nw">%s</span>' % ruby_chars(part, syllables(part)))
        else:
            out.append(html.escape(part))
    return "".join(out)


def rich(s):
    """Markup: **nhấn**, ___ chỗ trống, {汉字|pin yin} ghi đè pinyin, \\n xuống dòng."""
    if s is None:
        return ""
    out, bold = [], False
    for part in TOKEN.split(str(s)):
        if part == "":
            continue
        if part == "**":
            out.append("</b>" if bold else '<b class="hl">')
            bold = not bold
        elif part == "\n":
            out.append("<br>")
        elif part.startswith("~~"):
            out.append('<u class="sw">%s</u>' % rich(part[2:-2]))
        elif part.startswith("{{"):
            alts = part[2:-2]
            w = max(len(x) for x in alts.split("|"))
            out.append('<input class="gi" type="text" autocomplete="off" autocapitalize="off" spellcheck="false" data-a="%s" style="width:%.1fem">' % (html.escape(alts), max(3.2, w * 1.05 + 1.6)))
        elif part.startswith("[["):
            out.append('<span class="bl"><span class="a">%s</span></span>' % rich(part[2:-2]))
        elif part.startswith("___"):
            out.append('<span class="blank"></span>')
        elif part.startswith("{") and "|" in part:
            zh, py = part[1:-1].split("|", 1)
            out.append(ruby_override(zh, py))
        else:
            out.append(annotate(part))
    if bold:
        out.append("</b>")
    res = "".join(out)
    # dính dấu câu vào cụm chữ Hán đứng trước để không rơi xuống dòng riêng
    return re.sub(r'(<span class="nw">(?:(?!</span>).)*)</span>([！？。，、；：）”’…!?.,;:)]+)', r'\1\2</span>', res)


def plain(s):
    """Văn bản thô cho nút nghe (TTS)."""
    s = re.sub(r"\{([^{}|]+)\|[^{}]+\}", r"\1", str(s or "")).replace("**", "")
    s = re.sub(r"\[\[([^\]]+)\]\]", r"\1", s).replace("~~", "")
    s = re.sub(r"\{\{([^{}|]+)[^{}]*\}\}", r"\1", s)
    s = re.sub(r"_{3,}", "…", s)
    return s if HAN_RUN.search(s) else ""


def zh(s, cls="md", tag="div"):
    return '<%s class="zh %s">%s</%s>' % (tag, cls, rich(s), tag)


def say_btn(s):
    p = plain(s).strip()
    return '<button class="btn say" data-say="%s" title="Nghe" aria-label="Nghe">🔊</button>' % html.escape(p) if p else ""


# ---------------------------------------------------------------- hình
def icon_name(tok):
    cps = [ord(c) for c in tok]
    if 0x200D not in cps:
        cps = [c for c in cps if c != 0xFE0F]
    return "-".join("%x" % c for c in cps)


def load_icon(tok):
    name = icon_name(tok)
    if name in ICONS:
        return name
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    f = ICON_DIR / (name + ".svg")
    if not f.exists():
        cands = [name]
        alt = "-".join("%x" % ord(c) for c in tok)
        if alt != name:
            cands.append(alt)
        for c in cands:
            try:
                with urllib.request.urlopen(CDN % c, timeout=20) as r:
                    f.write_bytes(r.read())
                break
            except Exception:
                continue
    if not f.exists():
        WARN.append("Không tải được hình cho emoji %r (%s)" % (tok, name))
        return None
    svg = f.read_text("utf-8")
    m = re.search(r'<svg[^>]*viewBox="([^"]+)"[^>]*>(.*)</svg>', svg, re.S)
    ICONS[name] = (m.group(1), m.group(2)) if m else ("0 0 36 36", "")
    return name


def pic(img, size="md", tone=""):
    """img = các token cách nhau bằng dấu cách. Token emoji -> hình; token '+','=','→' -> dấu; '#chữ' -> nhãn."""
    if not img:
        return ""
    parts = []
    for tok in str(img).split():
        if tok[0] in "#":
            parts.append('<span class="lab">%s</span>' % rich(tok[1:]))
        elif tok.isascii() or tok in ("→", "←", "↔"):
            parts.append('<span class="op">%s</span>' % html.escape(tok))
        else:
            n = load_icon(tok)
            parts.append('<svg class="ico" viewBox="%s" role="img" aria-hidden="true"><use href="#e-%s"/></svg>' % (ICONS[n][0], n)
                         if n else '<span class="op">%s</span>' % html.escape(tok))
    return '<span class="pic %s %s">%s</span>' % (size, tone, "".join(parts))


def need(img, where, strict=True):
    if not img or not str(img).strip():
        (ERR if strict else WARN).append("Thiếu hình minh hoạ: " + where)


# ---------------------------------------------------------------- các phần
def sec(id_, no, title, extra, body):
    sm = "<small>%s</small>" % html.escape(extra) if extra else ""
    return '<section class="sec" id="%s"><h2><span class="no">%s</span>%s %s</h2>%s</section>' % (id_, no, title, sm, body)


def build_hero(d):
    unit = int(d.get("unit", 0))
    goals = "".join(
        '<div class="goal">%s<div>%s</div></div>' % (pic(g.get("img", ""), "sm", "warm"), rich(g["text"]))
        for g in d.get("goals", []))
    refs = "".join("<span>📖 %s: %s</span>" % (html.escape(k), html.escape(v)) for k, v in (d.get("refs") or {}).items())
    plan = d.get("plan") or ["**Buổi 1** · Từ vựng + ngữ pháp", "**Buổi 2** · Hội thoại + lỗi thường gặp", "**Buổi 3** · Luyện tập + hoạt động nói"]
    anchors = ["#s-vocab", "#s-dialogue", "#s-practice"]
    plan_html = "".join('<a href="%s">%s</a>' % (a, rich(p).replace('<b class="hl">', "<b>")) for a, p in zip(anchors, plan))
    hero = ('<header class="hero"><div><span class="unit">UNIT %02d · %s</span>'
            '<h1><div class="zh">%s</div><div class="vtitle">%s</div></h1>'
            '<div class="course">%s</div></div><div>%s</div></header>') % (
        unit, html.escape(d.get("level", "Sơ cấp")), rich(d["title_zh"]), html.escape(d["title_vi"]),
        html.escape(d.get("course", "Giao tiếp cấp tốc sơ cấp")), pic(d.get("hero_img", ""), "xl"))
    need(d.get("hero_img"), "hero_img", False)
    body = '<div class="goals">%s</div><div class="refs">%s</div><div class="plan">%s</div>' % (goals, refs, plan_html)
    return hero + sec("s-goal", "🎯", "Hôm nay bạn sẽ nói được", "", body)


def build_vocab(d, strict):
    items, cur = [], None
    for i, v in enumerate(d.get("vocab", []), 1):
        need(v.get("img"), "vocab #%d %s" % (i, v.get("zh")), strict)
        if v.get("group") and v["group"] != cur:
            cur = v["group"]
            items.append('<div class="vgroup">%s</div>' % rich(cur))
        chips = "".join(filter(None, [
            '<span class="chip star" title="Từ HSK 3+">★ HSK3+</span>' if v.get("hsk3") else "",
            '<span class="chip">%s</span>' % html.escape(v["pos"]) if v.get("pos") else ""]))
        items.append(
            '<div class="vcard">%s%s%s<div class="meaning">%s</div><div class="chips">%s</div>%s</div>' % (
                say_btn(v["zh"]), pic(v.get("img", ""), "md"), zh(v["zh"], "xl"), rich(v["vi"]), chips,
                '<div class="tip">💡 %s</div>' % rich(v["tip"]) if v.get("tip") else ""))
    return sec("s-vocab", 1, "Từ vựng", "%d từ" % len(d.get("vocab", [])), '<div class="vgrid">%s</div>' % "".join(items))


def table_html(t):
    head = "".join("<th>%s</th>" % rich(h) for h in t["headers"])
    rows = "".join("<tr>%s</tr>" % "".join('<td><span class="zh sm">%s</span></td>' % rich(c) for c in r) for r in t["rows"])
    return '<table class="tbl"><thead><tr>%s</tr></thead><tbody>%s</tbody></table>' % (head, rows)


def build_grammar(d, strict):
    out = []
    for i, g in enumerate(d.get("grammar", []), 1):
        exs = []
        for j, e in enumerate(g.get("examples", []), 1):
            need(e.get("img"), "grammar #%d ví dụ %d" % (i, j), strict)
            exs.append('<div class="ex">%s<div class="t">%s<div class="vi">%s</div></div>%s</div>' % (
                pic(e.get("img", ""), "md", "pale"), zh(e["zh"], "md"), rich(e["vi"]), say_btn(e["zh"])))
        out.append('<div class="card gpt"><h3><span class="n">%d</span>%s</h3><div class="formula"><div class="zh">%s</div></div>%s%s%s</div>' % (
            i, rich(g["title"]), rich(g["formula"]), "".join(exs),
            table_html(g["table"]) if g.get("table") else "",
            '<div class="note">%s</div>' % rich(g["note"]) if g.get("note") else ""))
    c = d.get("culture")
    if c:
        out.append('<div class="card culture">%s<div><h4>🏮 Góc văn hoá · %s</h4><div>%s</div></div></div>' % (
            pic(c.get("img", ""), "lg", "warm"), rich(c["title"]), rich(c["text"])))
    n = len(d.get("grammar", []))
    return sec("s-grammar", 2, "Ngữ pháp", "%d điểm" % n, "".join(out))


def build_dialogue(d, strict):
    dl = d["dialogue"]
    need(dl.get("scene_img"), "dialogue.scene_img", strict)
    sp = dl.get("speakers") or {"A": {"emoji": "👩", "name": "A"}, "B": {"emoji": "👨", "name": "B"}}
    lines = []
    for i, l in enumerate(dl["lines"], 1):
        who = l["who"]
        s = sp.get(who, {"emoji": "🙂", "name": who})
        react = ""
        lines.append(
            '<div class="line %s"><div class="av">%s<span>%s</span></div><div class="bub"><div class="row">%s%s</div><div class="vi">%s</div></div>%s</div>' % (
                who, pic(s["emoji"], "md"), html.escape(s.get("name", who)), zh(l["zh"], "md"), say_btn(l["zh"]),
                rich(l["vi"]), ('<div class="react">%s</div>' % pic(l["img"], "sm", "warm")) if l.get("img") else react))
    scene = '<div class="card scene">%s<div><b>Tình huống:</b> %s</div></div>' % (pic(dl.get("scene_img", ""), "lg"), rich(dl["situation"]))
    bar = ('<div class="sbar"><button class="btn" id="btn-play">▶ Nghe cả hội thoại</button>'
           '<span class="chip o">%s</span></div>') % html.escape(dl.get("drill", "Shadowing 2 lượt: nghe → đọc theo ngay"))
    return sec("s-dialogue", 3, "Hội thoại", "", scene + bar + '<div class="dlg">%s</div>' % "".join(lines))


def build_mistakes(d, strict):
    cards = []
    for i, m in enumerate(d.get("mistakes", []), 1):
        need(m.get("img"), "mistakes #%d" % i, strict)
        cards.append(
            '<div class="card mist"><div class="w"><span class="sym">✗</span>%s</div><div class="r"><span class="sym">✓</span>%s</div>'
            '<div class="why">%s<div>%s</div></div></div>' % (zh(m["wrong"], "md"), zh(m["right"], "md"), pic(m.get("img", ""), "sm", "pale"), rich(m["why"])))
    return sec("s-mistakes", 4, "Lỗi thường gặp", "người Việt hay sai", '<div class="mgrid">%s</div>' % "".join(cards))


def q_html(n, it, where, strict):
    need(it.get("img"), where, strict)
    opts = '<div class="opts">%s</div>' % "".join("<span>%s</span>" % rich(o) for o in it["opts"]) if it.get("opts") else ""
    ans = '<div class="ans">%s</div>' % rich(it["a"]) if it.get("a") else ""
    hint = '<div class="hint">👆 chạm để xem đáp án</div>' if it.get("a") else ""
    return '<div class="card q"><span class="no">%d</span>%s<div class="body"><div class="qt">%s</div>%s%s%s</div></div>' % (
        n, pic(it.get("img", ""), "md", "pale"), rich(it["q"]), opts, hint, ans)


def build_practice(d, strict):
    p = d["practice"]
    heads = [("l1", "Cấp 1 · Tri thức", "Đáp án cố định — củng cố", "level1"),
             ("l2", "Cấp 2 · Bán giao tiếp", "Ngữ cảnh hạn chế — dùng có kiểm soát", "level2")]
    out = []
    for cls, title, tag, key in heads:
        items = p.get(key) or []
        items = items.get("items", []) if isinstance(items, dict) else items
        qs = "".join(q_html(i, it, "practice.%s #%d" % (key, i), strict) for i, it in enumerate(items, 1))
        out.append('<div class="lvl %s"><h3><span class="b">%s</span><span class="tag">%s</span></h3><div class="qs">%s</div></div>' % (cls, title, tag, qs))
    t = p.get("level3")
    if t:
        need(t.get("img"), "practice.level3", strict)
        tb = ""
        if t.get("table"):
            hd = "".join("<th>%s</th>" % rich(h) for h in t["table"]["headers"])
            rows = "".join("<tr>%s</tr>" % "".join("<td></td>" for _ in t["table"]["headers"]) for _ in range(t["table"].get("rows", 3)))
            tb = '<table class="tbl log"><thead><tr>%s</tr></thead><tbody>%s</tbody></table>' % (hd, rows)
        out.append('<div class="lvl l3"><h3><span class="b">Cấp 3 · Giao tiếp</span><span class="tag">Đáp án mở — thông tin thật</span></h3>'
                   '<div class="card task">%s<div class="t"><div class="qt">%s</div>%s%s</div></div></div>' % (
                       pic(t.get("img", ""), "lg", "warm"), rich(t["task"]), tb,
                       '<div class="crit">🎯 %s</div>' % rich(t["criteria"]) if t.get("criteria") else ""))
    return sec("s-practice", 5, "Luyện tập 3 cấp", "tri thức → bán giao tiếp → giao tiếp", "".join(out))


def build_activity(d, strict):
    a = d.get("activity")
    if not a:
        return ""
    need(a.get("img"), "activity", strict)
    names = ["Tầng 1 · Mô phỏng", "Tầng 2 · Có hướng dẫn", "Tầng 3 · Tự do"]
    tiers = "".join('<div class="card tier"><span class="lv">%s</span><div>%s</div></div>' % (n, rich(t)) for n, t in zip(names, a["tiers"]))
    head = '<div class="card scene">%s<div><b>%s</b><div>%s</div></div></div>' % (pic(a.get("img", ""), "lg"), rich(a["name"]), rich(a.get("goal", "Học sinh nói ≥ 2/3 thời gian.")))
    notes = d.get("teacher_notes") or []
    gv = '<div class="gvnote gv-only"><b>👩‍🏫 Ghi chú giáo viên</b><ul>%s</ul></div>' % "".join("<li>%s</li>" % rich(n) for n in notes) if notes else ""
    return sec("s-speak", 6, "Hoạt động nói", "", head + '<div class="tiers">%s</div>' % tiers + gv)


def build_recap(d, strict):
    r = d.get("recap") or []
    if not r:
        return ""
    cards = []
    for i, x in enumerate(r, 1):
        need(x.get("img"), "recap #%d" % i, strict)
        cards.append('<div class="card rc">%s%s<div class="vi">%s</div></div>' % (pic(x.get("img", ""), "lg", "pale"), zh(x["zh"], "md"), rich(x.get("vi", ""))))
    return sec("s-recap", "⭐", "Nhớ %d điều này là đủ" % len(r), "", '<div class="recap">%s</div>' % "".join(cards))


# ---------------------------------------------------------------- tổng
def build(d, strict=True):
    parts = [build_hero(d), build_vocab(d, strict), build_grammar(d, strict), build_dialogue(d, strict),
             build_mistakes(d, strict), build_practice(d, strict), build_activity(d, strict), build_recap(d, strict)]
    css = (ROOT / "assets" / "lesson.css").read_text("utf-8")
    js = (ROOT / "assets" / "lesson.js").read_text("utf-8")
    defs = "".join('<symbol id="e-%s" viewBox="%s">%s</symbol>' % (n, vb, inner) for n, (vb, inner) in ICONS.items())
    nav = [("s-goal", "Mục tiêu"), ("s-vocab", "Từ vựng"), ("s-grammar", "Ngữ pháp"), ("s-dialogue", "Hội thoại"),
           ("s-mistakes", "Lỗi sai"), ("s-practice", "Luyện tập"), ("s-speak", "Nói"), ("s-recap", "Nhớ")]
    page_title = "Unit %02d · %s · %s" % (int(d.get("unit", 0)), re.sub(r"\{([^|]+)\|[^}]+\}", r"\1", d["title_zh"]), d["title_vi"])
    return """<!DOCTYPE html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@500;600;700;800;900&family=Noto+Sans+SC:wght@400;500;700&display=swap" rel="stylesheet">
<style>%s</style></head><body>
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>%s</defs></svg>
<div class="topbar"><div class="in"><span class="brand">汉语 · %s</span>
<nav class="nav">%s</nav>
<div class="tools"><button class="btn" id="btn-vi" title="Ẩn nghĩa tiếng Việt để luyện nói">Ẩn nghĩa Việt</button><button class="btn" id="btn-gv">👩‍🏫 Chế độ GV</button></div></div></div>
<main class="wrap">%s
<footer>%s · Hình minh hoạ: Twemoji © Twitter/X &amp; contributors, CC-BY 4.0 · Pinyin luôn hiển thị trên đầu chữ Hán</footer></main>
<script>%s</script></body></html>""" % (
        html.escape(page_title), css, defs, html.escape(d.get("course", "Giao tiếp cấp tốc sơ cấp")),
        "".join('<a href="#%s">%s</a>' % n for n in nav), "".join(parts), html.escape(d.get("course", "Giao tiếp cấp tốc sơ cấp")), js)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lesson")
    ap.add_argument("-o", "--out")
    ap.add_argument("--lenient", action="store_true", help="thiếu hình chỉ cảnh báo, không lỗi")
    a = ap.parse_args()
    d = json.loads(Path(a.lesson).read_text("utf-8"))
    out = build(d, strict=not a.lenient)
    for k, v in sorted(POLY_SEEN.items()):
        WARN.append("Chữ đa âm %r trong: %s — kiểm tra pinyin (ghi đè bằng {字|pin yin} nếu sai)" % (k, " / ".join(sorted(v)[:4])))
    if ERR:
        print("LỖI (%d):" % len(ERR), *ERR, sep="\n  - ")
        sys.exit(2)
    dst = Path(a.out or Path(a.lesson).with_suffix(".html"))
    dst.write_text(out, "utf-8")
    print("OK ->", dst, "(%.0f KB, %d hình)" % (dst.stat().st_size / 1024, len(ICONS)))
    if WARN:
        print("Cảnh báo (%d):" % len(WARN), *WARN, sep="\n  - ")


if __name__ == "__main__":
    main()
