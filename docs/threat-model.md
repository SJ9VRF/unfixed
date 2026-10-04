# Threat model

The Unfixed User treats personalization as a high-trust subsystem. This threat model covers the offline reference implementation and the interfaces used by external model backends.

## Protected assets
- explicit user preferences and corrections;
- inferred preferences and confidence values;
- provenance, context and temporal state;
- evaluation data and hidden labels;
- backend credentials.

## Primary risks
1. **Over-personalization:** irrelevant history leaks into a response.
2. **Stale-state harm:** an old preference overrides a newer correction.
3. **Inference overreach:** weak implicit evidence is presented as fact.
4. **Prompt injection through memory/metadata:** untrusted text attempts to control inference or generation.
5. **Secret leakage:** credentials or highly sensitive strings enter logs/artifacts.
6. **Benchmark leakage:** hidden ground truth becomes available to the model under evaluation.
7. **Cross-user contamination:** state from one synthetic/real user is reused for another.

## Mitigations implemented
- relevance gating before inference;
- explicit confidence and drift signals;
- corrections receive stronger evidence weights;
- inference ignores free-form metadata when computing preferences;
- recursive secret redaction utilities;
- schema/data validators;
- isolated `user_id` state construction;
- red-team regression suite executed by the quality gate.

## Out of scope / future production work
Encryption at rest, production IAM, deletion SLAs, formal privacy guarantees, adversarially trained LLM memory extraction, and legal compliance are deployment concerns and are not claimed by this research release.
