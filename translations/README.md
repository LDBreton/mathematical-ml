# Website languages

English is the default at the site root. Spanish reading pages live under `es/`.
The language links preserve the page and current section; no browser-locale or
saved-preference redirect changes the default.

The four `es/*.json` catalogs map exact English text segments to reviewed Spanish
translations. Keep keys unchanged. Equations, API names and filenames remain
unchanged. Code, captured outputs, downloadable notebooks, dataset text and image
labels retain their original language; Spanish pages explain this explicitly.

After editing English content, add matching translations. The website build fails
on missing segments rather than silently showing untranslated prose. HTML links,
IDs and layout remain shared. Run:

```console
python scripts/build_site.py
python scripts/check_site.py
python scripts/check_localization.py
```

Localization checks compare equations, code and output blocks in
each page pair, language metadata and links. The normal website checker covers
both language trees, including anchors and downloads. No translation service or
browser extension is required at runtime.
