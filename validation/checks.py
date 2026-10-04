from __future__ import annotations
from collections import Counter
from typing import Iterable, Mapping, Any
from interaction_engine.models import InteractionEvent
from user_model.schema import UserState

ALLOWED_CONTEXTS={'general','work','travel','high_stakes','casual'}
SENSITIVE_METADATA_KEYS={'password','ssn','social_security_number','api_key','token','secret'}

def validate_event(event: InteractionEvent) -> list[str]:
    errors=[]
    if not event.event_id.strip(): errors.append('empty event_id')
    if not event.user_id.strip(): errors.append('empty user_id')
    if event.context not in ALLOWED_CONTEXTS: errors.append(f'unknown context:{event.context}')
    bad=SENSITIVE_METADATA_KEYS.intersection(k.lower() for k in event.metadata)
    if bad: errors.append('sensitive metadata keys:'+','.join(sorted(bad)))
    if event.relevant and event.preference_key and event.observed_value is None:
        errors.append('relevant preference event missing observed_value')
    return errors

def validate_user_state(state: UserState) -> list[str]:
    errors=[]
    if not state.user_id.strip(): errors.append('empty user_id')
    for key,pref in state.preferences.items():
        if key != pref.key: errors.append(f'preference key mismatch:{key}!={pref.key}')
        if pref.evidence_count < 0: errors.append(f'negative evidence:{key}')
        if not (0 <= pref.confidence <= 1): errors.append(f'bad confidence:{key}')
        for ctx,cv in pref.context_values.items():
            if ctx not in ALLOWED_CONTEXTS: errors.append(f'unknown preference context:{key}:{ctx}')
            if not (0 <= cv.confidence <= 1): errors.append(f'bad context confidence:{key}:{ctx}')
    return errors

def validate_dataset_rows(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    rows=list(rows); ids=[str(r.get('event_id','')) for r in rows]
    duplicates=[k for k,v in Counter(ids).items() if k and v>1]
    null_keys=sum(1 for r in rows if r.get('relevant',True) and not r.get('preference_key'))
    sensitive=[]
    for i,r in enumerate(rows):
        meta=r.get('metadata') or {}
        bad=SENSITIVE_METADATA_KEYS.intersection(str(k).lower() for k in meta)
        if bad: sensitive.append({'row':i,'keys':sorted(bad)})
    return {'rows':len(rows),'duplicate_event_ids':duplicates,'relevant_rows_missing_preference_key':null_keys,'sensitive_metadata':sensitive,'ok':not duplicates and not sensitive}
