from training.neural_response_ranker import NeuralResponseRanker, RankingExample
from evals.response_level.benchmark import TASKS, VALUE_TO_INDEX, NO_PERSONALIZE

def test_response_task_spaces_align():
    for key,(_,opts) in TASKS.items():
        assert set(VALUE_TO_INDEX[key].values()) == set(range(len(opts)))
    assert all(opts[0] for _,opts in NO_PERSONALIZE)

def test_neural_ranker_learns_tiny_pairing():
    ex=[]
    for i in range(40):
        ex.append(RankingExample(str(i),'history user likes concise candidate concise',1))
        ex.append(RankingExample(str(i),'history user likes concise candidate detailed',0))
    m=NeuralResponseRanker.fit(ex,seed=3,epochs=8)
    s=m.score(['history user likes concise candidate concise','history user likes concise candidate detailed'])
    assert s[0] > s[1]
