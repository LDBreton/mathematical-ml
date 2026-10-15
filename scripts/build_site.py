"""Render the course's Markdown and notebooks as a local static website."""
from pathlib import Path
import html
import re
import shutil
import zipfile
import markdown
import nbformat

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
LECTURES = [
    ("01_regression", "01", "Regression", "Projection, empirical risk, and prediction"),
    ("02_classification", "02", "Classification", "Likelihood, probabilities, and decisions"),
    ("03_xgboost", "03", "XGBoost", "Additive trees and second-order optimization"),
    ("04_imbalanced_learning", "04", "Imbalanced learning", "Rare events, precision–recall, and alert costs"),
    ("05_text_classification", "05", "Text classification", "Sparse vectors, language features, and group-aware evaluation"),
    ("06_clustering", "06", "Clustering", "Centroids, principal components, and customer segmentation"),
    ("07_time_series", "07", "Time-series forecasting", "Lagged information and rolling-origin prediction"),
    ("08_deployment", "08", "From model to service", "Reproducible training and validated inference"),
]
CSS = '''
:root{--paper:#f5f2e9;--ink:#182d32;--teal:#16675f;--line:#d5d9cc;--muted:#536667}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.7 system-ui,sans-serif}a{color:var(--teal);text-underline-offset:4px}header{border-bottom:1px solid var(--line);padding:20px 5%;display:flex;gap:25px;justify-content:space-between}header a{text-decoration:none;font-weight:650}nav{display:flex;gap:22px;flex-wrap:wrap}main{max-width:1120px;margin:auto;padding:50px 28px}h1,h2,h3{line-height:1.18}h1{font-family:Georgia,serif;font-weight:400;font-size:clamp(40px,6vw,72px);max-width:850px;margin:20px 0}h2{font-size:28px;margin-top:40px}.eyebrow{text-transform:uppercase;letter-spacing:.16em;font-size:12px;color:var(--teal);font-weight:700}.intro{font-size:21px;max-width:760px;color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:20px;margin-top:40px}.card{border:1px solid var(--line);background:#fffdf7;padding:28px;border-radius:4px}.number{font:italic 38px Georgia;color:var(--teal)}.card h2{margin:8px 0 14px}.card p{color:var(--muted)}.actions{display:flex;gap:20px;flex-wrap:wrap}.button{display:inline-block;padding:10px 18px;background:var(--teal);color:white;text-decoration:none;border-radius:3px}.note{padding:22px;border-left:4px solid var(--teal);background:#e7ece2;margin:30px 0}.reading{max-width:850px}pre{background:#152c32;color:#eaf2ee;padding:22px;overflow-x:auto;border-radius:4px;font-size:14px;line-height:1.6}code{font-family:Consolas,monospace}p code,li code{background:#e5e9df;padding:2px 5px}table{border-collapse:collapse;width:100%;display:block;overflow:auto}td,th{border-bottom:1px solid var(--line);padding:10px;text-align:left}.cell{margin:30px 0}.cell-label{font-size:12px;text-transform:uppercase;letter-spacing:.1em;color:var(--muted)}footer{max-width:1120px;margin:auto;padding:30px;border-top:1px solid var(--line);color:var(--muted);font-size:14px}.search{width:100%;max-width:520px;padding:13px;border:1px solid var(--line);font:inherit;background:#fffdf7}.skip{position:absolute;left:-9999px}.skip:focus{left:20px;top:10px;background:white;padding:10px}[hidden]{display:none!important}@media(max-width:680px){.grid{grid-template-columns:1fr}header{flex-direction:column}main{padding:30px 20px}}
'''


def render_markdown(source: str) -> str:
    """Protect TeX from Markdown's underscore and escape processing."""
    expressions = []
    def protect(match):
        expressions.append(html.escape(match.group(0)))
        return f"MATHPLACEHOLDER{len(expressions)-1}TOKEN"
    source = re.sub(r"\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)|(?<!\$)\$(?!\$)[^\n$]+\$", protect, source)
    rendered = markdown.markdown(source, extensions=["fenced_code", "tables"])
    for index, expression in enumerate(expressions):
        rendered = rendered.replace(f"MATHPLACEHOLDER{index}TOKEN", expression)
    return rendered


def page(title: str, body: str) -> str:
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>''' + html.escape(title) + ''' · Mathematical ML</title><link rel="stylesheet" href="style.css"><script>window.MathJax={tex:{inlineMath:[['$','$'],['\\\\(','\\\\)']]}};</script><script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script></head><body><a class="skip" href="#main">Skip to content</a><header><a href="index.html">∑ Mathematical ML</a><nav aria-label="Course"><a href="index.html#lectures">Lectures</a><a href="setup.html">Getting started</a><a href="datasets.html">Datasets</a><a href="instructor.html">Teaching guide</a></nav></header><main id="main">''' + body + '''</main><footer>Eight practical lectures for mathematicians · Local, reproducible, CPU-friendly · Synthetic teaching data</footer></body></html>'''


def rewrite_links(body: str, folder: str | None = None) -> str:
    body = body.replace('href="../../README.md"', 'href="setup.html"')
    for directory, _, _, _ in LECTURES:
        body = body.replace(f'lectures/{directory}/README.md', f'{directory}.html')
    body = body.replace('data/README.md', 'datasets.html').replace('docs/instructor-guide.md', 'instructor.html')
    body = body.replace('docs/verification.md', 'verification.html')
    body = body.replace('docs/course-project.md', 'course-project.html')
    for source, rendered in [
        ("tabular_extensions.md", "tabular-data.html"),
        ("text_dataset.md", "text-data.html"),
        ("sales_dataset.md", "sales-data.html"),
    ]:
        body = body.replace(f'href="{source}"', f'href="{rendered}"')
        body = body.replace(f'href="../../data/{source}"', f'href="{rendered}"')
    if folder:
        for kind in ["lesson", "exercises", "solutions"]:
            body = body.replace(f'href="{kind}.ipynb"', f'href="{folder}-{kind}.html"')
    return body


def lecture_navigation(folder: str) -> str:
    """Keep the study sequence visible on lesson and notebook pages."""
    index = next(i for i, lecture in enumerate(LECTURES) if lecture[0] == folder)
    links = ['<a href="index.html#lectures">All lectures</a>']
    if index > 0:
        previous, number, title, _ = LECTURES[index - 1]
        links.insert(0, f'<a href="{previous}.html">← {number}: {title}</a>')
    if index + 1 < len(LECTURES):
        following, number, title, _ = LECTURES[index + 1]
        links.append(f'<a href="{following}.html">{number}: {title} →</a>')
    return '<nav class="actions" aria-label="Study sequence">' + "".join(links) + '</nav>'


def build() -> None:
    SITE.mkdir(exist_ok=True)
    (SITE / "style.css").write_text(CSS, encoding="utf-8")
    cards = []
    for folder, number, title, description in LECTURES:
        source = ROOT / "lectures" / folder
        target = SITE / "downloads" / folder
        target.mkdir(parents=True, exist_ok=True)
        links = []
        for kind in ["lesson", "exercises", "solutions"]:
            notebook = nbformat.read(source / f"{kind}.ipynb", as_version=4)
            cells = []
            for cell in notebook.cells:
                if cell.cell_type == "markdown":
                    content = render_markdown(cell.source)
                elif cell.cell_type == "code":
                    content = '<div class="cell-label">Python · run in the notebook</div><pre><code>' + html.escape(cell.source) + '</code></pre>'
                else:
                    continue
                cells.append(f'<section class="cell">{content}</section>')
            filename = f"{folder}-{kind}.html"
            download = f"downloads/{folder}/{kind}.ipynb"
            body = f'<div class="eyebrow">Lecture {number} / {kind}</div><div class="actions"><a href="{folder}.html">← Lecture guide</a><a href="{download}" download>Download notebook</a></div><article class="reading">' + "".join(cells) + '</article>'
            body += lecture_navigation(folder)
            (SITE / filename).write_text(page(f"{title}: {kind}", body), encoding="utf-8")
            shutil.copy2(source / f"{kind}.ipynb", target)
            links.append(f'<a class="button" href="{filename}">{kind.title()}</a>')
        guide = rewrite_links(render_markdown((source / "README.md").read_text(encoding="utf-8")), folder)
        body = f'<div class="eyebrow">Lecture {number}</div><h1>{title}</h1><p class="intro">{description}</p><div class="actions">' + "".join(links) + f'</div><article class="reading">{guide}</article>'
        body += lecture_navigation(folder)
        (SITE / f"{folder}.html").write_text(page(title, body), encoding="utf-8")
        cards.append(f'<article class="card" data-search="{html.escape((title+description).lower())}"><div class="number">{number}</div><h2>{title}</h2><p>{description}</p><a href="{folder}.html">Open lecture →</a></article>')
    route = " → ".join(number for _, number, _, _ in LECTURES)
    body = """
<div class="eyebrow">A hands-on course / Python + mathematics</div>
<h1>From mathematical models<br>to machine learning.</h1>
<p class="intro">Understand the objective. Read the implementation. Test the assumptions.
Eight guided lectures connect familiar mathematics to a working prediction service.</p>
<div class="actions">
  <a class="button" href="setup.html">Set up your environment</a>
  <a href="01_regression.html">Begin with regression →</a>
</div>
<div class="note"><strong>Your route: ROUTE.</strong>
Each lecture includes theory, runnable Python, exercises, and worked solutions.
Start with basic Python, linear algebra, calculus, and probability. No GPU or service account required.</div>
<h2 id="lectures">Explore the lectures</h2>
<label for="search">Filter by topic</label><br>
<input class="search" id="search" type="search" placeholder="Try likelihood, trees, or service">
<div class="grid">CARDS</div>
<p id="empty" hidden>No matching lectures. Try a broader term.</p>
<h2>Make the assumptions explicit</h2>
<p class="intro">The datasets come from documented equations. Compare what the model learns
with the mechanism that generated the observations—and explain where your conclusions stop.</p>
<a href="course-project.html">Finish with the course project →</a>
<script>
document.querySelector('#search').addEventListener('input', event => {
  const query = event.target.value.toLowerCase().trim();
  let count = 0;
  document.querySelectorAll('.card').forEach(card => {
    card.hidden = !card.dataset.search.includes(query);
    if (!card.hidden) count++;
  });
  document.querySelector('#empty').hidden = count !== 0;
});
</script>
""".replace("ROUTE", route).replace("CARDS", "".join(cards))
    (SITE / "index.html").write_text(page("Machine learning for mathematicians", body), encoding="utf-8")
    information_pages = [
        ("setup.html", ROOT / "README.md"),
        ("datasets.html", ROOT / "data/README.md"),
        ("instructor.html", ROOT / "docs/instructor-guide.md"),
        ("verification.html", ROOT / "docs/verification.md"),
        ("course-project.html", ROOT / "docs/course-project.md"),
        ("tabular-data.html", ROOT / "data/tabular_extensions.md"),
        ("text-data.html", ROOT / "data/text_dataset.md"),
        ("sales-data.html", ROOT / "data/sales_dataset.md"),
    ]
    for filename, source in information_pages:
        body = rewrite_links(render_markdown(source.read_text(encoding="utf-8")))
        if filename == "datasets.html":
            for csv in sorted((ROOT / "data").glob("*.csv")):
                shutil.copy2(csv, SITE / "downloads" / csv.name)
                body += f'<p><a href="downloads/{csv.name}" download>Download {csv.name}</a></p>'
        if filename == "setup.html":
            body = '<p><a class="button" href="downloads/course.zip" download>Download the complete course</a></p>' + body
        if filename == "verification.html":
            shutil.copy2(ROOT / "docs/course-preview.png", SITE / "course-preview.png")
        (SITE / filename).write_text(page(source.stem, f'<article class="reading">{body}</article>'), encoding="utf-8")
    # Bundle only authored teaching sources, never local environments or runtime state.
    files = [ROOT / name for name in ["README.md", "pyproject.toml", "requirements-lock.txt", "Dockerfile", ".dockerignore", ".gitignore", "CONTRIBUTING.md"]]
    for directory in ["lectures", "data", "src", "tests", "scripts", "docs", ".github"]:
        files.extend(p for p in (ROOT / directory).rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    with zipfile.ZipFile(SITE / "downloads/course.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(files):
            archive.write(path, path.relative_to(ROOT))
    print(f"Built navigator: {SITE / 'index.html'}")


if __name__ == "__main__":
    build()
