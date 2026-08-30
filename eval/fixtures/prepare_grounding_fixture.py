"""
Loads HaluEval's QA subset (HF-hosted, no access request needed) and reshapes
it into {question, context_chunks, answer, label} records for the grounding eval.
If RAGTruth access is later granted, swap the loader — the downstream eval
script only depends on this record shape, not the source dataset.
"""
import json
from datasets import load_dataset
import os

def prepare(n=200):
    ds = load_dataset("pminervini/HaluEval", "qa", split="data")
    sample = ds.select(range(min(n, len(ds))))

    records = []
    for i, row in enumerate(sample):
        records.append({
            "id": i,
            "question": row["question"],
            "context_chunks": [row["knowledge"]],
            "answer": row["hallucinated_answer"],
            "label": "hallucinated",
        })
        records.append({
            "id": f"{i}_ok",
            "question": row["question"],
            "context_chunks": [row["knowledge"]],
            "answer": row["right_answer"],
            "label": "supported",
        })
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(current_dir, "haluEval_sample.json")
    json.dump(records, open(out_path, "w"), indent=2)
    print(f"Wrote {len(records)} records to {out_path}")

if __name__ == "__main__":
    prepare()
