"""Give every cell a stable ID and keep authored notebooks output-free."""
from pathlib import Path
import nbformat

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    for path in sorted((ROOT / "lectures").glob("*/*.ipynb")):
        # Read JSON directly to supply IDs before nbformat validation warns.
        import json
        raw = json.loads(path.read_text(encoding="utf-8"))
        raw["nbformat_minor"] = 5
        for index, cell in enumerate(raw["cells"]):
            cell["id"] = f"cell-{index:03d}"
            if cell["cell_type"] == "code":
                cell["execution_count"] = None
                cell["outputs"] = []
        notebook = nbformat.from_dict(raw)
        nbformat.validate(notebook)
        nbformat.write(notebook, path)
