import html
import os
import re
import sys
import uuid
import zipfile
from datetime import datetime, timezone

def _configure_stdout():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

_configure_stdout()



IMG_RE = re.compile(r"^!\[(.*?)\]\((.+?)\)\s*$")

MEDIA = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
}


def inline(text):
    out = html.escape(text)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    return out


def md_to_xhtml(md, title, images):
    out = []
    in_list = False
    for raw in md.splitlines():
        line = raw.rstrip()
        if not line.strip():
            if in_list:
                out.append("</ul>")
                in_list = False
            continue
        m = IMG_RE.match(line)
        if m:
            if in_list:
                out.append("</ul>")
                in_list = False
            caption = m.group(1).strip()
            path = m.group(2).strip()
            name = os.path.basename(path)
            images.append(path)
            out.append('<div class="figure"><img src="images/%s" alt="%s" style="max-width:100%%;height:auto;"/>' % (html.escape(name), html.escape(caption)))
            if caption:
                out.append('<p class="caption">%s</p>' % html.escape(caption))
            out.append("</div>")
            continue
        if line.startswith("# "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append("<h1>%s</h1>" % html.escape(line[2:].strip()))
            continue
        if line.startswith("## "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append("<h2>%s</h2>" % html.escape(line[3:].strip()))
            continue
        if line.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append("<li>%s</li>" % inline(line[2:].strip()))
            continue
        if in_list:
            out.append("</ul>")
            in_list = False
        out.append("<p>%s</p>" % inline(line))
    if in_list:
        out.append("</ul>")
    body = "\n".join(out)
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        "<!DOCTYPE html>\n"
        '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh-CN" lang="zh-CN">\n'
        "<head>\n"
        '<meta charset="utf-8"/>\n'
        "<title>%s</title>\n"
        '<link rel="stylesheet" type="text/css" href="style.css"/>\n'
        "</head>\n<body>\n<article>\n%s\n</article>\n</body>\n</html>\n"
    ) % (html.escape(title), body)


CSS = """body { font-family: "Noto Serif CJK SC", "Source Han Serif SC", serif; line-height: 1.75; margin: 1.2em; }
h1 { font-size: 1.5em; margin: 0.6em 0 1em; line-height: 1.4; }
h2 { font-size: 1.15em; margin: 1.6em 0 0.6em; padding-bottom: 0.25em; border-bottom: 1px solid #ccc; }
p { text-indent: 2em; margin: 0.7em 0; text-align: justify; }
li { margin: 0.35em 0; }
ul { padding-left: 1.4em; }
div.figure { margin: 1.6em 0; text-align: center; page-break-inside: avoid; }
div.figure img { max-width: 100%; height: auto; }
p.caption { font-size: 0.85em; color: #555; margin-top: 0.5em; text-indent: 0; line-height: 1.5; text-align: center; }
"""


def build(md_path, epub_path, title, author):
    with open(md_path, "r", encoding="utf-8") as f:
        md = f.read()
    md_dir = os.path.dirname(os.path.abspath(md_path))
    images = []
    xhtml = md_to_xhtml(md, title, images)

    seen = []
    for p in images:
        name = os.path.basename(p)
        src = p if os.path.isabs(p) else os.path.join(md_dir, p)
        if os.path.exists(src) and name not in [s[0] for s in seen]:
            seen.append((name, src))

    book_id = "urn:uuid:" + str(uuid.uuid4())
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    manifest_images = []
    for i, (name, src) in enumerate(seen, start=1):
        ext = os.path.splitext(name)[1].lower()
        mt = MEDIA.get(ext, "image/png")
        manifest_images.append(
            '    <item id="img%d" href="images/%s" media-type="%s"/>' % (i, html.escape(name), mt)
        )

    content_opf = """<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="zh-CN">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">%s</dc:identifier>
    <dc:title>%s</dc:title>
    <dc:creator>%s</dc:creator>
    <dc:language>zh-CN</dc:language>
    <meta property="dcterms:modified">%s</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="css" href="style.css" media-type="text/css"/>
    <item id="text" href="text.xhtml" media-type="application/xhtml+xml"/>
%s
  </manifest>
  <spine>
    <itemref idref="text"/>
  </spine>
</package>
""" % (book_id, html.escape(title), html.escape(author), now, "\n".join(manifest_images))

    nav = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        "<!DOCTYPE html>\n"
        '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="zh-CN" lang="zh-CN">\n'
        '<head><meta charset="utf-8"/><title>目录</title></head>\n<body>\n'
        '<nav epub:type="toc" id="toc"><h1>目录</h1><ol><li><a href="text.xhtml">%s</a></li></ol></nav>\n'
        "</body></html>\n"
    ) % html.escape(title)

    container = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
        '  <rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>\n'
        "</container>\n"
    )

    with zipfile.ZipFile(epub_path, "w") as z:
        z.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", container, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/content.opf", content_opf, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/nav.xhtml", nav, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/style.css", CSS, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/text.xhtml", xhtml, compress_type=zipfile.ZIP_DEFLATED)
        for name, src in seen:
            z.write(src, "OEBPS/images/" + name, compress_type=zipfile.ZIP_DEFLATED)

    print("epub:", epub_path, os.path.getsize(epub_path), "bytes,", len(seen), "images")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
