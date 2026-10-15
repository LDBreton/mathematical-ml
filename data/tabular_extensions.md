# Tabular extension datasets

Both files are synthetic, deterministic teaching fixtures. Regenerate the CSVs from the repository root with `.venv/Scripts/python.exe scripts/generate_tabular_extensions.py`. The fraud and customer generators use independent NumPy random generators with seeds 404 and 606. The generator writes only the two CSV files; this note documents their committed versions.

Monetary features use arbitrary currency units. The merchant-risk score is an artificial predictor, not an externally validated probability.

## `fraud.csv`

The table has 5,000 independent transaction scenarios. NumPy lognormal parameters below are the mean and standard deviation of the underlying normal variable. Amount is clipped to [2, 1800]; continuous fields are rounded to five decimals in the CSV.

| Column | Synthetic generation |
|---|---|
| `amount` | LogNormal(3.45, 0.85), clipped to [2, 1800] |
| `hour` | Uniform integer from 0 through 23 |
| `card_present` | Bernoulli(0.72) |
| `international` | Bernoulli(0.11) |
| `account_age_days` | Uniform integer from 3 through 3650 |
| `transactions_24h` | Poisson(1.5) |
| `merchant_risk` | Beta(2, 5) |
| `fraud` | Bernoulli with probability below |

Let `night` equal one when `hour <= 5` or `hour >= 23`. The label probability is $\sigma(\eta)=1/(1+e^{-\eta})$, with

$$
\eta=-4.35+0.58\log(1+\mathrm{amount}/40)+0.82\,\mathrm{international}+0.72(1-\mathrm{card\_present})+0.43\,\mathrm{night}+0.16\,\mathrm{transactions\_24h}+1.15\,\mathrm{merchant\_risk}-0.12\log(1+\mathrm{account\_age\_days}/90).
$$

The committed seed-404 sample has 217 positives among 5,000 rows (4.34%). Split before any resampling or fitted preprocessing; the lessons do not resample.

## `customer_segments.csv`

This table has 1,200 rows and four hidden generator groups. Feature centers are shown in original units. Values are sampled independently conditional on group using the distributions below, then clipped and rounded. In particular, annual spend is generated independently of order count and average order value, so these fields are artificial feature proxies rather than an accounting-consistent transaction ledger.

| `segment_truth` | Rows | Recency days | Orders / 12 months | Average order value | Annual spend | Web share | Tenure months |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 320 | 78 | 2.2 | 180 | 470 | 0.20 | 30 |
| 1 | 300 | 30 | 10.5 | 360 | 980 | 0.62 | 22 |
| 2 | 300 | 115 | 1.4 | 95 | 260 | 0.35 | 48 |
| 3 | 280 | 18 | 16 | 520 | 1450 | 0.78 | 9 |

| Feature | Conditional distribution and stored range |
|---|---|
| `recency_days` | Normal(center, SD 12; group 3 uses SD 6), clipped to [1, 180], rounded to integer |
| `orders_12m` | Poisson(group center), clipped below at 0, integer |
| `average_order_value` | LogNormal(log(center), 0.27), clipped below at 10, rounded to cents |
| `annual_spend` | LogNormal(log(center), 0.22), clipped below at 20, rounded to cents |
| `web_share` | Beta(max(1.2, 12q), max(1.2, 12(1-q))), clipped to [0, 1], rounded to 4 decimals |
| `tenure_months` | Normal(center, SD 8), clipped to [1, 72], rounded to integer |
| `support_contacts_12m` | Poisson(0.6 + 0.12 times group order center), clipped below at 0, integer |

`segment_truth` records the generator group for post-hoc ARI analysis only. Exclude it from scaling, PCA, K-means, silhouette, and cluster-count selection. No real or personal records are included, and the synthetic relationships do not justify real decisions.
