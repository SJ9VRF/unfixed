from __future__ import annotations
import re
from typing import Any
KEY_PATTERN=re.compile(r'(password|passwd|secret|api[_-]?key|token|ssn|social[_-]?security)',re.I)
VALUE_PATTERNS=[
 re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
 re.compile(r'\bsk-[A-Za-z0-9_-]{12,}\b'),
 re.compile(r'(?i)bearer\s+[A-Za-z0-9._-]{12,}'),
]

def contains_secret_like_value(value: Any) -> bool:
    s=str(value)
    return any(p.search(s) for p in VALUE_PATTERNS)

def redact_mapping(obj: Any) -> Any:
    if isinstance(obj,dict):
        out={}
        for k,v in obj.items():
            out[k]='[REDACTED]' if KEY_PATTERN.search(str(k)) else redact_mapping(v)
        return out
    if isinstance(obj,list): return [redact_mapping(v) for v in obj]
    if isinstance(obj,tuple): return tuple(redact_mapping(v) for v in obj)
    if contains_secret_like_value(obj): return '[REDACTED]'
    return obj
