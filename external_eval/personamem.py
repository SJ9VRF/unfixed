from __future__ import annotations
import csv, json
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class PersonaMemRow:
    persona_id: str
    question_id: str
    question_type: str
    topic: str
    context: str
    question: str
    reference_answer: str | None

ALIASES={
 'persona_id':['persona_id'], 'question_id':['question_id','id'], 'question_type':['question_type','type'],
 'topic':['topic'], 'context':['context','shared_context','conversation_context','history'],
 'question':['question','query','prompt'], 'reference_answer':['answer','reference_answer','gold_answer','target']
}

def _get(row, names, default=''):
    for n in names:
        if n in row and row[n] not in (None,''): return row[n]
    return default

def load_personamem_questions(path:str|Path, max_items:int|None=None)->list[PersonaMemRow]:
    out=[]
    with open(path,encoding='utf-8',newline='') as f:
        for row in csv.DictReader(f):
            out.append(PersonaMemRow(
                persona_id=str(_get(row,ALIASES['persona_id'])), question_id=str(_get(row,ALIASES['question_id'])),
                question_type=str(_get(row,ALIASES['question_type'])), topic=str(_get(row,ALIASES['topic'])),
                context=str(_get(row,ALIASES['context'])), question=str(_get(row,ALIASES['question'])),
                reference_answer=(str(_get(row,ALIASES['reference_answer'])) or None)))
            if max_items and len(out)>=max_items: break
    return out

def export_prompt_jsonl(rows:list[PersonaMemRow], out_path:str|Path):
    with open(out_path,'w',encoding='utf-8') as f:
        for r in rows:
            payload={'id':r.question_id,'persona_id':r.persona_id,'prompt':f"History:\n{r.context}\n\nUser:\n{r.question}",
                     'reference_answer':r.reference_answer,'question_type':r.question_type,'topic':r.topic}
            f.write(json.dumps(payload,ensure_ascii=False)+'\n')
