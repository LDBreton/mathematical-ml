"""Build Spanish reading pages from reviewed, versioned translation catalogs.

HTML structure, anchor IDs, mathematics, executable code and captured outputs
remain shared. Missing text fails the build instead of silently mixing languages.
"""
import html
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


class SpanishPage(HTMLParser):
    def __init__(self, catalog):
        super().__init__(convert_charrefs=False)
        self.catalog = catalog
        self.parts = []
        self.skip = 0
        self.missing = set()

    def translate(self, value):
        key = value.strip()
        if not key or not any(c.isalpha() for c in key):
            return value
        if key not in self.catalog:
            self.missing.add(key)
            return value
        return value[:len(value)-len(value.lstrip())] + self.catalog[key] + value[len(value.rstrip()):]

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'pre', 'code'):
            self.skip += 1
        updated = []
        for key, value in attrs:
            if value is None:
                updated.append(key)
                continue
            if tag == 'html' and key == 'lang':
                value = 'es'
            elif key in ('alt', 'aria-label', 'placeholder', 'title') and not self.skip:
                value = self.translate(value)
            elif key == 'content' and tag == 'meta' and dict(attrs).get('name') == 'description':
                value = 'Ocho lecciones de aprendizaje automático para matemáticos: fundamentos, opciones de software y ejemplos guiados en Python.'
            elif key in ('href', 'src'):
                parsed = urlsplit(value)
                if not parsed.scheme and not parsed.netloc and parsed.path and not parsed.path.endswith('.html'):
                    value = '../' + value
            updated.append(f'{key}="{html.escape(value, quote=True)}"')
        self.parts.append('<' + tag + (' ' + ' '.join(updated) if updated else '') + '>')

    def handle_endtag(self, tag):
        self.parts.append(f'</{tag}>')
        if tag in ('script', 'style', 'pre', 'code'):
            self.skip -= 1

    def handle_data(self, value):
        self.parts.append(value if self.skip else html.escape(self.translate(value), quote=False))

    def handle_entityref(self, name):
        self.parts.append(f'&{name};')

    def handle_charref(self, name):
        self.parts.append(f'&#{name};')

    def handle_decl(self, decl):
        self.parts.append(f'<!{decl}>')

    def handle_comment(self, value):
        self.parts.append(f'<!--{value}-->')


def add_language_links(source, filename, spanish=False):
    english = '../' + filename if spanish else filename
    translated = filename if spanish else 'es/' + filename
    switch = ('<nav class="languages" aria-label="' + ('Idioma' if spanish else 'Language') + '">'
              f'<a href="{english}" lang="en" hreflang="en"'
              + ('' if spanish else ' aria-current="true"') + '>English</a>'
              f'<a href="{translated}" lang="es" hreflang="es"'
              + (' aria-current="true"' if spanish else '') + '>Español</a></nav>')
    source = source.replace('</header>', switch + '</header>', 1)
    alternates = (f'<link rel="alternate" hreflang="en" href="{english}">'
                  f'<link rel="alternate" hreflang="es" href="{translated}">'
                  f'<link rel="alternate" hreflang="x-default" href="{english}">')
    return source.replace('</head>', alternates + '</head>', 1)


def build_spanish(site):
    catalog = {}
    for path in sorted((ROOT / 'translations/es').glob('*.json')):
        entries = json.loads(path.read_text(encoding='utf-8'))
        overlap = catalog.keys() & entries.keys()
        if overlap:
            raise ValueError(f'Duplicate translation keys in {path}: {overlap}')
        catalog.update(entries)
    destination = site / 'es'
    destination.mkdir(exist_ok=True)
    missing = set()
    for path in sorted(site.glob('*.html')):
        source = path.read_text(encoding='utf-8')
        parser = SpanishPage(catalog)
        parser.feed(source)
        missing.update(parser.missing)
        translated = ''.join(parser.parts)
        translated = translated.replace('<main id="main">', '<main id="main"><p class="translation-note">Versión en español. El código, los datos, las salidas calculadas y las etiquetas dentro de las figuras se conservan en su idioma original. Los cuadernos descargables están en inglés.</p>', 1)
        (destination / path.name).write_text(add_language_links(translated, path.name, True), encoding='utf-8')
        path.write_text(add_language_links(source, path.name), encoding='utf-8')
    if missing:
        raise ValueError('Missing Spanish translations:\n' + '\n'.join(sorted(missing)))
    print(f'Built {len(list(destination.glob("*.html")))} Spanish pages; English remains the default')
