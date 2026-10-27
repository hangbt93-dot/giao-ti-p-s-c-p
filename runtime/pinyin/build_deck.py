#!/usr/bin/env python3
"""Dựng giáo án dạng SLIDE 16:9 (1 file HTML tự chứa) từ deck.json.

    python3 build_deck.py deck.json --assets <thư mục có photos/ và audio/> -o Unit-01.html

deck.json = thông tin bìa + "flow": danh sách slide theo đúng thứ tự trình chiếu. Mỗi phần tử có "type":
  vocab · grammar · khoa (bài khoá + audio cả bài) · ext (cụm mở rộng, audio từng cụm) · practice ·
  tblex (bảng điền) · picex (bài tập có ảnh sách) · recap · homework

- Mọi chữ Hán có pinyin trên đầu (2/3 cỡ chữ Hán) — dùng lại bộ xử lý của build_lesson.py.
- Ô trống: viết [[đáp án]] — bấm từng ô để hiện đáp án.
- Ảnh: <assets>/photos/<khoá>.jpg; thiếu thì dùng emoji ("img") làm ảnh tạm.
- Audio: <assets>/audio/<tên>.mp3 nhúng base64; thiếu thì nút 🔊 đọc bằng giọng trình duyệt.
"""
import argparse, base64, html, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_lesson as bl  # noqa: E402

ROOT = bl.ROOT
rich, plain = bl.rich, bl.plain
AUDIO, USED_PHOTOS, MISSING_PHOTO, MISSING_AUDIO = {}, set(), [], []
ASSETS = None
NUM = "①②③④⑤⑥⑦⑧⑨⑩"
POS = {"đt": "đại từ", "tt": "tính từ", "ph": "phó từ", "dt": "danh từ", "đg": "động từ", "lt": "lượng từ", "gt": "giới từ", "lt2": "liên từ"}
VN = re.compile(r"([A-Za-zÀ-ỹ][A-Za-zÀ-ỹ ]*[A-Za-zÀ-ỹ]|[A-Za-zÀ-ỹ])")


def fm_html(f):
    """Công thức: chữ Latin/Việt (Người, S, Adj…) nhỏ hơn, font Times; chữ Hán giữ nguyên."""
    return "".join('<span class="vn">%s</span>' % html.escape(p) if VN.fullmatch(p) else rich(p) for p in VN.split(f) if p)


def pos_name(p):
    return POS.get(p, p)


def b64(p):
    return base64.b64encode(Path(p).read_bytes()).decode()


def visual(img, stem, cls=""):
    f = ASSETS / "photos" / (stem + ".jpg") if stem else None
    if f and f.exists():
        USED_PHOTOS.add(stem)
        return '<img class="photo %s" alt="" src="data:image/jpeg;base64,%s">' % (cls, b64(f))
    if stem:
        MISSING_PHOTO.append(stem)
    return bl.pic(img or "🙂", "md")


def audio_file(key):
    """Tìm file audio theo khoá: ưu tiên .mp3, rồi .m4a (AAC, nhẹ hơn wav)."""
    for ext, mime in ((".mp3", "audio/mpeg"), (".m4a", "audio/mp4")):
        f = ASSETS / "audio" / (key + ext)
        if f.exists():
            return f, mime
    return None, None


def audio_key(name):
    n = re.sub(r"[！？。，、!?.,\s…]", "", name)
    f, mime = audio_file(n)
    if f:
        AUDIO.setdefault(n, "data:%s;base64,%s" % (mime, b64(f)))
        return n
    return ""


def say(text, key=None, small=True):
    k = key or audio_key(plain(text))
    if not k:
        MISSING_AUDIO.append(plain(text))
    return '<button class="btn say%s" data-aud="%s" data-say="%s" aria-label="Nghe / dừng">🔊</button>' % (
        " sm" if small else "", html.escape(k), html.escape(plain(text)))


def play_btn(key, label):
    f, mime = audio_file(key)
    if not f:
        MISSING_AUDIO.append(key)
        return ""
    AUDIO.setdefault(key, "data:%s;base64,%s" % (mime, b64(f)))
    return '<button class="btn play" data-aud="%s" data-label="%s">▶ %s</button>' % (key, html.escape(label), html.escape(label))


def slide(inner):
    return '<div class="frame"><section class="slide">%s</section></div>' % inner


def head(d, title, sub=""):
    return '<div class="hd"><span class="u">UNIT %d</span><h2>%s</h2>%s</div>' % (
        int(d["unit"]), rich(title), '<span class="sub">%s</span>' % rich(sub) if sub else "")


def body(inner):
    return '<div class="bd">%s</div>' % inner


# ------------------------------------------------------------------ bìa
def s_cover(d):
    goals = "".join("<div>%s</div>" % rich(g) for g in d["goals"])
    return slide(
        '<div class="circle"></div><div class="in"><div class="l"><span class="u">UNIT %02d · %s</span><h1><div class="zh">%s</div></h1>'
        '<div class="vt">%s</div><div class="course">%s</div><div class="goals">%s</div></div><div class="r">%s</div></div>' % (
            int(d["unit"]), html.escape(d.get("level", "Sơ cấp")), rich(d["title_zh"]), html.escape(d["title_vi"]),
            html.escape(d.get("course", "Giao tiếp cấp tốc sơ cấp")), goals, visual(d.get("cover_img", "👋 😊"), d.get("cover_photo", "你好")))
    ).replace('class="slide"', 'class="slide cover"')


# ------------------------------------------------------------------ từ vựng
def s_vocab(d, sl):
    cards = []
    for it in sl["items"]:
        long = len(re.sub(r"[^%s]" % bl.HAN, "", it["zh"])) >= 3
        cards.append('<div class="card vc%s">%s%s%s<div class="zh">%s</div><div class="m">%s</div></div>' % (
            " big" if long else "", '<span class="chip">%s</span>' % html.escape(pos_name(it["pos"])) if it.get("pos") else "",
            say(it["zh"]), visual(it.get("img"), it.get("photo", it["zh"])), rich(it["zh"]), rich(it["vi"])))
    return slide(head(d, sl["title"], sl.get("sub", "")) + body('<div class="vgrid">%s</div>' % "".join(cards)))


# ------------------------------------------------------------------ ngữ pháp
def s_grammar(d, sl):
    parts, fms = [], []
    for f in sl["formulas"]:
        fms.append('<div class="fm"><div class="zh">%s</div>%s</div>' % (fm_html(f["f"]), '<div class="lab">%s</div>' % rich(f["label"]) if f.get("label") else ""))
    parts.append('<div class="fms" style="--n:%d">%s</div>' % (len(fms), "".join(fms)))
    if sl.get("table"):
        t = sl["table"]

        def cell(c):
            z, _, v = c.partition("§")
            return rich(z.strip()) + ('<span class="vi">%s</span>' % html.escape(v.strip()) if v else "")
        head_ = "".join("<th>%s</th>" % rich(h) for h in t["headers"])
        rows = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % cell(c) for c in r) for r in t["rows"])
        parts.append('<table class="tbl"><thead><tr>%s</tr></thead><tbody>%s</tbody></table>' % (head_, rows))
    if sl.get("phrases"):
        xs = "".join('<div class="card xi">%s<div class="t"><div class="zh">%s</div><div class="vi hv">%s</div></div></div>' % (
            say(it["zh"], small=False), rich(it["zh"]), rich(it["vi"])) for it in sl["phrases"])
        parts.append('<div class="xs" style="--c:%d">%s</div>' % (sl.get("pcols", 3), xs))
    if sl.get("examples"):
        cols = " three" if len(sl["examples"]) == 3 else ""
        ex = "".join('<div class="card ex"><div class="t"><div class="zh">%s</div><div class="vi hv">%s</div></div></div>' % (rich(e["zh"]), rich(e["vi"])) for e in sl["examples"])
        parts.append('<div class="exs%s">%s</div>' % (cols, ex))
    if sl.get("note"):
        parts.append('<div class="note">%s</div>' % rich(sl["note"]))
    return slide(head(d, sl["title"], sl.get("sub", "")) + body('<div class="g">%s</div>' % "".join(parts)))


# ------------------------------------------------------------------ bài khoá (audio cả bài)
def line_html(l, audio=False):
    return '<div class="ln %s"><span class="who">%s</span><div class="t"><div class="zh">%s</div><div class="vi hv">%s</div></div>%s</div>' % (
        l["who"], l["who"], rich(l["zh"]), rich(l["vi"]), say(l["zh"]) if audio and audio_key(plain(l["zh"])) else "")


def bubble_html(bb):
    if bb.get("rows"):
        rows = "".join('<div class="br">%s</div>' % "".join("<span>%s</span>" % rich(x) for x in r) for r in bb["rows"])
        return '<div class="bb rows">%s</div>' % rows
    return '<div class="bb">%s</div>' % "".join('<span class="bw">%s</span>' % rich(w) for w in bb["words"].split())


def s_khoa(d, sl):
    blocks = ""
    for i, b in enumerate(sl["blocks"]):
        lines = "".join(line_html(l, sl.get("line_audio")) for l in b["lines"])
        bubs = "".join(bubble_html(x) for x in b.get("bubbles", []))
        num = '<span class="bn">%s</span>' % NUM[i] if sl.get("number", True) else ""
        cls = ("tall " if b.get("tall") else "") + ("wide " if b.get("wide") else "") + ("bs " if b.get("bside") else "")
        if b.get("bubbles_out"):
            blocks += '<div class="card blk span2 %s">%s<div class="bkl">%s</div></div><div class="bubbox"><div class="bubs">%s</div></div>' % (cls, num, lines, bubs)
        else:
            inner = '<div class="bkl">%s</div>%s' % (lines, '<div class="bubs">%s</div>' % bubs if bubs else "")
            blocks += '<div class="card blk %s">%s%s</div>' % (cls, num, inner)
    for sw in sl.get("swaps", []):
        blocks += '<div class="swap">%s</div>' % rich(sw)
    side = "" if not (sl.get("photo") or sl.get("img")) else '<div class="side">%s<div class="sit"><b>Tình huống:</b> %s</div>%s</div>' % (
        visual(sl.get("img"), sl.get("photo")), rich(sl["situation"]), play_btn(sl["audio"], sl.get("audio_label", "Nghe bài khoá")) if sl.get("audio") else "")
    return slide(head(d, sl["title"], sl.get("sub", "")) + body('<div class="dl">%s<div class="blocks" style="--c:%d;%s">%s</div></div>' % (side, sl.get("cols", 2), ("grid-template-columns:%s" % sl["gridcols"]) if sl.get("gridcols") else "", blocks)))


# ------------------------------------------------------------------ cụm mở rộng, mỗi cụm 1 nút audio
def s_ext(d, sl):
    cols = ""
    for g in sl["groups"]:
        items = "".join('<div class="card xi">%s<div class="t"><div class="zh">%s</div><div class="vi hv">%s</div></div></div>' % (
            say(it["zh"], key=it.get("audio"), small=False), rich(it["zh"]), rich(it["vi"])) for it in g["items"])
        cols += '<div class="xc"><div class="xh">%s</div><div class="xs" style="--c:%d">%s</div></div>' % (rich(g["label"]), g.get("cols", 3), items)
    return slide(head(d, sl["title"], sl.get("sub", "")) + body('<div class="xg">%s</div>' % cols))


# ------------------------------------------------------------------ luyện tập
def q_html(i, it):
    opts = '<div class="opts">%s</div>' % "".join("<span>%s</span>" % rich(o) for o in it["opts"]) if it.get("opts") else ""
    ans = '<div class="ans">%s</div>' % rich(it["a"]) if it.get("a") else ""
    return '<div class="card q%s%s"><span class="n">%d</span><div class="tx mix">%s%s%s</div></div>' % (
        "" if it.get("a") else " nb", " wide" if it.get("wide") else "", i, rich(it["q"]), opts, ans)


def s_practice(d, sl):
    qs = [q_html(i, it) for i, it in enumerate(sl.get("items", []), 1)]
    if sl.get("task"):
        tb = ""
        if sl.get("table"):
            hd = "".join("<th>%s</th>" % rich(h) for h in sl["table"]["headers"])
            rows = "".join("<tr>%s</tr>" % "".join("<td></td>" for _ in sl["table"]["headers"]) for _ in range(sl["table"].get("rows", 3)))
            tb = '<table class="tbl log"><thead><tr>%s</tr></thead><tbody>%s</tbody></table>' % (hd, rows)
        qs.append('<div class="card task mix"><div>%s%s%s</div></div>' % (
            rich(sl["task"]), tb, '<div class="vi" style="margin-top:14px">🎯 %s</div>' % rich(sl["criteria"]) if sl.get("criteria") else ""))
    one = " one" if sl.get("cols", 2) == 1 else ""
    side = '<div class="side">%s<div class="tag">%s</div></div>' % (visual(sl.get("img"), sl.get("photo")), rich(sl.get("tag", "")))
    return slide(head(d, sl["title"], sl.get("sub", "")) + body('<div class="pr">%s<div class="qs%s">%s</div></div>' % (side, one, "".join(qs))))


def s_tblex(d, sl):
    t = sl["table"]
    hd = "".join("<th>%s</th>" % rich(h) for h in t["headers"])
    rows = "".join("<tr>%s</tr>" % "".join('<td class="mix">%s</td>' % rich(c) for c in r) for r in t["rows"])
    side = '<div class="side">%s<div class="tag">%s</div></div>' % (visual(sl.get("img"), sl.get("photo")), rich(sl.get("tag", "")))
    return slide(head(d, sl["title"], sl.get("sub", "")) + body(
        '<div class="pr">%s<div class="qs one"><table class="tbl ex2"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div></div>' % (side, hd, rows)))


def s_picex(d, sl):
    cards = []
    for it in sl["items"]:
        lines = "".join('<div class="pl">%s<span class="mix">%s</span></div>' % ('<b class="pw">%s</b>' % it_who if (it_who := l.get("who")) else "", rich(l["t"])) for l in it["lines"])
        cards.append('<div class="card pc">%s<div class="pls">%s</div></div>' % (visual(it.get("img"), it.get("photo"), "bk"), lines))
    return slide(head(d, sl["title"], sl.get("sub", "")) + body('<div class="pg%s" style="--c:%d;--ph:%dpx">%s</div>' % (" row" if sl.get("row") else "", sl.get("cols", 3), sl.get("ph", 200), "".join(cards))))


# ------------------------------------------------------------------ tổng kết, về nhà
def s_recap(d, sl):
    out = []
    v = "".join('<div class="card row"><span class="lb">%s</span><div class="zh">%s</div></div>' % (rich(x["label"]), rich(x["words"])) for x in sl["vocab"])
    g = "".join('<div class="fm sm"><div class="zh">%s</div><div class="lab">%s</div></div>' % (rich(x["f"]), rich(x["label"])) for x in sl["grammar"])
    return [slide(head(d, "Tổng kết · Từ vựng") + body('<div class="rc g1">%s</div>' % v)),
            slide(head(d, "Tổng kết · Ngữ pháp") + body('<div class="g" style="gap:20px">%s</div>' % g))]


def s_homework(d, h):
    tasks = "".join('<div class="card tk"><div class="k">%s<small>%s</small></div><div class="tt">%s</div></div>' % (
        rich(t["title"]), html.escape(t.get("time", "")), rich(t["text"])) for t in h["tasks"])
    ck = '<div class="ck">%s</div>' % "".join("<span>%s</span>" % rich(c) for c in h["checklist"])
    return slide(head(d, "Bài tập về nhà", h.get("sub", "≈ 15 phút")) + body(
        '<div class="hw"><div class="side">%s<div class="sit">%s</div></div><div class="main">%s%s</div></div>' % (
            visual(h.get("img"), h.get("photo")), rich(h.get("lead", "")), tasks, ck)))


def s_flash(d, sl, vocab_items):
    per = sl.get("per", 8)
    out = []
    chunks = [vocab_items[i:i + per] for i in range(0, len(vocab_items), per)]
    for ci, ch in enumerate(chunks, 1):
        cards = []
        for it in ch:
            n_han = len(re.sub(r"[^%s]" % bl.HAN, "", it["zh"]))
            front = '<div class="f card"><div class="zh%s">%s</div>%s</div>' % (" l4" if n_han >= 4 else " l3" if n_han == 3 else "", rich(it["zh"]), '<span class="chip">%s</span>' % html.escape(pos_name(it["pos"])) if it.get("pos") else "")
            back = '<div class="b card">%s%s<div class="m">%s</div></div>' % (
                say(it["zh"]), visual(it.get("img"), it.get("photo", it["zh"])), rich(it["vi"]))
            cards.append('<div class="fc"><div class="in">%s%s</div></div>' % (front, back))
        out.append(slide(head(d, sl.get("title", "Flashcard"), "bấm thẻ để lật · %d / %d" % (ci, len(chunks))) + body('<div class="fgrid">%s</div>' % "".join(cards))))
    return out


def s_hwfill(d, sl):
    qs = "".join('<div class="card q nb"><span class="n">%d</span><div class="tx mix">%s</div><span class="mk"></span></div>' % (i, rich(it["q"])) for i, it in enumerate(sl["items"], 1))
    side = '<div class="side">%s<div class="tag">%s</div><button class="btn chk" id="hwchk">✔ Kiểm tra đáp án</button><button class="btn rst" id="hwrst">↺ Làm lại</button><div class="score" id="hwsc"></div></div>' % (
        visual(sl.get("img"), sl.get("photo")), rich(sl.get("tag", "")))
    return slide(head(d, sl["title"], sl.get("sub", "")) + body('<div class="pr hwf">%s<div class="qs">%s</div></div>' % (side, qs)))


HANDLERS = {"hwfill": s_hwfill, "vocab": s_vocab, "grammar": s_grammar, "khoa": s_khoa, "ext": s_ext, "practice": s_practice, "tblex": s_tblex, "picex": s_picex}


def build(d):
    slides = [s_cover(d)]
    vocab_items = [it for sl in d["flow"] if sl["type"] == "vocab" for it in sl["items"]]
    for sl in d["flow"]:
        t = sl["type"]
        if t == "flash":
            slides += s_flash(d, sl, vocab_items)
        elif t == "recap":
            slides += s_recap(d, sl)
        elif t == "homework":
            slides.append(s_homework(d, sl))
        else:
            slides.append(HANDLERS[t](d, sl))
    n = len(slides)
    swap = lambda s: re.sub(r"<ruby([^>]*)>(.*?)<rt>(.*?)</rt></ruby>", r"<ruby\1><rt>\3</rt>\2</ruby>", s)
    numbered = []
    for i, s in enumerate(slides, 1):
        s = swap(s)
        k = s.rfind("</section>")
        numbered.append(s[:k] + '<div class="bar" style="width:%.1f%%"></div><div class="no">%d / %d</div>' % (100.0 * i / n, i, n) + s[k:])
    css = (ROOT / "assets" / "deck.css").read_text("utf-8")
    js = (ROOT / "assets" / "deck.js").read_text("utf-8")
    defs = "".join('<symbol id="e-%s" viewBox="%s">%s</symbol>' % (k, vb, inner) for k, (vb, inner) in bl.ICONS.items())
    aud = "window.AUD=" + json.dumps(AUDIO, ensure_ascii=False) + ";"
    title = "Unit %d · %s · %s" % (int(d["unit"]), re.sub(r"\{([^|]+)\|[^}]+\}", r"\1", d["title_zh"]), d["title_vi"])
    return """<!DOCTYPE html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@500;600;700;800;900&family=Noto+Sans+SC:wght@400;500;700&display=swap" rel="stylesheet">
<style>%s</style></head><body>
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>%s</defs></svg>
<div id="viewport">%s</div>
<div id="ctl"><button id="prev" aria-label="Trước">◀</button><span class="c" id="cnt"></span><button id="next" aria-label="Sau">▶</button>
<button id="bvi" title="Ẩn nghĩa tiếng Việt">Ẩn nghĩa Việt</button><button id="bsc" title="Cuộn dọc / xem toàn bộ">Cuộn</button><button id="bfs" title="Toàn màn hình">⛶</button></div>
<script>%s</script><script>%s</script></body></html>""" % (html.escape(title), css, defs, "".join(numbered), aud, js)


def main():
    global ASSETS
    ap = argparse.ArgumentParser()
    ap.add_argument("deck")
    ap.add_argument("--assets", required=True, help="thư mục chứa photos/ và audio/")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    ASSETS = Path(a.assets)
    d = json.loads(Path(a.deck).read_text("utf-8"))
    out = build(d)
    for k, v in sorted(bl.POLY_SEEN.items()):
        bl.WARN.append("Chữ đa âm %r trong: %s — kiểm tra pinyin" % (k, " / ".join(sorted(v)[:4])))
    Path(a.out).write_text(out, "utf-8")
    print("OK ->", a.out, "(%.1f MB; %d slide; %d ảnh thật; %d audio)" % (Path(a.out).stat().st_size / 1e6, out.count('<section class="slide'), len(USED_PHOTOS), len(AUDIO)))
    if MISSING_PHOTO:
        print("Chưa có ảnh thật (đang dùng emoji tạm) cho %d mục: %s" % (len(set(MISSING_PHOTO)), " ".join(sorted(set(MISSING_PHOTO)))))
    if MISSING_AUDIO:
        print("Chưa có audio (đọc bằng giọng trình duyệt): %s" % " ".join(sorted(set(MISSING_AUDIO))))
    if bl.WARN:
        print("Cảnh báo:", *bl.WARN, sep="\n  - ")


if __name__ == "__main__":
    main()
