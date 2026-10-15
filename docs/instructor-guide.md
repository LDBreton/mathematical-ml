# Instructor guide

## Teaching approach

Ask students to write the probabilistic assumptions before fitting anything. Distinguish the population risk \(R(f)=\mathbb E[\ell(Y,f(X))]\) from its sample approximation. A numerical optimizer solves the latter; a holdout estimates generalization under assumptions about the sampling process. Neither provides an automatic theorem about future deployment.

Recommended rhythm for each 150-minute class: 25 minutes of theory, 20 minutes exploring the data-generating model, 45 minutes running and discussing the lesson, 45 minutes attempting exercises, and 15 minutes comparing interpretations. Solutions are separate for independent work, but visible in this public teaching repository.

## 01: Regression

Students should identify the design matrix, interpret least squares geometrically, explain a baseline, and understand why learned preprocessing belongs inside cross-validation. Ask: when does a coefficient estimate equal the generating coefficient? Discuss finite samples, noise, identifiability with dummy variables, missing-data handling, and regularization bias. A good answer reports test MAE with units and analyzes residuals rather than reporting only a score.

## 02: Classification

Students should derive Bernoulli negative log likelihood, distinguish probabilities from labels, and calculate precision/recall from counts. Ask: why can two classifiers have the same ROC AUC but different operational costs? Threshold selection must use validation data; the final test is not a tuning tool. Discuss calibration separately from ranking and distinguish association from intervention.

## 03: XGBoost

Students should connect negative loss derivatives to additive fitting, derive the optimal leaf weight for a fixed partition, and explain why the split gain is an approximate objective reduction. Ask: where is the approximation, and what changes with learning-rate shrinkage? Compare to a dummy and random forest under the same final test. A higher benchmark score alone is insufficient without discussing variation, complexity, and validation choices.

## 04: Imbalanced learning

Have students derive precision from prevalence, true-positive rate, and false-positive rate before looking at model scores. Ask why a model can have strong ROC AUC while producing too many false alerts. Compare average precision with trapezoidal PR area and explain the no-skill prevalence reference. Derive how class weighting changes the fitted posterior, then choose thresholds on validation data with stated costs. A useful fraud report includes alert volume and positive-class recall, not accuracy alone. All transactions are synthetic; the example cannot establish operational fraud prevention.

## 05: Text classification

Build a document-term matrix by hand, then apply the exact smoothed IDF and L2 normalization used by scikit-learn. Connect the sparse representation to a linear score and multinomial likelihood. Ask what happens when an unseen word has no vocabulary coordinate. Keep related template-family messages in one partition, and fit vocabulary only on training messages. Discuss macro versus micro metrics and inspect actual errors. Synthetic templates are a controlled teaching corpus; they do not measure broad natural-language understanding. Embeddings are an optional conceptual extension, not a prerequisite.

## 06: Clustering

Derive the centroid update by differentiating within-cluster squared distance. Explain why alternating updates decrease the objective yet can converge to a local minimum. Use standardization to expose the dependence on units. Derive PCA from a variance-maximizing direction and relate it to singular vectors. Cluster in the full standardized feature space, using PCA only as a visualization. Choose the number of clusters using internal diagnostics; any synthetic latent label must remain outside fitting and selection. Ask why permuting cluster IDs changes no geometric conclusion and why silhouette is not a theorem about natural customer segments.

## 07: Time-series forecasting

State the exact forecast origin and information set before constructing features. Ask students to explain why `shift(1).rolling(...)` is admissible while an unshifted moving average can leak the target. Compare seasonal persistence against XGBoost with ordered development and final test periods. Show expanding-window evaluation without using final test observations for selection. Distinguish rolling one-step predictions, where yesterday's actual sales become available, from a multi-day forecast made at a single origin. Report error in sales units; forecasting assumptions must match what observations are available in deployment.

## 08: Deployment

Students should explain why a trained preprocessing map is part of the model, verify reload parity, reject invalid inputs, and distinguish a probability from the threshold policy. Inspect a tracked run and trace its data, seed, parameters, and artifact. The supplied HTTP interface has no authentication or monitoring and stays local. Discuss drift, privacy, latency, calibration, and rollback as requirements for any real deployment.

## Assessment rubric

Use 30% mathematical reasoning and stated assumptions, 25% sound validation design, 25% readable runnable implementation, and 20% interpretation and limitations. Reward thoughtful negative results. Do not grade solely on the highest test score. Require a short model report: intended use, data origin, sampling assumptions, objective, baseline, validation strategy, metrics with units, errors, and limitations.

## Technology references

- [scikit-learn pipelines](https://scikit-learn.org/stable/modules/compose.html): keep preprocessing and estimation together.
- [XGBoost estimator interface](https://xgboost.readthedocs.io/en/stable/python/sklearn_estimator.html) and [parameters](https://xgboost.readthedocs.io/en/stable/parameter.html).
- [MLflow tracking](https://mlflow.org/docs/latest/tracking/): parameters, metrics, and artifacts.
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/): test request validation without running a server.
- [Average precision](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html): recall-weighted precision rather than trapezoidal interpolation.
- [TF-IDF transformation](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfTransformer.html): the precise smoothing and normalization conventions.
- [Silhouette analysis](https://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_silhouette_analysis.html): internal cluster diagnostics.
- [Lagged forecasting features](https://scikit-learn.org/stable/auto_examples/applications/plot_time_series_lagged_features.html): chronological evaluation.
