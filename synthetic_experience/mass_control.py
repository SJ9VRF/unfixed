from __future__ import annotations
from dataclasses import replace
from interaction_engine.models import InteractionEvent


def cap_synthetic_mass(events:list[InteractionEvent], max_total_mass:float=.16, per_signature_cap:float=.10)->list[InteractionEvent]:
    """Return copies of synthetic events with reliability capped at the dataset level.

    Synthetic examples are grouped by (preference_key, context).  The total
    reliability injected for one user is capped, and repeated samples from the
    same signature receive progressively smaller weight.  Real events should be
    concatenated by the caller and are never modified.
    """
    if not events:return []
    base=max_total_mass/max(1,len(events)); seen={};out=[]
    for e in events:
        sig=(e.preference_key,e.context);seen[sig]=seen.get(sig,0)+1
        rel=min(float(e.reliability),base,per_signature_cap/seen[sig])
        out.append(e.model_copy(update={'reliability':rel}) if hasattr(e,'model_copy') else replace(e,reliability=rel))
    return out
