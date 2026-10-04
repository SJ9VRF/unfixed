from frontier_eval.graders import outcome_match, restraint, state_verification, trajectory_sanity
from frontier_eval.harness import EvalHarness
from frontier_eval.reference_suite import build_reference_tasks
from frontier_eval.run_reference import reference_agent


def test_frontier_harness_reference_suite():
    harness = EvalHarness(reference_agent, [outcome_match, restraint, state_verification, trajectory_sanity], trials_per_task=2)
    report = harness.run(build_reference_tasks())
    summary = report.summary()
    assert summary["n_trials"] == 8
    assert summary["pass_rate"] == 1.0
    assert summary["mean_score"] == 1.0
    assert set(summary["families"]) == {"stable_preference", "preference_drift", "anti_personalization", "context_specific"}


def test_harness_rejects_invalid_trials():
    try:
        EvalHarness(reference_agent, [outcome_match], trials_per_task=0)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")
