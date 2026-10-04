from __future__ import annotations
import hashlib, random, re
from dataclasses import dataclass
from typing import Iterable
import torch
from torch import nn

_TOKEN_RE=re.compile(r"[a-zA-Z0-9_']+")

def _hash_token(tok:str,vocab_size:int)->int:
    h=hashlib.blake2b(tok.encode('utf-8'),digest_size=8).digest()
    return int.from_bytes(h,'little')%vocab_size

def _tokens(text:str)->list[str]: return [t.lower() for t in _TOKEN_RE.findall(text)]
def encode_text(text:str,vocab_size:int)->list[int]:
    toks=_tokens(text); return [_hash_token(t,vocab_size) for t in toks] or [0]

def _parts(text:str)->tuple[str,str,str,str]:
    # Inputs are generated with stable section markers; robust fallbacks keep the ranker reusable.
    hist=text.split('HISTORY:',1)[-1].split('\nCONTEXT:',1)[0] if 'HISTORY:' in text else text
    ctx=text.split('\nCONTEXT:',1)[-1].split('\nQUERY:',1)[0] if '\nCONTEXT:' in text else ''
    query=text.split('\nQUERY:',1)[-1].split('\nCANDIDATE:',1)[0] if '\nQUERY:' in text else ''
    cand=text.split('\nCANDIDATE:',1)[-1] if '\nCANDIDATE:' in text else text
    return hist,ctx,query,cand

def _extras(text:str)->list[float]:
    hist,ctx,query,cand=_parts(text)
    hs,qs,cs=set(_tokens(hist)),set(_tokens(query)),set(_tokens(cand))
    def overlap(a,b): return len(a&b)/max(1,len(b))
    return [overlap(hs,cs),overlap(qs,cs),float(ctx.lower() in cand.lower() and bool(ctx.strip())),min(1.0,len(cs)/24.0)]

@dataclass(frozen=True)
class RankingExample:
    group_id:str
    text:str
    label:int

class NeuralResponseRanker(nn.Module):
    """Small PyTorch response ranker for natural-language personalization evaluation.

    This is not a foundation model.  It provides a learned response-selection
    baseline with trainable lexical representations and explicit history/candidate
    interaction features, so response-level results are not reducible to the
    structured preference classifier used elsewhere in the project.
    """
    def __init__(self,vocab_size:int=8192,dim:int=56,hidden:int=72):
        super().__init__(); self.vocab_size=vocab_size
        self.emb=nn.EmbeddingBag(vocab_size,dim,mode='mean')
        self.net=nn.Sequential(nn.Linear(dim+4,hidden),nn.ReLU(),nn.Dropout(.05),nn.Linear(hidden,1))

    def forward(self,flat_tokens:torch.Tensor,offsets:torch.Tensor,extras:torch.Tensor)->torch.Tensor:
        x=self.emb(flat_tokens,offsets); x=torch.cat([x,extras],dim=1)
        return self.net(x).squeeze(-1)

    @staticmethod
    def _batch(texts:list[str],vocab_size:int):
        seqs=[encode_text(t,vocab_size) for t in texts]; offsets=[];flat=[];cur=0
        for s in seqs: offsets.append(cur);flat.extend(s);cur+=len(s)
        ex=torch.tensor([_extras(t) for t in texts],dtype=torch.float32)
        return torch.tensor(flat,dtype=torch.long),torch.tensor(offsets,dtype=torch.long),ex

    @classmethod
    def fit(cls,examples:Iterable[RankingExample],seed:int=0,epochs:int=14,lr:float=.012,weight_decay:float=1e-4)->'NeuralResponseRanker':
        ex=list(examples); random.Random(seed).shuffle(ex); torch.manual_seed(seed)
        model=cls(); opt=torch.optim.AdamW(model.parameters(),lr=lr,weight_decay=weight_decay)
        # Balance positive/negative candidates within each group-heavy dataset.
        pos=sum(x.label for x in ex); neg=max(1,len(ex)-pos); pos_weight=torch.tensor([neg/max(1,pos)],dtype=torch.float32)
        loss_fn=nn.BCEWithLogitsLoss(pos_weight=pos_weight)
        for epoch in range(epochs):
            order=list(range(len(ex)));random.Random(seed+epoch+1).shuffle(order)
            model.train()
            for start in range(0,len(order),192):
                idxs=order[start:start+192]; texts=[ex[i].text for i in idxs]
                flat,offs,extra=model._batch(texts,model.vocab_size)
                logits=model(flat,offs,extra); y=torch.tensor([float(ex[i].label) for i in idxs])
                loss=loss_fn(logits,y);opt.zero_grad();loss.backward();opt.step()
        return model.eval()

    @torch.no_grad()
    def score(self,texts:list[str])->list[float]:
        flat,offs,extra=self._batch(texts,self.vocab_size)
        return torch.sigmoid(self(flat,offs,extra)).tolist()
