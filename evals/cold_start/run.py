from user_simulator.profiles import SyntheticProfileConfig, generate_user_state
from evals.cold_start.benchmark import evaluate_cold_start


def main() -> None:
    user = generate_user_state("demo-user", SyntheticProfileConfig(n_preferences=7, seed=42))
    results = evaluate_cold_start(user, seed=42)
    print("n_interactions,personalization_accuracy,calibration_error,incorrect_personalization_rate")
    for r in results:
        print(f"{r.n_interactions},{r.personalization_accuracy:.3f},{r.calibration_error:.3f},{r.incorrect_personalization_rate:.3f}")


if __name__ == "__main__":
    main()
