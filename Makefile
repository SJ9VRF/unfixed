.PHONY: test benchmark paper quality demo api release verify release-verify

test:
	pytest -q

benchmark:
	python scripts/run_all.py

paper:
	python -m evals.suite.paper_runner
	python scripts/build_paper_figures.py
	python scripts/verify_paper_claims.py
	cd paper && pdflatex -interaction=nonstopmode -halt-on-error the_unfixed_user.tex >/dev/null && pdflatex -interaction=nonstopmode -halt-on-error the_unfixed_user.tex >/dev/null

quality:
	python scripts/quality_gate.py

demo:
	python demo/run_demo.py

api:
	uvicorn api.app:app --reload

release: quality benchmark
	python scripts/build_manifest.py

.PHONY: paper-response
paper-response:
	python -m evals.response_level.repeated
	python scripts/build_paper_figures.py
	python scripts/verify_paper_claims.py

frontier-eval:
	python -m frontier_eval.run_reference --trials 5

model-gate: frontier-eval
	python scripts/model_change_gate.py

verify:
	python -m frontier_eval.run_reference --trials 5
	python scripts/quality_gate.py
	python scripts/verify_paper_claims.py
	python scripts/verify_claims.py
	python scripts/statistical_audit.py
	python scripts/model_change_gate.py
	python scripts/build_manifest.py

release-verify:
	python scripts/verify_release.py
