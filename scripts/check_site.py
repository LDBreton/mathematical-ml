"""Check generated local links, downloads, and unintended TeX control characters."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class LocalLinks(HTMLParser):
    def __init__(self, path: Path):
        super().__init__()
        self.path = path
        self.broken = []

    def handle_starttag(self, tag, attributes):
        for key, value in attributes:
            if key not in {"href", "src"} or not value:
                continue
            url = urlsplit(value)
            if url.scheme or url.netloc or not url.path:
                continue
            target = self.path.parent / unquote(url.path)
            if not target.exists():
                self.broken.append(value)


if __name__ == "__main__":
    pages = sorted((ROOT / "site").glob("*.html"))
    if not pages:
        raise SystemExit("Build the website first: python scripts/build_site.py")
    errors = []
    for path in pages:
        source = path.read_text(encoding="utf-8")
        parser = LocalLinks(path)
        parser.feed(source)
        errors.extend(f"{path.name}: {link}" for link in parser.broken)
        if any(ord(character) < 32 and character not in "\n\t\r" for character in source):
            errors.append(f"{path.name}: unexpected control character")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"PASS: {len(pages)} HTML pages, all local links and downloads exist")
