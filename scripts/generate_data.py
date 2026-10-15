"""Generate small, deterministic teaching datasets; no downloads or private data."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def generate(destination: Path = ROOT / "data") -> None:
    destination.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(42)
    n = 1200
    area = rng.uniform(35, 220, n)
    bedrooms = rng.integers(1, 6, n)
    age = rng.uniform(0, 70, n)
    distance = rng.uniform(0, 30, n)
    neighborhood = rng.choice(["central", "residential", "outer"], n)
    premium = pd.Series(neighborhood).map({"central": 90000, "residential": 35000, "outer": 0}).to_numpy()
    price = 50000 + 2400 * area + 12000 * bedrooms - 900 * age - 1800 * distance + premium + rng.normal(0, 25000, n)
    housing = pd.DataFrame(dict(area_m2=area, bedrooms=bedrooms, age_years=age,
                                distance_km=distance, neighborhood=neighborhood, price=price))
    housing.loc[rng.choice(n, 35, replace=False), "age_years"] = np.nan
    housing.round(4).to_csv(destination / "housing.csv", index=False)

    n = 1800
    tenure = rng.integers(1, 73, n)
    charge = rng.uniform(20, 140, n)
    calls = rng.poisson(1.4, n)
    contract = rng.choice(["monthly", "annual", "two_year"], n, p=[.55, .3, .15])
    effect = pd.Series(contract).map({"monthly": .9, "annual": -.4, "two_year": -1.1}).to_numpy()
    log_odds = -1.8 - .025 * tenure + .018 * (charge - 60) + .45 * calls + effect
    probability = 1 / (1 + np.exp(-log_odds))
    churn = rng.binomial(1, probability)
    pd.DataFrame(dict(tenure_months=tenure, monthly_charge=charge, support_calls=calls,
                      contract=contract, churn=churn)).round(4).to_csv(destination / "churn.csv", index=False)

    n = 2000
    temperature = rng.uniform(0, 35, n)
    humidity = rng.uniform(20, 95, n)
    wind = rng.uniform(0, 35, n)
    hour = rng.integers(0, 24, n)
    weekday = rng.integers(0, 7, n)
    season = rng.integers(0, 4, n)
    rush = 80 * np.exp(-((hour - 8) / 2) ** 2) + 110 * np.exp(-((hour - 17) / 2.5) ** 2)
    mean = np.maximum(5, 35 + 5 * temperature - .12 * (temperature - 23) ** 2
                      - .45 * humidity - .8 * wind + rush + 20 * (weekday >= 5) + 10 * season)
    rentals = rng.poisson(mean)
    pd.DataFrame(dict(temperature_c=temperature, humidity=humidity, wind_kmh=wind,
                      hour=hour, weekday=weekday, season=season, rentals=rentals)).round(4).to_csv(destination / "bike_demand.csv", index=False)


if __name__ == "__main__":
    generate()
