# Final course project

Choose one problem from lectures 01–07 and turn the lesson into an independently justified experiment. The purpose is to connect the mathematics to the assumptions, code, and evaluation. Use the supplied synthetic data or an instructor-approved public dataset with documented provenance. Do not collect private records for this assignment.

## Required report

1. **Problem and information:** define the response, prediction unit, intended decision, and what information is available at prediction time. For clustering, define the geometry and intended interpretation instead of inventing a target.
2. **Mathematical model:** write the objective and explain each term. Derive at least one update, gradient, projection, or decision rule. Separate the model assumptions from conclusions that actually follow from them.
3. **Data and validation:** document schema, units, provenance, missingness, and sampling structure. Justify independent, group-aware, or chronological splitting. State which observations are used for preprocessing, parameter selection, threshold selection, and final evaluation.
4. **Baseline and model:** build a transparent baseline and at least one justified alternative. For clustering, compare a prespecified set of cluster counts or geometries instead. Keep learned transformations together with the estimator where appropriate.
5. **Results and errors:** choose metrics tied to the problem, show a useful diagnostic plot, and analyze concrete failure cases. Explain uncertainty and data limitations. Avoid choosing a procedure based on the final test scores.
6. **Reproducibility:** supply a notebook that runs from a fresh kernel, fixed inputs and seeds, dependency instructions, and a short command to reproduce the result. State where exact floating-point reproducibility is not guaranteed.

## Suggested extensions

- Fraud: compare an unweighted probability model with a weighted ranking model; derive the implications for alert costs and probability interpretation.
- Text: compare unigram and bigram features while preserving message-family groups; inspect errors and vocabulary limitations.
- Clustering: study how scaling, initialization, and the number of clusters affect assignments; explain whether the interpretation remains stable.
- Forecasting: compare seasonal persistence, a linear autoregressive model, and XGBoost using the same rolling one-step origins; explain how evaluation would change for a seven-day fixed-origin forecast.

## Optional software handoff

Use lecture 08 to persist a fitted pipeline and validate reload behavior. Its supplied API serves the churn schema specifically. A different model needs a matching request schema, response meaning, preprocessing map, and tests; replacing only the artifact is not sufficient. Forecasting additionally needs an explicit way to supply or maintain the observed history. An offline batch prediction command is an acceptable handoff when it fits the task better than an HTTP service.

## Assessment

Apply the instructor-guide rubric: 30% mathematical reasoning, 25% validation design, 25% readable runnable implementation, and 20% interpretation. A well-explained negative result can earn full credit. The highest test score alone cannot.
