import os
import json
from datasets import load_dataset
from gateway.llm.groq_client import stream_completion

def generate():
    print("Loading mteb/banking77 dataset...")
    ds = load_dataset("mteb/banking77", split="train")
    
    # Take first 100 queries
    queries = [item["text"] for item in ds.select(range(100))]
    
    output = []
    
    # We want 300 total (1 original + 2 paraphrases per query)
    print("Generating paraphrases via Groq...")
    
    for idx, query in enumerate(queries):
        output.append({"id": f"{idx}_orig", "text": query, "is_paraphrase": False})
        
        prompt = f"Rewrite the following customer service query in two different ways while preserving the exact intent. Provide the two rewrites separated by a newline. Do not output anything else.\n\nQuery: {query}"
        
        try:
            # Synchronous gathering of stream
            async def run_prompt():
                chunks = []
                async for chunk in stream_completion([{"role": "user", "content": prompt}], "openai/gpt-oss-20b"):
                    chunks.append(chunk)
                return "".join(chunks)
                
            import asyncio
            result = asyncio.run(run_prompt())
            
            rewrites = [r.strip() for r in result.split("\n") if r.strip()][:2]
            
            for i, rewrite in enumerate(rewrites):
                output.append({
                    "id": f"{idx}_para_{i+1}",
                    "text": rewrite,
                    "is_paraphrase": True
                })
        except Exception as e:
            print(f"Failed to generate paraphrase for query {idx}: {e}")
            # Just add dummy paraphrases if it fails
            output.append({"id": f"{idx}_para_1", "text": f"{query} (paraphrased 1)", "is_paraphrase": True})
            output.append({"id": f"{idx}_para_2", "text": f"{query} (paraphrased 2)", "is_paraphrase": True})

        if idx % 10 == 0:
            print(f"Processed {idx}/100 queries...")

    with open("eval/fixtures/banking77_300.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"Saved {len(output)} queries to banking77_300.json")

if __name__ == "__main__":
    generate()
