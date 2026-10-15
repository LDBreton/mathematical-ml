"""Generate local synthetic datasets used by lectures 04 and 06."""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

def generate(destination: Path = ROOT / "data") -> None:
    """Write deterministic fraud and customer-segmentation CSV fixtures."""
    destination.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(404)
    n = 5000
    amount = rng.lognormal(3.45, 0.85, n).clip(2, 1800)
    hour = rng.integers(0, 24, n)
    card_present = rng.binomial(1, 0.72, n)
    international = rng.binomial(1, 0.11, n)
    account_age_days = rng.integers(3, 3651, n)
    transactions_24h = rng.poisson(1.5, n)
    merchant_risk = rng.beta(2, 5, n)
    night = ((hour <= 5) | (hour >= 23)).astype(int)
    eta = (-4.35 + 0.58 * np.log1p(amount / 40) + 0.82 * international
           + 0.72 * (1 - card_present) + 0.43 * night
           + 0.16 * transactions_24h + 1.15 * merchant_risk
           - 0.12 * np.log1p(account_age_days / 90))
    probability = 1 / (1 + np.exp(-eta))
    fraud = rng.binomial(1, probability)
    fraud_frame = pd.DataFrame({
        "amount": amount,
        "hour": hour,
        "card_present": card_present,
        "international": international,
        "account_age_days": account_age_days,
        "transactions_24h": transactions_24h,
        "merchant_risk": merchant_risk,
        "fraud": fraud,
    })
    fraud_frame.round(5).to_csv(destination / "fraud.csv", index=False)

    rng = np.random.default_rng(606)
    group_sizes = [320, 300, 300, 280]
    group_centers = [
        (78, 2.2, 180, 470, 0.20, 30),
        (30, 10.5, 360, 980, 0.62, 22),
        (115, 1.4, 95, 260, 0.35, 48),
        (18, 16.0, 520, 1450, 0.78, 9),
    ]
    segment_truth = np.concatenate([
        np.full(size, group) for group, size in enumerate(group_sizes)
    ])
    rng.shuffle(segment_truth)
    values = np.empty((len(segment_truth), 7))
    for group, center in enumerate(group_centers):
        recency, frequency, monetary, annual, web_share, tenure = center
        in_group = segment_truth == group
        count = int(in_group.sum())
        recency_sd = 6 if group == 3 else 12
        values[in_group, 0] = rng.normal(recency, recency_sd, count)
        values[in_group, 1] = rng.poisson(frequency, count)
        values[in_group, 2] = rng.lognormal(np.log(monetary), 0.27, count)
        values[in_group, 3] = rng.lognormal(np.log(annual), 0.22, count)
        beta_a = max(1.2, web_share * 12)
        beta_b = max(1.2, (1 - web_share) * 12)
        values[in_group, 4] = rng.beta(beta_a, beta_b, count)
        values[in_group, 5] = rng.normal(tenure, 8, count)
        values[in_group, 6] = rng.poisson(0.6 + 0.12 * frequency, count)

    customers = pd.DataFrame(values, columns=[
        "recency_days", "orders_12m", "average_order_value", "annual_spend",
        "web_share", "tenure_months", "support_contacts_12m",
    ])
    customers["recency_days"] = customers["recency_days"].clip(1, 180).round().astype(int)
    customers["orders_12m"] = customers["orders_12m"].clip(0).round().astype(int)
    customers["average_order_value"] = customers["average_order_value"].clip(10).round(2)
    customers["annual_spend"] = customers["annual_spend"].clip(20).round(2)
    customers["web_share"] = customers["web_share"].clip(0, 1).round(4)
    customers["tenure_months"] = customers["tenure_months"].clip(1, 72).round().astype(int)
    customers["support_contacts_12m"] = customers["support_contacts_12m"].clip(0).round().astype(int)
    customers["segment_truth"] = segment_truth
    customers.to_csv(destination / "customer_segments.csv", index=False)
if __name__ == "__main__":
    generate()
