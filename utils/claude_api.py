"""Claude API — utilidad compartida por todos los agentes."""
import os
import json
import time
import anthropic

_client = None

def get_client(api_key: str = None) -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
    return _client

def call_claude(
    prompt: str,
    system: str = "",
    model: str = "claude-haiku-4-5-20251001",
    max_tokens: int = 4000,
    api_key: str = None,
    expect_json: bool = False,
    retries: int = 3,
) -> str:
    """Llama a la API de Claude con reintentos automáticos."""
    client = get_client(api_key)
    messages = [{"role": "user", "content": prompt}]

    for attempt in range(retries):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system,
                messages=messages,
            )
            text = response.content[0].text.strip()

            if expect_json:
                # Limpiar fences de markdown si existen
                clean = text.replace("```json", "").replace("```", "").strip()
                return json.loads(clean)

            return text

        except anthropic.RateLimitError:
            wait = 2 ** attempt
            print(f"  ⏳ Rate limit, esperando {wait}s...")
            time.sleep(wait)
        except anthropic.APIError as e:
            if attempt == retries - 1:
                raise
            time.sleep(1)
        except json.JSONDecodeError as e:
            if attempt == retries - 1:
                return {} if expect_json else text
            time.sleep(1)

    return {} if expect_json else ""
