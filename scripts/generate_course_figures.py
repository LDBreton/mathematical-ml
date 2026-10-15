"""Generate reproducible teaching figures; no network or notebook execution required."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/figures"
OUT.mkdir(exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.labelcolor": "#173451", "text.color": "#173451",
                     "axes.titleweight": "bold", "svg.hashsalt": "mathematical-ml"})
BLUE, TEAL, GOLD = "#285b85", "#26938a", "#c47739"
rng = np.random.default_rng(42)


def save(fig, name):
    fig.tight_layout(pad=2)
    fig.savefig(OUT / f"{name}.svg", metadata={"Date": None}, facecolor="white")
    plt.close(fig)


# Illustrations are explicitly distinct from held-out course results.
x = np.linspace(-3, 3, 90)
y = np.sin(x) + rng.normal(0, .20, len(x))
grid = np.linspace(-3, 3, 400)
fig, ax = plt.subplots(figsize=(10, 4.3))
ax.scatter(x, y, color=BLUE, alpha=.5, s=24, label="Observed responses")
ax.plot(grid, np.sin(grid), color=TEAL, lw=3, label="Illustrative conditional mean")
ax.plot(grid, np.polyval(np.polyfit(x, y, 1), grid), color=GOLD, lw=2, label="Least-squares line")
ax.set(xlabel="Feature x", ylabel="Response y", title="Regression: choose a function, then measure its errors")
ax.legend(frameon=False, fontsize=9)
save(fig, "01_regression")

fig, ax = plt.subplots(figsize=(10, 4.3))
p = 1 / (1 + np.exp(-grid))
ax.plot(grid, p, color=BLUE, lw=3, label="Illustrative logistic probability")
ax.axhline(.5, color=GOLD, ls="--", label="Decision threshold = 0.5")
ax.fill_between(grid, 0, 1, where=grid > 0, alpha=.08, color=TEAL)
ax.set(xlabel="Linear score z", ylabel="P(Y = 1 | x)", ylim=(-.03, 1.03), title="Classification: a probability becomes a decision")
ax.legend(frameon=False, fontsize=9)
save(fig, "02_classification")

fig, ax = plt.subplots(figsize=(10, 4.3))
tree = DecisionTreeRegressor(max_depth=3, random_state=42).fit(x[:, None], y)
ax.scatter(x, y, color=BLUE, alpha=.35, s=20, label="Illustrative observations")
ax.plot(grid, tree.predict(grid[:, None]), color=GOLD, lw=3, label="One depth-3 regression tree")
ax.set(xlabel="Feature x", ylabel="Prediction", title="Trees: piecewise-constant building blocks for boosting")
ax.legend(frameon=False, fontsize=9)
save(fig, "03_xgboost")

fraud = pd.read_csv(ROOT / "data/fraud.csv")
counts = fraud.fraud.value_counts().reindex([0, 1])
fig, ax = plt.subplots(figsize=(10, 4.3))
bars = ax.barh(["Non-fraud", "Fraud"], counts, color=[BLUE, GOLD], height=.5)
ax.bar_label(bars, padding=8)
ax.set(xlim=(0, counts.max() * 1.17), xlabel="Rows in the complete teaching dataset", title="Rare events: accuracy can hide the class you care about")
save(fig, "04_imbalanced_learning")

texts = ["reset password account", "payment invoice refund", "password login account", "refund payment charge"]
vectorizer = TfidfVectorizer()
matrix = vectorizer.fit_transform(texts).toarray()
fig, ax = plt.subplots(figsize=(10, 4.3))
image = ax.imshow(matrix, cmap="Blues", aspect="auto", vmin=0, vmax=1)
ax.set_xticks(range(len(vectorizer.get_feature_names_out())), vectorizer.get_feature_names_out(), rotation=30, ha="right")
ax.set_yticks(range(4), texts)
ax.set(title="Text becomes a sparse matrix", xlabel="Vocabulary columns learned from these four illustrative messages")
fig.colorbar(image, ax=ax, label="Normalized TF-IDF weight")
save(fig, "05_text_classification")

customers = pd.read_csv(ROOT / "data/customer_segments.csv").drop(columns="segment_truth")
scaled = StandardScaler().fit_transform(customers)
labels = KMeans(n_clusters=4, n_init=10, random_state=42).fit_predict(scaled)
pca = PCA(n_components=2).fit(scaled)
scores = pca.transform(scaled)
fig, ax = plt.subplots(figsize=(10, 4.3))
ax.scatter(*scores.T, c=labels, cmap="viridis", alpha=.55, s=12)
ax.set(xlabel="Principal component 1", ylabel="Principal component 2", title="Clusters fitted in seven dimensions, viewed in two")
ax.text(.02, .98, "Illustrative k = 4; this display does not select k.\nPCA retains %.0f%% of standardized variance." % (100 * pca.explained_variance_ratio_.sum()), transform=ax.transAxes, va="top", fontsize=9)
save(fig, "06_clustering")

sales = pd.read_csv(ROOT / "data/daily_sales.csv")
fig, ax = plt.subplots(figsize=(10, 4.3))
t = np.arange(len(sales))
for a, b, color, label in [(0, 700, BLUE, "Earlier observations"), (700, 850, TEAL, "Validation period"), (850, 1000, GOLD, "Final test period")]:
    ax.plot(t[a:b], sales.sales.iloc[a:b], color=color, lw=1, label=label)
ax.set(xlabel="Day index", ylabel="Sales", title="Forecasting: preserve the direction of time")
ax.legend(frameon=False, fontsize=9)
save(fig, "07_time_series")

fig, ax = plt.subplots(figsize=(10, 3.6))
ax.axis("off")
for position, title, description in [(.13, "INPUT", "Validate fields\nand ranges"), (.50, "MODEL", "Saved preprocessing\n+ fitted predictor"), (.87, "OUTPUT", "Probability\n+ threshold decision")]:
    ax.text(position, .58, title, ha="center", weight="bold", color=BLUE, transform=ax.transAxes, bbox=dict(boxstyle="round,pad=.8", fc="#eef3f7", ec="#cddae4"))
    ax.text(position, .25, description, ha="center", va="center", transform=ax.transAxes)
for a, b in [(.24, .38), (.63, .76)]:
    ax.annotate("", xy=(b, .59), xytext=(a, .59), xycoords="axes fraction", arrowprops=dict(arrowstyle="->", lw=2, color=TEAL))
ax.set_title("A prediction service makes the model's contract explicit", pad=20)
save(fig, "08_deployment")

fig, axes = plt.subplots(1, 3, figsize=(12, 3.7))
axes[0].scatter(x, y, s=13, color=BLUE, alpha=.45)
axes[0].plot(grid, np.sin(grid), color=TEAL, lw=2)
axes[0].set(title="Predict a quantity", xlabel="Feature", ylabel="Response")
axes[1].plot(grid, p, color=BLUE, lw=2)
axes[1].axhline(.5, color=GOLD, ls="--")
axes[1].set(title="Estimate a probability", xlabel="Score", ylabel="Probability")
axes[2].scatter(*scores.T, c=labels, cmap="viridis", s=8, alpha=.5)
axes[2].set(title="Explore structure", xlabel="Principal component 1", ylabel="Principal component 2")
save(fig, "course-atlas")
print("Generated nine teaching figures in", OUT)
