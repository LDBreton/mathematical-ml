"""Export checked lesson outputs for static reading; run after check_notebooks.py.

The website build requires these committed snapshots to match current teaching
sources and data. It never executes notebooks during a Pages deployment.
"""
import base64
import hashlib
import json
from pathlib import Path
import platform

import nbformat

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "docs/results"


def source_hashes():
    paths = list((ROOT / "data").glob("*.csv"))
    paths += list((ROOT / "src/course_ml").glob("*.py"))
    paths += list((ROOT / "lectures").glob("*/lesson.ipynb"))
    # Normalize line endings because Git checkouts may use CRLF on Windows.
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(
        p.read_bytes().replace(b"\r\n", b"\n")).hexdigest() for p in sorted(paths)}


def export():
    import numpy
    import pandas
    import sklearn
    import xgboost
    DESTINATION.mkdir(exist_ok=True)
    lessons = {}
    for source in sorted((ROOT / "lectures").glob("*/lesson.ipynb")):
        name = source.parent.name
        executed_path = ROOT / ".verification" / f"{name}_lesson.ipynb"
        original = nbformat.read(source, as_version=4)
        executed = nbformat.read(executed_path, as_version=4)
        if [(c.cell_type, c.source) for c in original.cells] != [
            (c.cell_type, c.source) for c in executed.cells
        ]:
            raise ValueError(f"Execute current lesson before exporting: {name}")
        items = []
        heading = "Lesson results"
        for cell in executed.cells:
            if cell.cell_type == "markdown":
                headings = [line.lstrip("# ") for line in cell.source.splitlines()
                            if line.startswith("## ")]
                if headings:
                    heading = headings[-1]
                continue
            if cell.cell_type != "code" or cell.execution_count is None:
                if cell.cell_type == "code":
                    raise ValueError(f"Unexecuted cell: {name}/{cell.id}")
                continue
            for index, output in enumerate(cell.get("outputs", [])):
                if output.output_type == "error":
                    raise ValueError(f"Execution error: {name}/{cell.id}")
                item = {"cell_id": cell.id, "heading": heading}
                data = output.get("data", {})
                if "image/png" in data:
                    filename = f"{name}-{cell.id}-{index}.png"
                    (DESTINATION / filename).write_bytes(base64.b64decode(data["image/png"]))
                    item["image"] = filename
                elif output.output_type == "stream" and output.get("name") == "stdout":
                    item["text"] = output.text
                elif "text/plain" in data:
                    item["text"] = data["text/plain"]
                else:
                    continue
                items.append(item)
        lessons[name] = items
    manifest = {
        "format": 1, "description": "Outputs from successful local lesson execution on synthetic course data.",
        "source_hashes": source_hashes(),
        "versions": {"python": platform.python_version(), "numpy": numpy.__version__,
                     "pandas": pandas.__version__, "scikit_learn": sklearn.__version__,
                     "xgboost": xgboost.__version__},
        "lessons": lessons,
    }
    (DESTINATION / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Exported {sum(len(v) for v in lessons.values())} outputs from {len(lessons)} executed lessons")


if __name__ == "__main__":
    export()
