# What didn’t work

Failures are kept here because they changed the method. None of these entries is a fabricated “messy” story; each is backed by a result file in the release.

## 1. Naive synthetic augmentation

**Expectation:** adding plausible counterfactual user evidence would improve sample efficiency.

**What happened:** at 10 real interactions, real-only training reached **0.663** context accuracy. Random synthetic augmentation fell to **0.600**, diversity to **0.605**, and decision-boundary selection to **0.631**. Uncertainty sampling was essentially tied at **0.663**.

**Why it mattered:** the project stopped treating synthetic-data quantity or selector informativeness as a sufficient objective.

**Change:** downstream training utility became the metric that decides whether synthetic data is useful.

Raw: [`results/v3_synthetic_utility.csv`](../results/v3_synthetic_utility.csv)

## 2. “The labels must be wrong”

**Expectation:** the degradation came from pseudo-label mistakes near decision boundaries.

**What happened:** pseudo-label error in the diagnostic was only **1/2200 (0.045%)**. Oracle-labeled augmentation still scored **0.609** versus **0.664** real-only. UCES had zero observed label errors in the selected diagnostic set and still scored **0.587**.

**Why it mattered:** correct labels were not enough.

**Change:** the investigation moved from sample correctness to dataset composition and correlated evidence mass.

Raw: [`results/paper_oracle_vs_pseudo.csv`](../results/paper_oracle_vs_pseudo.csv)

## 3. Optimizing selection proxies

**Expectation:** examples with higher verified information value should train a better model.

**What happened:** failure-driven and information-gain-style selectors scored ~**0.758** on the proxy versus **0.649** for random, but downstream accuracy did not improve over real-only. Decision-boundary samples were especially informative-looking yet harmful downstream.

**Change:** proxy scores were demoted from objectives to diagnostics.

Raw: [`results/selection_ablation.csv`](../results/selection_ablation.csv), [`results/v3_synthetic_utility.csv`](../results/v3_synthetic_utility.csv)

## 4. Custom drift detection as a contribution

**Expectation:** the project-specific drift heuristic would be a competitive detector.

**What happened:** heuristic ROC-AUC was **0.928**; EWMA **0.980**, CUSUM **0.981**, Bayesian shift **0.969**.

**Change:** drift detection remains infrastructure, not a novelty claim.

Raw: [`results/paper_drift_baselines.csv`](../results/paper_drift_baselines.csv)

## 5. A neural response ranker would automatically be stronger

**Expectation:** a learned PyTorch response ranker should beat simpler structured policies.

**What happened:** across five seeds the scratch neural ranker averaged **0.450 ± 0.022**, while Bayesian state + restraint averaged **0.680 ± 0.013**.

**Interpretation:** more flexible function approximation did not compensate for limited controlled data and weak inductive structure.

**Change:** keep it as a negative baseline; do not hide it or tune until it “wins.”

Raw: [`results/paper_response_level_repeated.csv`](../results/paper_response_level_repeated.csv)
