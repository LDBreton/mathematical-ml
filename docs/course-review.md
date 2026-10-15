# Beginner-perspective course review

Requested reviewer: Astra at low reasoning effort, adopting the perspective of a mathematician with numerical-analysis experience who knows Python but has no machine-learning background. The review inspected all eight lesson notebooks, lecture READMEs, setup instructions, and website source. It did not execute notebooks or visually inspect the browser. This is a pedagogical critique, not an independent runtime certification.

## Main finding

The course is stronger on mathematical qualifications and evaluation discipline than on introducing the software abstractions needed to reproduce its arguments. Preserve the mathematical depth, but make software objects, transformed arrays, and observable results as explicit as the equations.

## Changes made following the review

- Added a first-experiment guide: observations/features/targets, shapes, terminology, library roles, estimator methods, notebook execution, and troubleshooting.
- Added nine reproducible SVG figures, with captions identifying illustrations versus supplied-data calculations. Figures appear in the landing page, lecture guides, and guided notebooks.
- Added introductory bridges in all eight lessons, including a tiny Ridge calculation, logistic loss calculation, tree/forest distinction, rare-event alert arithmetic, sparse-matrix vocabulary, a Lloyd update, a concrete lag-date example, and serving vocabulary.
- Added an executed transformed-row inspection in lecture 01: raw rows, scaled and encoded columns, and fitted training means.
- Explained the provisional k=4 clustering figure and why descriptive segmentation fits the observed population.
- Labeled the deployment threshold of 0.4 as an illustrative software-contract policy, rather than implying it carries forward validation selection.
- Added anchored contents on notebook reading pages, an explicit static-reading notice, and lesson → exercises → solutions navigation.

## Follow-up implementation

All eight prioritized follow-ups are now implemented:

- Selected clustering sizes, original-unit and standardized centroids, PCA colors, and a discrete legend all refer to the silhouette-selected model. Ten single-start fits supplement the initialization diagnostic; two actual customer-pair distances illustrate scaling.
- Eight result galleries and inline lesson outputs are exported from successfully executed notebooks, with source/data hashes and dependency versions. They distinguish computed results from conceptual illustrations and link each output to its source cell.
- Deployment follows a single fitted pipeline and validation-selected threshold through saving, loading, and the API. Assertions verify probability, threshold, and decision parity. Cleanup is isolated in a documented notebook helper; MLflow tracks the same artifact without retraining. Docker is an extension.
- Rare-event validation cost and alert-count curves explain the threshold tie rule; the always-negative policy's test cost appears in the same comparison.
- Classification includes a validation reliability diagram, bin counts, and a labeled confusion matrix. It does not claim to recalibrate the model.
- Text includes count/IDF/normalized-matrix displays, cosine similarity, sibling-template rows, and new-message/all-unseen-token probes.
- Forecasting includes a five-date feature table and a perturbation check covering the contemporaneous target as well as the future. The long expanding-window function is moved to a documented helper while preserving development-only evaluation.
- Small numerical Ridge and split-gain calculations, objective-matched mean/median baselines, a data-role diagram, and build-time syntax highlighting improve the mathematical and software bridges.

The finite random-start check remains an initialization diagnostic, not a claim about stability under new data. Result snapshots document one successful run rather than promising byte-identical figures across platforms.

## What to shorten or remove

Keep the present eight-topic scope before adding deep learning or further libraries. Use lecture READMEs primarily for orientation and deliverables rather than repeating notebook theory. Consolidate repeated qualifications into concise limits sections while preserving substantive assumptions. Move environment restoration and cleanup machinery in deployment into clearly labeled setup helpers or an appendix in the optional extension. Treat MLflow and Docker as extensions for first-time learners.

## Strengths to preserve

Training-only preprocessing; explicit validation/test separation; manual residual boosting; the worked TF-IDF/IDF check; fitting clusters in full feature space while using PCA only for display; and forecasting information-set and future-perturbation checks. These connect mathematical reasoning to trustworthy experiments.
