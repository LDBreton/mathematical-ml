# 02 — Classification: predicting a binary outcome

This lecture predicts churn in a generated customer dataset. The rows are synthetic and describe no real customers or retention program.

## Learning objectives

After this lecture, you should be able to:

- Derive logistic regression's Bernoulli negative log likelihood, gradient, and Hessian.
- Explain why the regularized objective is convex and how the penalty affects the slope coefficients.
- Build a leakage-safe classification pipeline for numerical and categorical features.
- Distinguish probability ranking, thresholded decisions, and probability calibration.
- Derive a cost-based threshold and choose it with validation data before one final test evaluation.

## Mathematical route

For $Y\in\{0,1\}$ and $\eta=\beta_0+x^T\beta$, let $p=\sigma(\eta)$. The Bernoulli negative log likelihood per observation is $-y\log p-(1-y)\log(1-p)$. The average loss over $n$ rows is

$$L(\beta)=\frac1n\sum_{i=1}^n\left[\log(1+e^{\eta_i})-y_i\eta_i\right].$$

Its slope gradient is $X^T(p-y)/n$ and Hessian is $X^TWX/n$, with $W_{ii}=p_i(1-p_i)\ge0$, so the loss is convex. Adding $\lambda\|\beta\|_2^2/2$ adds $\lambda\beta$ to the gradient and $\lambda I$ to the slope Hessian block. The intercept is conventionally unpenalized; scikit-learn handles it separately.

Accuracy is the fraction of correct decisions. Precision is the share of predicted positives that are positive, recall is the share of actual positives found, and $F_1=2PR/(P+R)$. ROC-AUC is the probability that a randomly selected positive scores above a randomly selected negative, with ties counting one half; it does not assess calibration or choose a decision policy. A probability becomes a decision only after choosing a threshold. With calibrated probability $p$, constant known costs, and zero cost for correct decisions, choose churn when $C_{FP}(1-p)\le C_{FN}p$, equivalently $p\ge C_{FP}/(C_{FP}+C_{FN})$. This rule assumes unconstrained individual decisions. Capacity limits, uncertain costs, poor calibration, or other harms require a different analysis.

## Study steps

1. Follow the environment setup in the repository [README](../../README.md). Open JupyterLab from the repository root and select the **Mathematical ML** kernel.
2. Read `lesson.ipynb` from top to bottom. It searches parent folders for `data/churn.csv`, so it also works when Jupyter starts inside this lecture directory.
3. Attempt the derivation and code in `exercises.ipynb`. It uses separate training, validation, and final test partitions.
4. Compare with `solutions.ipynb`. Model regularization is selected within training cross-validation, threshold is selected on validation under stated toy costs, and the final test set evaluates the frozen choices once.

The generated patterns are for mathematics practice; they do not support real customer interventions.


## Visual guide and study route

![Teaching figure for classification](../../docs/figures/02_classification.svg)

*Illustrative sigmoid and decision threshold. A continuous probability and a discrete action are different outputs.*

New to the libraries? Start with [the first-experiment walkthrough](../../docs/first-steps.md). Read the guided lesson, attempt the exercises, then consult solutions. Allow about 2–3 hours for a first reading; running experiments and completing exercises may require another session.
