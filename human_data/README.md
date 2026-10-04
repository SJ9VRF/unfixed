# Human Data Engine

This directory contains a local pairwise annotation UI and agreement calculator. No human-study results are fabricated in this repository. To run a real study, collect judgments into `labels.jsonl` with `item_id`, `annotator_id`, `winner`, and optional ratings, then run `python human_data/agreement.py`.

Recommended dimensions: usefulness, appropriate personalization, factuality, trust, over-personalization, and preference match.
