import csv, json
from external_eval.personamem import load_personamem_questions
from external_eval.pahf import load_pahf_scenarios
from training.llm_posttraining import build_sft_jsonl

def test_external_adapters_and_sft(tmp_path):
    p=tmp_path/'p.csv'
    p.write_text('persona_id,question_id,question_type,topic,context,question,answer\nu1,q1,mcq,food,likes tea,choose,tea\n')
    r=load_personamem_questions(p); assert r[0].persona_id=='u1' and r[0].reference_answer=='tea'
    q=tmp_path/'q.json'; q.write_text(json.dumps([{'index':0,'user':'A','task':'bring drink','context':'pref','scene':'tea coffee','user_intent_object':'tea'}]))
    assert load_pahf_scenarios(q)[0].target=='tea'
    out=build_sft_jsonl([{'history':'h','query':'q','response':'r'}],tmp_path/'sft.jsonl'); assert out.exists()
