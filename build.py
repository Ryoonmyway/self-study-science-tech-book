"""把 Obsidian 书稿同步成 book.md，并用 Chrome 打印出带版权页和问卷页的 PDF。

用法：python build.py [书稿路径] [--version 20261017]（版本号默认取当天日期）
依赖：pip install markdown；本机装有 Chrome 或 Edge。
"""

import argparse
import html
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import fitz  # pymupdf，用来量章节页码
import markdown

ROOT = Path(__file__).resolve().parent
DEFAULT_SOURCE = (
    ROOT.parent
    / "20260621_223610_自学科学与技术：反内卷的大学生存工程学"
    / "自学科学与技术：反内卷的大学生存工程学.md"
)
TITLE = "自学科学与技术"
SUBTITLE = "反内卷的大学生存工程学"
AUTHOR = "在路上的小凉"
REPO_URL = "https://github.com/Ryoonmyway/self-study-science-tech-book"
LICENSE_URL = "https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hans"
QR = "assets/feedback-qr.png"
BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]

FEEDBACK_EMBED = re.compile(r"!\[\[[^\]]*读者反馈问卷[^\]]*\]\]")


def to_book_md(text: str) -> str:
    """Obsidian 写法转成 GitHub 能渲染的 Markdown。"""
    text = FEEDBACK_EMBED.sub(f"![读者反馈问卷]({QR})", text)
    if "![[" in text:
        sys.exit("书稿里还有未处理的 Obsidian 图片嵌入 ![[...]]，先在 build.py 里加转换规则。")
    return text.rstrip() + "\n"


def display_version(version: str) -> str:
    """20261017 → 2026.10.17 版；不是日期格式就原样显示。"""
    if re.fullmatch(r"\d{8}", version):
        return f"{version[:4]}.{version[4:6]}.{version[6:]} 版"
    return version


def front_pages(version: str) -> str:
    shown = display_version(version)
    return f"""
<section class="cover">
  <h1 class="book-title">{TITLE}</h1>
  <p class="book-subtitle">{SUBTITLE}</p>
  <p class="book-meta">{AUTHOR}<br>{shown}</p>
</section>
<section class="copyright">
  <p><strong>《{TITLE}：{SUBTITLE}》{shown}</strong></p>
  <p>作者：{AUTHOR}（公众号：在路上的小凉；X：@Ryo_onmyway）</p>
  <p>本书采用 <a href="{LICENSE_URL}">CC BY-NC-SA 4.0</a> 协议发布：
  欢迎转载和改编，请注明作者与原始地址，改编版本须沿用同一协议；不得用于商业用途。</p>
  <p>以下用途视为商业使用，未经许可不得进行：放进付费社群或付费课程，打包进收费资料包，以任何形式单独售卖。</p>
  <p>最新版地址：<a href="{REPO_URL}">{REPO_URL}</a></p>
</section>
"""


def feedback_page() -> str:
    return f"""
<section class="feedback" id="feedback">
  <h1>读者反馈</h1>
  <p>读完了？花两分钟告诉我哪里有用、哪里没用。下一版会根据这些反馈修改。</p>
  <img src="{QR}" alt="读者反馈问卷二维码">
  <p class="hint">手机微信扫码，或在微信里长按识别</p>
</section>
"""


CSS = """
@page { size: A4; margin: 22mm 20mm 20mm;
  @bottom-center { content: counter(page); font-size: 9pt; color: #888; } }
@page :first { @bottom-center { content: none; } }
body { font-family: "Microsoft YaHei", "PingFang SC", sans-serif; font-size: 11pt;
  line-height: 1.8; color: #222; }
h1 { font-size: 20pt; break-before: page; margin: 0 0 1em; }
h2 { font-size: 14pt; margin: 1.6em 0 .6em; break-after: avoid; }
p, li { text-align: justify; }
a { color: #1a5fb4; word-break: break-all; }
table { border-collapse: collapse; width: 100%; font-size: 10pt; margin: 1em 0; }
th, td { border: 1px solid #ccc; padding: 4px 8px; text-align: left; vertical-align: top; }
code { font-family: Consolas, monospace; font-size: 9.5pt; background: #f3f3f3; padding: 0 3px; }
pre { background: #f3f3f3; padding: 8px 12px; white-space: pre-wrap; break-inside: avoid; }
pre code { background: none; padding: 0; }
blockquote { margin: 1em 0; padding-left: 1em; border-left: 3px solid #ccc; color: #555; }
img { max-width: 100%; }
.cover { height: 240mm; display: flex; flex-direction: column; justify-content: center; text-align: center; }
.cover .book-title { break-before: auto; font-size: 32pt; margin: 0; }
.book-subtitle { font-size: 16pt; color: #555; margin: .4em 0 3em; text-align: center; }
.book-meta { color: #555; text-align: center; }
.copyright { break-before: page; padding-top: 140mm; font-size: 9.5pt; color: #444; }
.copyright p { margin: .5em 0; }
.toc { break-before: page; padding-top: 18mm; }
.toc-label { margin: 0; font-size: 9pt; letter-spacing: .35em; color: #1a5fb4; }
.toc .toc-title { break-before: auto; font-size: 26pt; margin: .1em 0 1.2em;
  padding-bottom: .5em; border-bottom: 2px solid #222; }
.toc-list { list-style: none; padding: 0; margin: 0; }
.toc-list li { border-bottom: 1px solid #e6e6e6; }
.toc-list a { display: flex; align-items: baseline; padding: .62em 0; color: #222; text-decoration: none; }
.toc-num { width: 2.4em; flex: none; font-size: 13pt; font-weight: 700; color: #1a5fb4; }
.toc-main { font-size: 12pt; font-weight: 700; }
.toc-sub { margin-left: .8em; font-size: 10pt; color: #777; }
.toc-dots { flex: 1; margin: 0 .8em; border-bottom: 1px dotted #bbb; transform: translateY(-.3em); }
.toc-page { flex: none; min-width: 1.6em; text-align: right; font-size: 10.5pt; color: #555;
  font-variant-numeric: tabular-nums; }
.toc-list li.extra .toc-main { font-weight: 400; color: #555; }
.feedback { text-align: center; }
.feedback p { text-align: center; }
.feedback img { width: 60mm; margin: 1.5em auto; display: block; }
.feedback .hint { color: #888; font-size: 9.5pt; }
"""


CHAPTER = re.compile(r"^([零一二三四五六七八九十]+)，(.+)$")


def toc_entries(md: markdown.Markdown) -> list[dict]:
    """一级标题拆成 章节号 / 主标题 / 副标题，例如「四，内化：试卷的逆向工程」。"""
    entries = []
    for tok in md.toc_tokens:
        name = html.unescape(tok["name"])
        m = CHAPTER.match(name)
        num, rest = (m.group(1), m.group(2)) if m else ("", name)
        main_title, _, sub = rest.partition("：")
        entries.append({"id": tok["id"], "heading": name, "num": num,
                        "main": main_title, "sub": sub})
    entries.append({"id": "feedback", "heading": "读者反馈", "num": "",
                    "main": "读者反馈", "sub": ""})
    return entries


def toc_html(entries: list[dict], pages: dict[str, int]) -> str:
    items = []
    for e in entries:
        sub = f'<span class="toc-sub">{e["sub"]}</span>' if e["sub"] else ""
        extra = "" if e["num"] else ' class="extra"'
        items.append(
            f'<li{extra}><a href="#{e["id"]}"><span class="toc-num">{e["num"]}</span>'
            f'<span class="toc-main">{e["main"]}</span>{sub}<span class="toc-dots"></span>'
            f'<span class="toc-page">{pages.get(e["heading"], "")}</span></a></li>'
        )
    return ('<section class="toc"><p class="toc-label">CONTENTS</p>'
            f'<h1 class="toc-title">目录</h1><ol class="toc-list">{"".join(items)}</ol></section>')


def build_html(book_md: str, version: str, pages: dict[str, int]) -> tuple[str, list[dict]]:
    # 正文末尾的问卷嵌图由单独的反馈页代替，开头的作者行由版权页代替，避免重复。
    body_md = book_md.replace(f"![读者反馈问卷]({QR})", "")
    body_md = re.sub(r"\A作者：.*\n", "", body_md)
    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists"])
    body = md.convert(body_md)
    entries = toc_entries(md)
    page = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>{TITLE}：{SUBTITLE} {display_version(version)}</title><style>{CSS}</style></head>
<body>{front_pages(version)}{toc_html(entries, pages)}<main>{body}</main>{feedback_page()}</body></html>
"""
    return page, entries


def find_pages(pdf_path: Path, entries: list[dict]) -> dict[str, int]:
    """在第一遍生成的 PDF 里找每章标题所在页，页码从封面算起。"""
    doc = fitz.open(pdf_path)
    texts = [[line.strip() for line in p.get_text().splitlines()] for p in doc]
    doc.close()
    start = next(i for i, t in enumerate(texts) if "目录" in t) + 1
    pages = {}
    for e in entries:
        hit = next((i for i in range(start, len(texts)) if e["heading"] in texts[i]), None)
        if hit is None:
            sys.exit(f"PDF 里找不到标题「{e['heading']}」，目录页码无法生成。")
        pages[e["heading"]] = hit + 1
    return pages


def print_pdf(html_path: Path, pdf_path: Path) -> None:
    browser = next((b for b in BROWSERS if Path(b).exists()), None)
    if browser is None:
        sys.exit("没找到 Chrome 或 Edge，改一下 build.py 里的 BROWSERS。")
    subprocess.run(
        [browser, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={pdf_path}", html_path.as_uri()],
        check=True, capture_output=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", nargs="?", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--version", default=date.today().strftime("%Y%m%d"),
                        help="默认用今天的日期，例如 20261017")
    args = parser.parse_args()

    book_md = to_book_md(args.source.read_text(encoding="utf-8"))
    (ROOT / "book.md").write_text(book_md, encoding="utf-8")

    dist = ROOT / "dist"
    if dist.exists():
        shutil.rmtree(dist)
    dist.mkdir()
    html_path = ROOT / "book.html"  # 放在根目录，图片相对路径才能找到
    pdf_path = dist / f"{TITLE}-{args.version}.pdf"
    try:
        # 第一遍不带页码，量出每章在第几页；第二遍把页码填进目录。
        page, entries = build_html(book_md, args.version, {})
        html_path.write_text(page, encoding="utf-8")
        print_pdf(html_path, pdf_path)
        pages = find_pages(pdf_path, entries)
        page, _ = build_html(book_md, args.version, pages)
        html_path.write_text(page, encoding="utf-8")
        print_pdf(html_path, pdf_path)
        if find_pages(pdf_path, entries) != pages:
            sys.exit("目录页码和正文对不上，检查一下目录页是否被挤成了两页。")
    finally:
        html_path.unlink()
    print(f"book.md 已同步；PDF：{pdf_path}")


if __name__ == "__main__":
    main()
