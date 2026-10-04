import csv, json
from pathlib import Path
from backends.openai_compatible import OpenAICompatibleAdapter
from human_eval.build_study import build
from human_eval.analyze import analyze

def test_openai_compatible_request_is_deterministic():
    a=OpenAICompatibleAdapter("https://example.test/v1","test-model","secret")
    url, headers, body=a.build_request("hello")
    assert url.endswith("/v1/chat/completions")
    assert headers["Authorization"]=="Bearer secret"
    payload=json.loads(body)
    assert payload["temperature"]==0 and payload["messages"][0]["content"]=="hello"

def test_human_study_balances_and_analyzes(tmp_path: Path):
    p=tmp_path/"study.csv"; build(p,n_per_type=2,seed=1)
    rows=list(csv.DictReader(p.open())); assert len(rows)==14
    for r in rows:
        r.update(winner="left",over_personalized="no",stale_preference="no",invented_preference="no")
    a=tmp_path/"annotations.csv"
    with a.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    result=analyze(a)
    assert result["annotations"]==14
    assert 0 <= result["pairwise_personalized_win_rate"] <= 1
