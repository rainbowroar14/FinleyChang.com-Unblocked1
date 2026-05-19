from pathlib import Path

root = Path(__file__).resolve().parents[1]
marker = '  <script src="assets/cleaning/cleaning-sprites-data.js"></script>\n'
data_js = (root / "assets" / "cleaning" / "cleaning-sprites-data.js").read_text(encoding="utf-8")
inline = "  <script>\n" + "\n".join("  " + line for line in data_js.splitlines()) + "\n  </script>\n"
html_path = root / "index.html"
html = html_path.read_text(encoding="utf-8")
if marker not in html:
    raise SystemExit("marker missing")
head, rest = html.split(marker, 1)
while rest.startswith("  <script>") and "window.CLEANING_SPRITE_DATA" in rest.split("  </script>", 1)[0]:
    rest = rest.split("  </script>\n", 1)[1]
html_path.write_text(head + marker + inline + rest, encoding="utf-8")
print("deduped and refreshed inline")
