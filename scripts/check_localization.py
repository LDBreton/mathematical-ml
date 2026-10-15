"""Verify bilingual routes and preservation of mathematics and executable code."""
from html.parser import HTMLParser
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MATH = re.compile(r'\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)|(?<!\$)\$(?!\$)[^\n$]+\$')


class ReadingPage(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lang = None
        self.in_pre = False
        self.code = []
        self.links = []
        self.text = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ('script', 'style'):
            self.skip += 1
        if tag == 'html':
            self.lang = attrs.get('lang')
        if tag == 'pre':
            self.in_pre = True
            self.code.append('')
        if tag == 'a':
            self.links.append(attrs.get('href'))

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip -= 1
        if tag == 'pre':
            self.in_pre = False

    def handle_data(self, value):
        if not self.skip:
            self.text.append(value)
        if self.in_pre:
            self.code[-1] += value


def check():
    pages = list((ROOT / 'site').glob('*.html'))
    for path in pages:
        english, spanish = ReadingPage(), ReadingPage()
        english.feed(path.read_text(encoding='utf-8'))
        spanish.feed((path.parent / 'es' / path.name).read_text(encoding='utf-8'))
        assert english.lang == 'en' and spanish.lang == 'es', path.name
        assert english.code == spanish.code, f'Code or computed output changed: {path.name}'
        # Entity and inline-tag boundaries can split a formula across catalog
        # segments, so compare complete decoded page text, not individual entries.
        assert sorted(MATH.findall(''.join(english.text))) == sorted(MATH.findall(''.join(spanish.text))), f'Mathematics changed: {path.name}'
        assert 'es/' + path.name in english.links, path.name
        assert '../' + path.name in spanish.links, path.name
    print(f'PASS: {len(pages)} bilingual page pairs; equations, code, outputs and language links')


if __name__ == '__main__':
    check()
