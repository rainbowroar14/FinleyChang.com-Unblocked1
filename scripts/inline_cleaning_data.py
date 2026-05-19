from pathlib import Path

root = Path(__file__).resolve().parents[1]
data_js = (root / "assets" / "cleaning" / "cleaning-sprites-data.js").read_text(encoding="utf-8")
html_path = root / "index.html"
html = html_path.read_text(encoding="utf-8")
marker = '  <script src="assets/cleaning/cleaning-sprites-data.js"></script>\n'
inline = "  <script>\n" + "\n".join("  " + line for line in data_js.splitlines()) + "\n  </script>\n"
if marker not in html:
    if "window.CLEANING_SPRITE_DATA" in html:
        print("already inlined")
    else:
        raise SystemExit("marker missing")
elif "window.CLEANING_SPRITE_DATA" in html.split(marker, 1)[1].split("<script>", 1)[0]:
    print("already inlined after marker")
else:
    html_path.write_text(html.replace(marker, marker + inline, 1), encoding="utf-8")
    print("inlined ok")
