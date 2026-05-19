from pathlib import Path

p = Path(__file__).resolve().parents[1] / "index.html"
text = p.read_text(encoding="utf-8")
needle = 'window.CLEANING_SPRITE_DATA = {"plate":'
count = text.count(needle)
if count <= 1:
    print("no duplicate, count=", count)
else:
    first = text.index(needle)
    second = text.index(needle, first + 1)
    start = text.rfind("<script>", 0, second)
    end = text.index("</script>", second) + len("</script>")
  # remove duplicate block including newline
    while end < len(text) and text[end] in "\r\n":
        end += 1
    text = text[:start] + text[end:]
    p.write_text(text, encoding="utf-8")
    print("removed duplicate block")
