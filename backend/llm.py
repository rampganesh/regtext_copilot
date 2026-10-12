import json
import httpx

import config


class LLMError(Exception):
    pass


class OllamaProvider:
    def __init__(self, host=None):
        self.host = (host or config.OLLAMA_HOST).rstrip('/')

    def chat(self, messages, json_schema=None):
        prompt = self._build_prompt(messages)
        payload = {'model': config.OLLAMA_CHAT_MODEL, 'prompt': prompt, 'stream': False, 'options': {'temperature': 0}}
        if json_schema is not None:
            payload['format'] = json_schema
        r = httpx.post(self.host + '/api/generate', json=payload, timeout=600)
        r.raise_for_status()
        return r.json().get('response', '')

    def embed(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        vectors = []
        batch = 100
        for start in range(0, len(texts), batch):
            chunk = texts[start:start + batch]
            r = httpx.post(self.host + '/api/embed', json={'model': config.OLLAMA_EMBED_MODEL, 'input': chunk}, timeout=600)
            r.raise_for_status()
            data = r.json()
            for vec in data.get('embeddings', []):
                vectors.append(vec)
        return vectors

    @staticmethod
    def _build_prompt(messages):
        parts = []
        for m in messages:
            role = m.get('role', 'user')
            content = m.get('content', '')
            parts.append('### ' + role.upper() + chr(10) + content)
        return chr(10).join(parts)


class Adapter:
    def __init__(self, provider=None, retries=1):
        self.provider = provider or OllamaProvider()
        self.retries = retries

    def chat(self, messages, json_schema=None):
        last = None
        for _ in range(self.retries + 1):
            raw = self.provider.chat(messages, json_schema=json_schema)
            if json_schema is None:
                return raw
            if self._conforms(raw, json_schema):
                return raw
            last = raw
        raise LLMError('model output did not conform to the requested schema after retries')

    def embed(self, texts):
        return self.provider.embed(texts)

    @staticmethod
    def _conforms(raw, json_schema):
        if not raw or not raw.strip():
            return False
        try:
            json.loads(raw)
            return True
        except (json.JSONDecodeError, ValueError):
            return False


llm = Adapter()
