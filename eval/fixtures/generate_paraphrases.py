"""
One-time script. Run manually, NOT part of the eval suite or CI.
Costs real API calls once; output is committed to the repo so eval
runs afterward are free and deterministic.
"""
import json, os
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

def load_banking77_sample(n=100) -> list[dict]:
    # Pull from HF datasets: `banking77`, take first n, or a stratified sample
    from datasets import load_dataset
    ds = load_dataset("banking77", split="test")
    sample = ds.select(range(n))
    return [{"id": i, "text": row["text"], "label": row["label"]} for i, row in enumerate(sample)]

def paraphrase(text: str) -> str:
    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content":
            f"Paraphrase this customer support question in a different way, same meaning, one line only:\n\n{text}"}],
        temperature=0.9,
    )
    return resp.choices[0].message.content.strip()

if __name__ == "__main__":
    sample = load_banking77_sample(100)
    os.makedirs("eval/fixtures", exist_ok=True)
    json.dump(sample, open("eval/fixtures/banking77_sample.json", "w"), indent=2)

    paraphrases = {}
    for row in sample:
        paraphrases[row["id"]] = [paraphrase(row["text"]) for _ in range(2)]  # 2 paraphrases each
        print(f"done {row['id']}")

    json.dump(paraphrases, open("eval/fixtures/paraphrases.json", "w"), indent=2)
