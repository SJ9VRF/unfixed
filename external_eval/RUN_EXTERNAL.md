# Running external personalization evaluations

The release keeps third-party benchmark data outside the repository. This avoids redistributing data under someone else's license and prevents benchmark-specific examples from leaking into the controlled simulator.

## PersonaMem

1. Obtain the official PersonaMem release from its authors and preserve the original split and license.
2. Point `external_eval.personamem.load_personamem_questions` at the released CSV.
3. Export model-ready prompts with `external_eval.personamem.export_prompt_jsonl`.
4. Run the same completion backend used for every compared method.
5. Score with the benchmark's official evaluator when available; keep raw generations and exact model/prompt configuration with the result bundle.

The adapter intentionally does not normalize away question type, topic, or evolving history because those fields are part of the personalization setting.

## PAHF

1. Obtain the official PAHF scenarios from the authors' release.
2. Load them with `external_eval.pahf.load_pahf_scenarios`.
3. Evaluate memory-only, clarification, correction, and The Unfixed User variants under matched model and interaction budgets.
4. Store every action, correction, and clarification turn rather than only the final score.

## Open-weight post-training

`training/llm_posttraining.py` creates an SFT JSONL export and checks whether the local environment has the required model-training dependencies. A paper result should only be added after all of the following exist:

- exact base checkpoint and revision;
- tokenizer revision;
- training JSONL checksum;
- optimizer and adapter configuration;
- seed(s), hardware, and training duration;
- held-out personalized-response evaluation;
- raw generations and checkpoint hash.

The current release does **not** report a foundation-model post-training result because a suitable checkpoint and Hugging Face/PEFT stack were not available in the execution environment.

## Fair-comparison rule

For every external benchmark, hold the completion model, decoding parameters, context budget, and evaluation script fixed across methods. Only the personalization mechanism may change. Any method-specific extra interaction (for example, clarification) must be reported as interaction cost rather than silently granted.
