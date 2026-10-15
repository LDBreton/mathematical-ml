"""Verify that generators reproduce the committed classroom CSV bytes locally."""
from pathlib import Path
import hashlib
import tempfile

from generate_data import generate as generate_original
from generate_tabular_extensions import generate as generate_tabular
from generate_text_data import generate as generate_text
from generate_sales_data import generate as generate_sales

ROOT = Path(__file__).resolve().parents[1]


if __name__ == "__main__":
    workspace = ROOT / ".verification"
    workspace.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=workspace) as temporary:
        destination = Path(temporary)
        for generator in [generate_original, generate_tabular, generate_text, generate_sales]:
            generator(destination)
        generated = sorted(destination.glob("*.csv"))
        committed = sorted((ROOT / "data").glob("*.csv"))
        if [path.name for path in generated] != [path.name for path in committed]:
            raise SystemExit("Generated filenames differ from the classroom fixtures")
        for path in generated:
            expected = ROOT / "data" / path.name
            actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            expected_hash = hashlib.sha256(expected.read_bytes()).hexdigest()
            if actual_hash != expected_hash:
                raise SystemExit(
                    f"Dataset mismatch: {path.name}. Compare numerical-library versions "
                    "and generation inputs; do not overwrite the fixture automatically."
                )
            print(f"PASS {path.name}")
