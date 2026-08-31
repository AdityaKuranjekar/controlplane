import os
from dotenv import load_dotenv

load_dotenv()
from groq import Groq

DEFAULT_MODEL = "openai/gpt-oss-20b"

def get_client() -> Groq | None:
    api_key = os.environ.get("GROQ_API_KEY", "mock_key")
    if api_key and api_key != "mock_key" and not api_key.startswith("your_"):
        try:
            return Groq(api_key=api_key)
        except Exception:
            return None
    return None

client = get_client()

def sync_completion(messages: list[dict], model: str = DEFAULT_MODEL, temperature: float = 0.0) -> str:
    active_client = get_client()
    if not active_client:
        return "This is a mocked sync response from ControlPlane L1. Set GROQ_API_KEY to test real LLMs."
    resp = active_client.chat.completions.create(model=model, messages=messages, temperature=temperature, stream=False)
    return resp.choices[0].message.content or ""

async def complete_sync(messages: list[dict], model: str = DEFAULT_MODEL) -> str:
    return sync_completion(messages, model=model)

async def stream_completion(messages: list[dict], model: str = DEFAULT_MODEL):
    active_client = get_client()
    if not active_client:
        mock_response = "This is a mocked response from ControlPlane L0. Set GROQ_API_KEY to test real LLMs."
        for word in mock_response.split(" "):
            yield word + " "
        return

    stream = active_client.chat.completions.create(
        model=model, messages=messages, stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta

