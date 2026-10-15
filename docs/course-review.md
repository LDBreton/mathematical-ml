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

## Strong recommendations for the next teaching iteration

| Priority | Recommendation | Why it matters |
|---|---|---|
| High | Display final silhouette-selected cluster sizes, profiles, and a matching PCA plot | The initial k=4 picture must not stand in for a different selected fit |
| High | Build selected result galleries from verified notebook executions | These authored concept figures complement, but do not replace, actual residual, PR, and forecast diagnostics |
| High | Present one artifact lifecycle through training, threshold selection, saving, loading, and API parity | Several independent deployment demonstrations currently require extra explanation |
| Medium | Add a validation-cost/alert-count threshold plot and place always-negative cost in the same comparison | Makes rare-event decisions operational rather than just metric-driven |
| Medium | Add a calibration reliability example and labeled confusion-matrix counts | Ranking, probability quality, and policy quality are separate questions |
| Medium | Show a count matrix, IDF vector, normalized rows, and one cosine calculation | Extend the existing strong manual-IDF example into sparse geometry |
| Medium | Add a compact five-date forecast-feature table and more than two clustering starts | Make information availability and stability more observable |

## What to shorten or remove

Keep the present eight-topic scope before adding deep learning or further libraries. Use lecture READMEs primarily for orientation and deliverables rather than repeating notebook theory. Consolidate repeated qualifications into concise limits sections while preserving substantive assumptions. Move environment restoration and cleanup machinery in deployment into clearly labeled setup helpers or an appendix in a future refactor. Treat MLflow and Docker as extensions for first-time learners.

## Strengths to preserve

Training-only preprocessing; explicit validation/test separation; manual residual boosting; the worked TF-IDF/IDF check; fitting clusters in full feature space while using PCA only for display; and forecasting information-set and future-perturbation checks. These connect mathematical reasoning to trustworthy experiments.
