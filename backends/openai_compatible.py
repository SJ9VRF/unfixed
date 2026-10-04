from __future__ import annotations
import json, os, urllib.request
from dataclasses import dataclass
from typing import Callable

@dataclass
class OpenAICompatibleAdapter:
    """Minimal dependency-free adapter for OpenAI-compatible chat-completions endpoints.

    Network use is optional and excluded from reference benchmark claims.
    """
    base_url: str
    model: str
    api_key: str | None = None
    timeout_s: float = 60.0

    @classmethod
    def from_env(cls, *, model: str, base_url: str | None = None) -> "OpenAICompatibleAdapter":
        return cls(
            base_url=(base_url or os.getenv("TUU_API_BASE", "https://api.openai.com/v1")).rstrip("/"),
            model=model,
            api_key=os.getenv("TUU_API_KEY") or os.getenv("OPENAI_API_KEY"),
        )

    def build_request(self, prompt: str) -> tuple[str, dict[str, str], bytes]:
        url = f"{self.base_url}/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        body = json.dumps({
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
        }).encode("utf-8")
        return url, headers, body

    def __call__(self, prompt: str) -> str:
        url, headers, body = self.build_request(prompt)
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
            payload = json.load(resp)
        return payload["choices"][0]["message"]["content"]
