"""Render the course's Markdown and notebooks as a local static website."""
from pathlib import Path
import html
import re
import shutil
import zipfile
import json
import markdown
import nbformat
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer, get_lexer_by_name
from pygments.util import ClassNotFound
from export_lesson_results import source_hashes

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
CSS = (ROOT / "scripts/site.css").read_text(encoding="utf-8")
SCRIPT = (ROOT / "scripts/site.js").read_text(encoding="utf-8")
RESULT_GUIDANCE = {
    "01_regression": "Compare Ridge with both constant baselines, then inspect residual structure and the transformed feature columns. Metric units are price units.",
    "02_classification": "Compare ranking, calibration, and thresholded decisions. Inspect validation-bin counts before interpreting deviations from the reliability diagonal.",
    "03_xgboost": "Follow residual-tree stages and validation early stopping, then compare the frozen models on the same test rows. The hand split calculation is an illustrative numerical check.",
    "04_imbalanced_learning": "Compare validation cost with alert workload. In the final test table, compare every frozen policy with the always-negative policy using the same cost units.",
    "05_text_classification": "Inspect the tiny executed TF-IDF matrix before reading the held-out template-family results. New-message probes demonstrate behavior; they are not an independent accuracy estimate.",
    "06_clustering": "Start with the selected-k plots below: they show the exact silhouette-selected fit. The earlier k=4 plot is an initial illustration. Cluster IDs are nominal, and PCA can hide separation in other dimensions.",
    "07_time_series": "Check the chronological boundaries and forecast-row alignment, then compare seasonal naive and XGBoost on the same one-step targets. Preserve the baseline comparison even when the more complex model loses.",
    "08_deployment": "Trace the validation-selected cutoff into the saved artifact and compare identical probabilities before saving, after loading, and through the API. HTTP correctness and predictive quality are separate checks.",
}


def highlighted_code(source: str, language: str = "python") -> str:
    """Highlight at build time: no JavaScript, CDN, or network required."""
    try:
        lexer = get_lexer_by_name(language)
    except ClassNotFound:
        return '<pre><code>' + html.escape(source) + '</code></pre>'
    return highlight(source, lexer, HtmlFormatter(cssclass="highlight"))


def render_output(item: dict) -> str:
    if "image" in item:
        return ('<figure class="result-figure"><img loading="lazy" src="results/'
                + html.escape(item["image"]) + '" alt="Executed result: '
                + html.escape(item["heading"], quote=True) + '"><figcaption>'
                + html.escape(item["heading"]) + ' · captured notebook output</figcaption></figure>')
    return '<details class="result-text"><summary>' + html.escape(item["heading"]) + ' · computed output</summary><pre>' + html.escape(item["text"]) + '</pre></details>'



def render_markdown(source: str) -> str:
    """Protect TeX from Markdown's underscore and escape processing."""
    expressions = []
    def protect(match):
        expressions.append(html.escape(match.group(0)))
        return f"MATHPLACEHOLDER{len(expressions)-1}TOKEN"
    source = re.sub(r"\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)|(?<!\$)\$(?!\$)[^\n$]+\$", protect, source)
    rendered = markdown.markdown(source, extensions=["fenced_code", "tables"])
    def highlight_fence(match):
        return highlighted_code(html.unescape(match.group(2)), match.group(1) or "text")
    rendered = re.sub(r'<pre><code(?: class="language-([^" ]+)")?>([\s\S]*?)</code></pre>', highlight_fence, rendered)
    for index, expression in enumerate(expressions):
        rendered = rendered.replace(f"MATHPLACEHOLDER{index}TOKEN", expression)
    return rendered


def page(title: str, body: str) -> str:
    navigation = '<a href="index.html">Course overview</a><h3>Start here</h3><a href="setup.html">Installation &amp; first steps</a>'
    navigation += '<a href="first-steps.html">New to ML? Start here</a><h3>The lectures</h3>'
    for folder, number, name, _ in LECTURES:
        navigation += f'<details><summary><a href="{folder}.html">{number} · {name}</a></summary>'
        for kind in ["lesson", "exercises", "solutions"]:
            navigation += f'<a class="sub" href="{folder}-{kind}.html">{kind.title()}</a>'
        navigation += '</details>'
    navigation += '<h3>Resources</h3><a href="results.html">Executed result galleries</a><a href="datasets.html">Datasets</a><a href="course-project.html">Course project</a><a href="instructor.html">Teaching guide</a><a href="verification.html">Verification</a>'
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Eight guided machine learning lectures for mathematicians: theory, readable Python, exercises and worked solutions."><title>{html.escape(title)} · Mathematical ML</title><link rel="stylesheet" href="style.css"><script defer src="site.js"></script><script>window.MathJax={{tex:{{inlineMath:[['$','$'],['\\\\(','\\\\)']]}}}};</script><script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script></head><body><a class="skip" href="#main">Skip to content</a><header><button class="menu" aria-controls="sidebar" aria-expanded="false" aria-label="Toggle course navigation">☰</button><a class="brand" href="index.html">∑ <span>Mathematical ML</span></a><nav aria-label="Quick links"><a href="setup.html">Get started</a><a href="index.html#lectures">Lectures</a><button id="theme" aria-label="Switch color theme">◐</button></nav></header><div class="layout"><aside id="sidebar" aria-label="Course navigation">{navigation}</aside><main id="main">{body}</main></div><footer>Mathematical ML · Eight practical lectures for mathematicians<br>Readable Python · Reproducible experiments · Synthetic teaching data</footer></body></html>'''


def rewrite_links(body: str, folder: str | None = None) -> str:
    body = body.replace('href="../../README.md"', 'href="setup.html"')
    body = body.replace('href="../README.md"', 'href="setup.html"')
    body = body.replace('../lectures/', 'lectures/')
    for directory, _, _, _ in LECTURES:
        body = body.replace(f'lectures/{directory}/README.md', f'{directory}.html')
    body = body.replace('data/README.md', 'datasets.html').replace('docs/instructor-guide.md', 'instructor.html')
    body = body.replace('docs/verification.md', 'verification.html')
    body = body.replace('docs/course-project.md', 'course-project.html')
    body = body.replace('course-review.md', 'course-review.html')
    body = body.replace('../../docs/first-steps.md', 'first-steps.html')
    body = body.replace('docs/first-steps.md', 'first-steps.html')
    body = body.replace('../../docs/figures/', 'figures/')
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
    result_manifest = json.loads((ROOT / "docs/results/manifest.json").read_text(encoding="utf-8"))
    if result_manifest["source_hashes"] != source_hashes():
        raise ValueError("Result snapshots are stale. Execute notebooks, then run scripts/export_lesson_results.py")
    SITE.mkdir(exist_ok=True)
    (SITE / "style.css").write_text(CSS, encoding="utf-8")
    (SITE / "site.js").write_text(SCRIPT, encoding="utf-8")
    shutil.copytree(ROOT / "docs/figures", SITE / "figures", dirs_exist_ok=True)
    shutil.copytree(ROOT / "docs/results", SITE / "results", dirs_exist_ok=True)
    cards = []
    gallery_links = []
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
                    content = '<div class="cell-label">Python · run in the notebook</div>' + highlighted_code(cell.source)
                    if kind == "lesson":
                        content += ''.join(render_output(item) for item in result_manifest["lessons"][folder]
                                           if item["cell_id"] == cell.id)
                else:
                    continue
                cells.append(f'<section class="cell" id="cell-{html.escape(cell.id, quote=True)}">{content}</section>')
            filename = f"{folder}-{kind}.html"
            section_links = []
            def add_section(match):
                anchor = f"section-{len(section_links) + 1}"
                label = re.sub(r"<[^>]+>", "", match.group(2))
                section_links.append(f'<a href="#{anchor}">{label}</a>')
                return f'<h{match.group(1)} id="{anchor}">{match.group(2)}</h{match.group(1)}>'
            contents = re.sub(r"<h([23])>(.*?)</h\1>", add_section, "".join(cells))
            toc = '<details class="contents"><summary>On this page</summary><nav aria-label="Page contents">' + "".join(section_links) + '</nav></details>'
            download = f"downloads/{folder}/{kind}.ipynb"
            body = f'<div class="eyebrow">Lecture {number} / {kind}</div><div class="actions"><a href="{folder}.html">← Lecture guide</a><a href="{download}" download>Download notebook</a></div><p class="note">This page is a reading view. To execute Python, download the complete course and open this notebook in Jupyter. <a href="first-steps.html">First notebook walkthrough →</a></p>' + toc + '<article class="reading">' + rewrite_links(contents, folder) + '</article>'
            if kind == "lesson":
                body += f'<p><a href="{folder}-results.html">Explore this lecture’s executed result gallery →</a></p>'
                body += f'<p><a class="button" href="{folder}-exercises.html">Next: attempt the exercises →</a></p>'
            elif kind == "exercises":
                body += f'<p>After writing your own answers, <a href="{folder}-solutions.html">compare with the worked solutions →</a></p>'
            body += lecture_navigation(folder)
            (SITE / filename).write_text(page(f"{title}: {kind}", body), encoding="utf-8")
            shutil.copy2(source / f"{kind}.ipynb", target)
            links.append(f'<a class="button" href="{filename}">{kind.title()}</a>')
        guide = rewrite_links(render_markdown((source / "README.md").read_text(encoding="utf-8")), folder)
        links.append(f'<a href="{folder}-results.html">Executed results →</a>')
        body = f'<div class="eyebrow">Lecture {number}</div><h1>{title}</h1><p class="intro">{description}</p><div class="actions">' + "".join(links) + f'</div><article class="reading">{guide}</article>'
        body += lecture_navigation(folder)
        (SITE / f"{folder}.html").write_text(page(title, body), encoding="utf-8")
        gallery = (f'<div class="eyebrow">Lecture {number} / Executed results</div><h1>{title}: results</h1>'
                   '<p>Captured from a successful run of the supplied notebook on synthetic teaching data. '
                   'These are computed outputs, distinct from the conceptual illustrations. '
                   'Source and dataset hashes are checked during every website build.</p>'
                   f'<p><a href="{folder}-lesson.html">Read the explanation and implementation →</a></p>')
        gallery += '<p class="note"><strong>What to inspect.</strong> ' + RESULT_GUIDANCE[folder] + '</p>'
        figures = [item for item in result_manifest["lessons"][folder] if "image" in item]
        if folder == "06_clustering":
            figures.sort(key=lambda item: item["cell_id"] != "selected-clusters-code")
        computed = [item for item in result_manifest["lessons"][folder] if "text" in item]
        for index, item in enumerate(figures + computed):
            if index == 0 and figures:
                gallery += '<h2>Computed figures</h2>'
            if index == len(figures):
                gallery += '<h2>Tables and printed results</h2>'
            gallery += ('<section class="gallery-result">' + render_output(item)
                        + f'<a class="result-source" href="{folder}-lesson.html#cell-{html.escape(item["cell_id"], quote=True)}">Source cell and explanation →</a></section>')
        gallery += '<details class="contents"><summary>Execution environment and provenance</summary><pre>' + html.escape(json.dumps(result_manifest["versions"], indent=2)) + '</pre><a href="results/manifest.json">Source hashes and output manifest</a></details>'
        (SITE / f"{folder}-results.html").write_text(page(f"{title}: executed results", gallery), encoding="utf-8")
        gallery_links.append(f'<li><a href="{folder}-results.html">{number}: {title}</a></li>')
        cards.append(f'<article class="card" data-search="{html.escape((title+description).lower())}"><img class="card-image" src="figures/{folder}.svg" alt="{html.escape(title)} teaching illustration" loading="lazy" width="1000" height="430"><div class="number">{number}</div><h2>{title}</h2><p>{description}</p><a href="{folder}.html">Open lecture →</a></article>')
    route = " → ".join(number for _, number, _, _ in LECTURES)
    body = """
<section class="hero">
<div class="eyebrow">Mathematical ML · A practical course in Python</div>
<h1>Machine learning.<br><span>From equations to decisions.</span></h1>
<p class="intro">Turn linear algebra, probability, and optimization into working models.
Follow each mathematical idea into readable Python, test it on data, and understand what the result actually means.</p>
<div class="actions"><a class="button" href="first-steps.html">Start learning →</a><a class="button secondary" href="setup.html">Set up Python</a><a class="button secondary" href="downloads/course.zip" download>Download the course</a></div>
<p class="meta">8 lectures &nbsp; · &nbsp; 24 notebooks &nbsp; · &nbsp; 7 datasets &nbsp; · &nbsp; CPU-friendly</p>
<p><a href="results.html">See the experiments: plots, tables, and computed results →</a></p>
</section>
<figure class="course-figure"><img src="figures/course-atlas.svg" alt="Three learning tasks: a fitted response curve, a logistic probability curve with a threshold, and a two-dimensional view of clusters." width="1200" height="370"><figcaption>Three questions, three mathematical objects. Curves are illustrative; the cluster projection uses the supplied synthetic customer data.</figcaption></figure>
<section class="roadmap" aria-label="Learning roadmap">
<div class="eyebrow">An idea becomes an experiment</div><h2>Follow the mathematics into code.</h2>
<div class="stages"><div><span>01 / FORMULATE</span><strong>Choose an objective</strong><code>minimize empirical risk</code><p>Projection, likelihood,<br>regularization.</p></div><b aria-hidden="true">→</b><div><span>02 / LEARN</span><strong>Fit a model</strong><code>pipeline.fit(X, y)</code><p>Linear models, trees,<br>text, and clusters.</p></div><b aria-hidden="true">→</b><div><span>03 / QUESTION</span><strong>Test the assumptions</strong><code>evaluate on held-out data</code><p>Leakage, uncertainty,<br>costs, and drift.</p></div></div>
<p class="caption">A conceptual roadmap. Each lecture makes the objective, implementation, and evaluation explicit.</p></section>
<section class="orientation"><h2>A course built for mathematical minds</h2><p>You already know how to reason about an equation. Here you learn how to turn that reasoning into a reliable experiment.</p><div class="features"><div><h3>Understand the model</h3><p>Derive the objective and connect its assumptions to the quantities the code computes.</p></div><div><h3>Work through the details</h3><p>Run a guided notebook, change the experiment, then compare your work with explained solutions.</p></div><div><h3>Make a defensible decision</h3><p>Compare baselines, select metrics, and distinguish a good score from a useful model.</p></div></div></section>
<h2 id="lectures">Explore the lectures</h2>
<label for="search">Filter by topic</label><br>
<input class="search" id="search" type="search" placeholder="Try likelihood, trees, or service">
<div class="grid">CARDS</div>
<p id="empty" hidden>No matching lectures. Try a broader term.</p>
<section class="finish"><div class="eyebrow">Put it together</div><h2>One project. A complete learning workflow.</h2>
<p class="intro">The datasets come from documented equations. Compare what the model learns
with the mechanism that generated the observations—and explain where your conclusions stop.</p>
<a class="button" href="course-project.html">Explore the course project →</a></section><div class="note"><strong>Before you begin.</strong> Bring basic Python, linear algebra, calculus, and probability. Start at lecture 01 and work through 08. No GPU or service account is required. <a href="instructor.html">Teaching this course?</a></div>
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
    (SITE / "results.html").write_text(page("Executed result galleries", '<h1>See what the experiments produced.</h1><p>Explore actual outputs from all eight successfully executed lesson notebooks. Read each result beside its source code, assumptions, and interpretation. Random seeds and dependency versions affect numerical details; these synthetic results do not establish real-world accuracy.</p><ul>' + ''.join(gallery_links) + '</ul>'), encoding="utf-8")
    information_pages = [
        ("setup.html", ROOT / "README.md"),
        ("first-steps.html", ROOT / "docs/first-steps.md"),
        ("course-review.html", ROOT / "docs/course-review.md"),
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
