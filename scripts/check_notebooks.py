"""Execute every notebook in its own directory, preserving originals."""
from pathlib import Path
import os
import asyncio
import argparse
import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lecture", help="Check only a lecture folder, for example 08_deployment")
    arguments = parser.parse_args()
    output = ROOT / ".verification"
    output.mkdir(exist_ok=True)
    # Keep notebook runtime state inside this checkout, including on Windows.
    for variable, directory in {
        "IPYTHONDIR": "ipython", "JUPYTER_RUNTIME_DIR": "runtime",
        "MPLCONFIGDIR": "matplotlib", "TEMP": "tmp", "TMP": "tmp",
    }.items():
        location = output / directory
        location.mkdir(exist_ok=True)
        os.environ[variable] = str(location)
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    pattern = f"{arguments.lecture}/*.ipynb" if arguments.lecture else "*/*.ipynb"
    paths = sorted((ROOT / "lectures").glob(pattern))
    if not paths:
        parser.error("No notebooks matched the selected lecture")
    for path in paths:
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)
        NotebookClient(notebook, timeout=300, kernel_name="python3",
                       resources={"metadata": {"path": str(path.parent)}}).execute()
        nbformat.write(notebook, output / f"{path.parent.name}_{path.name}")
        print(f"PASS {path.relative_to(ROOT)}", flush=True)
