import json
import logging
import time

import httpx

import config
import logging_setup

_log = logging_setup.get_logger('llm')


class LLMError(Exception):
    pass


class OllamaProvider:
    def __init__(self, host=None):
        self.host = (host or config.OLLAMA_HOST).rstrip('/')

    def chat(self, messages, json_schema=None):
        prompt = self._build_prompt(messages)
        payload = {'model': config.OLLAMA_CHAT_MODEL, 'prompt': prompt, 'stream': False, 'think': False, 'options': {'temperature': 0}}
        if json_schema is not None:
            payload['format'] = json_schema
        start = time.perf_counter()
        r = httpx.post(self.host + '/api/generate', json=payload, timeout=600)
        r.raise_for_status()
        duration_ms = round((time.perf_counter() - start) * 1000, 1)
        body = r.json()
        response = body.get('response', '')
        logging_setup.log_event(
            _log,
            'llm_chat',
            level=logging.DEBUG,
            model=config.OLLAMA_CHAT_MODEL,
            endpoint='/api/generate',
            prompt_chars=len(prompt),
            response_chars=len(response),
            duration_ms=duration_ms,
        )
        if not response.strip():
            logging_setup.log_event(
                _log,
                'llm_chat_empty_response',
                level=logging.WARNING,
                model=config.OLLAMA_CHAT_MODEL,
                endpoint='/api/generate',
                duration_ms=duration_ms,
            )
        return response

    def embed(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        vectors = []
        batch = 100
        for bi, start in enumerate(range(0, len(texts), batch)):
            chunk = texts[start:start + batch]
            bstart = time.perf_counter()
            r = httpx.post(self.host + '/api/embed', json={'model': config.OLLAMA_EMBED_MODEL, 'input': chunk}, timeout=600)
            r.raise_for_status()
            bd_ms = round((time.perf_counter() - bstart) * 1000, 1)
            data = r.json()
            for vec in data.get('embeddings', []):
                vectors.append(vec)
            logging_setup.log_event(
                _log,
                'embed_batch',
                level=logging.DEBUG,
                batch=bi,
                n=len(chunk),
                duration_ms=bd_ms,
                model=config.OLLAMA_EMBED_MODEL,
            )
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
