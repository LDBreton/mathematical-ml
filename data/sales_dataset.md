# Synthetic daily sales dataset

`daily_sales.csv` is a deterministic, synthetic teaching series. It contains 1,000 consecutive daily rows from 2023-01-01. `date` is the calendar date and `sales` is the simulated daily quantity. It contains no real company or customer data.

The generator is `scripts/generate_sales_data.py`. It uses NumPy's `default_rng(202607)` and, for day index $t=0,\ldots,999$, generates

$$Y_t=1000+0.16t+105\cos\!\left(2\pi\frac{d_t-5}{7}\right)+55\sin\!\left(2\pi\frac{t}{365.25}-0.8\right)+\epsilon_t,$$

where $d_t$ is the weekday index with Monday equal to 0, and independently $\epsilon_t\sim\mathcal N(0,58^2)$. The stored response is rounded to two decimal places. The weekly term creates higher weekend sales; the linear and annual terms provide smooth drift and seasonality. There are no promotion features.

Regenerate the file from the repository root with:

```powershell
.\.venv\Scripts\python.exe scripts\generate_sales_data.py
```

The lecture uses calendar variables known in advance and lag/rolling features computed only from past sales. The synthetic process is for instruction, not a realistic demand model or a claim about forecast performance in production.
