from __future__ import annotations
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from interaction_engine.models import InteractionEvent
from user_model.schema import UserState


def _features(events:list[InteractionEvent], key:str, query_context:str|None=None)->dict[str,float]:
    f={}
    relevant=[e for e in events if e.preference_key==key and e.observed_value is not None]
    for e in relevant:
        v=str(e.observed_value)
        # Context matching gets stronger weight; global evidence remains visible.
        ctx_mult=1.6 if query_context and e.context==query_context else 1.0
        f[f'value={v}']=f.get(f'value={v}',0)+e.reliability*ctx_mult
        f[f'source={e.signal_type.value}']=f.get(f'source={e.signal_type.value}',0)+ctx_mult
        f[f'ctx={e.context}|value={v}']=f.get(f'ctx={e.context}|value={v}',0)+e.reliability
    if query_context:
        f[f'query_ctx={query_context}']=1.0
    f['n_events']=len(relevant)
    return f


def build_training_rows(states:list[UserState], events_by_user:dict[str,list[InteractionEvent]], contexts:list[str]|None=None)->dict[str,tuple[list[dict],list[str]]]:
    rows={}; contexts=contexts or ['general','work','travel','high_stakes','casual']
    for state in states:
        ev=events_by_user.get(state.user_id,[])
        for key,p in state.preferences.items():
            x,y=rows.setdefault(key,([],[]))
            # One row per context teaches context-conditioned labels, plus a global row.
            x.append(_features(ev,key,None)); y.append(str(p.value))
            for ctx in contexts:
                value,_=p.value_for_context(ctx)
                x.append(_features(ev,key,ctx)); y.append(str(value))
    return rows


class TrainablePreferenceModel:
    def __init__(self):
        self.models={}; self.vectorizers={}; self.constants={}
    def fit(self, rows):
        for key,(X,y) in rows.items():
            uniq=sorted(set(y))
            if len(uniq)<2:
                self.constants[key]=uniq[0]; continue
            vec=DictVectorizer(sparse=True); Xm=vec.fit_transform(X)
            clf=LogisticRegression(max_iter=500,random_state=0,C=1.0).fit(Xm,y)
            self.vectorizers[key]=vec; self.models[key]=clf
        return self
    def predict(self,key:str,events:list[InteractionEvent],context:str|None=None)->tuple[str|None,float]:
        if key in self.constants:return self.constants[key],0.75
        if key not in self.models:return None,0.0
        vec=self.vectorizers[key]; clf=self.models[key]
        X=vec.transform([_features(events,key,context)])
        prob=clf.predict_proba(X)[0]; idx=int(np.argmax(prob))
        return str(clf.classes_[idx]),float(prob[idx])
