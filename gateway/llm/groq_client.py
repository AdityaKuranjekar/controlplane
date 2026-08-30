import os
from groq import Groq

api_key = os.environ.get("GROQ_API_KEY", "mock_key")
client = Groq(api_key=api_key) if api_key != "mock_key" else None

async def complete_sync(messages: list[dict], model: str) -> str:
    if not client:
        return "This is a mocked sync response from ControlPlane L1. Set GROQ_API_KEY to test real LLMs."
    resp = client.chat.completions.create(model=model, messages=messages, stream=False)
    return resp.choices[0].message.content

async def stream_completion(messages: list[dict], model="llama-3.1-8b-instant"):
    if not client:
        # Mock streaming for testing without key
        mock_response = "This is a mocked response from ControlPlane L0. Set GROQ_API_KEY to test real LLMs."
        for word in mock_response.split(" "):
            yield word + " "
        return

    stream = client.chat.completions.create(
        model=model, messages=messages, stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
