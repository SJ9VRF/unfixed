from __future__ import annotations
from dataclasses import dataclass
import math
import re
from typing import Iterable

KEY_LEXICON={
 'travel_priority': {'flight','hotel','trip','travel','booking','price','comfort','direct','layover'},
 'work_time': {'work','focus','focused','schedule','time','morning','afternoon','evening','deep'},
 'answer_detail': {'explain','answer','detail','depth','concise','detailed','technical'},
 'autonomy': {'act','ask','assistant','automatic','reversible','change','permission','autonomy'},
 'privacy_sensitivity': {'privacy','private','personal','sensitive','shared','information','detail','expose'},
 'risk_tolerance': {'risk','risky','uncertainty','option','tradeoff','appetite','accept'},
 'planning_style': {'plan','planning','itinerary','weekend','structure','structured','spontaneous'},
}

@dataclass(frozen=True)
class GateExample:
    prompt: str
    preference_key: str | None
    should_personalize: bool

class PersonalizationGate:
    """Tiny trainable semantic-ish gate with hashed lexical features.

    It is deliberately dependency-light and deterministic. The API can later be backed
    by embeddings or a foundation model without changing evaluation code.
    """
    def __init__(self, dim: int = 128, lr: float = 0.18, epochs: int = 220, l2: float = 1e-3):
        self.dim=dim; self.lr=lr; self.epochs=epochs; self.l2=l2
        self.w=[0.0]*dim; self.b=0.0; self.fitted=False

    @staticmethod
    def _tokens(text: str) -> list[str]:
        return re.findall(r"[a-z0-9_]+", text.lower())

    def _index(self, token: str) -> int:
        # Stable hash independent of PYTHONHASHSEED.
        h=2166136261
        for ch in token.encode('utf-8'):
            h ^= ch; h = (h * 16777619) & 0xffffffff
        return h % self.dim

    def _features(self, prompt: str, preference_key: str | None) -> dict[int,float]:
        tokens=self._tokens(prompt)
        prompt_tokens=list(tokens)
        if preference_key:
            tokens += [f'pref_{preference_key}']
            tokens += [f'prefword_{p}' for p in preference_key.split('_')]
            # Cross-features let the tiny model learn topical relevance of a preference key.
            tokens += [f'cross={t}|pref={preference_key}' for t in prompt_tokens]
            lex=KEY_LEXICON.get(preference_key,set())
            overlap=sum(1 for t in prompt_tokens if t in lex)
            if overlap:
                tokens += ['semantic_overlap']*min(overlap,4)
                tokens += [f'semantic_overlap={preference_key}']*min(overlap,4)
            else:
                tokens += ['semantic_no_overlap']
        # bigrams improve topical relevance while keeping model tiny.
        tokens += [f'{a}__{b}' for a,b in zip(prompt_tokens,prompt_tokens[1:])]
        x={}
        for t in tokens:
            i=self._index(t); x[i]=x.get(i,0.0)+1.0
        norm=math.sqrt(sum(v*v for v in x.values())) or 1.0
        return {i:v/norm for i,v in x.items()}

    @staticmethod
    def _sigmoid(z: float) -> float:
        if z >= 0:
            e=math.exp(-z); return 1/(1+e)
        e=math.exp(z); return e/(1+e)

    def fit(self, examples: Iterable[GateExample]):
        rows=list(examples)
        for _ in range(self.epochs):
            for ex in rows:
                x=self._features(ex.prompt,ex.preference_key)
                p=self._sigmoid(self.b+sum(self.w[i]*v for i,v in x.items()))
                err=p-float(ex.should_personalize)
                for i,v in x.items():
                    self.w[i]-=self.lr*(err*v+self.l2*self.w[i])
                self.b-=self.lr*err
        self.fitted=True
        return self

    def score(self, prompt: str, preference_key: str | None=None) -> float:
        x=self._features(prompt,preference_key)
        return self._sigmoid(self.b+sum(self.w[i]*v for i,v in x.items()))

    def should_personalize(self, prompt: str, preference_key: str | None=None, threshold: float=.5) -> bool:
        return self.score(prompt,preference_key)>=threshold
