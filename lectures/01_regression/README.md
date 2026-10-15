# 01 — Regression: predicting a numerical response

This lecture builds a regression workflow around a generated housing dataset. The examples are synthetic and do not describe real homes or a real market.

## Learning objectives

After this lecture, you should be able to:

- Derive why the conditional mean minimizes population squared-error risk.
- Derive the least-squares normal equations and explain how design-matrix rank affects coefficient uniqueness.
- Explain how Ridge regularization changes the linear system and why the intercept is not penalized.
- Build a preprocessing and regression pipeline for numerical and categorical features without leakage.
- Compare held-out errors with a baseline and use residual plots as diagnostics rather than causal evidence.

## Mathematical route

For any fixed feature value $X=x$,

$$\mathbb E[(Y-a)^2\mid X=x]=\operatorname{Var}(Y\mid X=x)+(a-\mathbb E[Y\mid X=x])^2,$$

so the population squared-loss minimizer is $f^*(x)=\mathbb E[Y\mid X=x]$. With design matrix $A$, least squares projects $y$ onto the column space of $A$. At an optimum the residual is orthogonal to every column, hence $A^TA\hat\beta=A^Ty$. Full column rank makes $A^TA$ invertible and the coefficient vector unique. If columns are dependent, fitted values can still be uniquely projected while coefficients are not unique.

Ridge minimizes $\|y-A\beta\|_2^2+\alpha\|\beta\|_2^2$. For $\alpha>0$, the penalized coefficient system is invertible. Scikit-learn fits the intercept as a separate unpenalized term; scaling predictors makes the slope penalty comparable across units. Do not add a duplicate constant feature when also fitting an intercept.

## Study steps

1. Follow the environment setup in the repository [README](../../README.md). Open JupyterLab from the repository root and select the **Mathematical ML** kernel.
2. Read `lesson.ipynb` from top to bottom. It searches parent folders for `data/housing.csv`, so it also works when Jupyter starts inside this lecture directory.
3. Attempt the written prompts and marked code in `exercises.ipynb`.
4. Compare your derivations, metrics, and diagnostics with `solutions.ipynb`.

The test partition is held out before fitting and model selection. Cross-validation selects the Ridge penalty from training rows only. Imputation, scaling, and category encoding are fit within the pipeline. MAE and RMSE are in the synthetic target units; $R^2$ is a relative squared-error comparison, not a causal or explanatory fraction.
