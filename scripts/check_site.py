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
        self.ids = set()
        self.fragments = []

    def handle_starttag(self, tag, attributes):
        properties = dict(attributes)
        if properties.get("id"):
            self.ids.add(properties["id"])
        if tag == "img" and not properties.get("alt"):
            self.broken.append("image without descriptive alt text")
        for key, value in attributes:
            if key not in {"href", "src"} or not value:
                continue
            url = urlsplit(value)
            if url.scheme or url.netloc:
                continue
            target = self.path.parent / unquote(url.path) if url.path else self.path
            if key == "href" and url.fragment:
                self.fragments.append((target.resolve(), unquote(url.fragment)))
            if not target.exists():
                self.broken.append(value)


if __name__ == "__main__":
    pages = sorted((ROOT / "site").glob("*.html"))
    if not pages:
        raise SystemExit("Build the website first: python scripts/build_site.py")
    errors = []
    parsed = {}
    for path in pages:
        source = path.read_text(encoding="utf-8")
        parser = LocalLinks(path)
        parser.feed(source)
        parsed[path.resolve()] = parser
        errors.extend(f"{path.name}: {link}" for link in parser.broken)
        if any(ord(character) < 32 and character not in "\n\t\r" for character in source):
            errors.append(f"{path.name}: unexpected control character")
    for path, parser in parsed.items():
        for target, fragment in parser.fragments:
            if target in parsed and fragment not in parsed[target].ids:
                errors.append(f"{path.name}: missing anchor {target.name}#{fragment}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"PASS: {len(pages)} HTML pages, local links, anchors, downloads, and image descriptions")
