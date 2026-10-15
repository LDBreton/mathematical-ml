"""Generate the deterministic synthetic daily sales series used in lecture 07."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def generate(destination: Path = ROOT / "data") -> None:
    """Write 1,000 synthetic daily observations using an independent fixed RNG."""
    destination.mkdir(parents=True, exist_ok=True)
    n = 1000
    dates = pd.date_range("2023-01-01", periods=n, freq="D")
    day_index = np.arange(n, dtype=float)
    rng = np.random.default_rng(202607)
    weekday = dates.dayofweek.to_numpy()
    weekly = 105.0 * np.cos(2 * np.pi * (weekday - 5) / 7)
    annual = 55.0 * np.sin(2 * np.pi * day_index / 365.25 - 0.8)
    trend = 0.16 * day_index
    noise = rng.normal(0.0, 58.0, size=n)
    sales = 1000.0 + trend + weekly + annual + noise
    frame = pd.DataFrame({"date": dates.strftime("%Y-%m-%d"), "sales": np.round(sales, 2)})
    frame.to_csv(destination / "daily_sales.csv", index=False)


if __name__ == "__main__":
    generate()
