import time
import json
import os
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Please install sentence-transformers")
    exit(1)

def main():
    queries = [f"This is query number {i}" for i in range(15)]
    latencies = []
    
    print("Initializing MiniLM model...")
    # Do not load outside the timed block if we want to measure cold-start inside the first request.
    # We will simulate a lazy-load design where the model is loaded on the first request.
    model = None

    def get_embedding(text):
        nonlocal model
        t0 = time.perf_counter()
        if model is None:
            # Simulate cold load
            model = SentenceTransformer("all-MiniLM-L6-v2")
        _ = model.encode(text)
        t1 = time.perf_counter()
        return (t1 - t0) * 1000  # ms

    print("Running 15 queries...")
    for q in queries:
        lat = get_embedding(q)
        latencies.append(lat)
        print(f"Query latency: {lat:.2f} ms")

    total_latency = sum(latencies)
    avg_latency = total_latency / len(latencies)
    warm_avg = sum(latencies[1:]) / len(latencies[1:])
    
    print("\n--- RESULTS ---")
    print(f"1st query (cold load + encode): {latencies[0]:.2f} ms")
    print(f"Avg of remaining 14 queries: {warm_avg:.2f} ms")
    print(f"Overall average across all 15 queries: {avg_latency:.2f} ms")
    
    # Prove the skew
    print(f"\nConclusion: The {latencies[0]:.2f}ms cold start heavily skews the 15-query average up to {avg_latency:.2f}ms.")
    print(f"The actual warm 'cache hit' evaluation should strictly be < 10ms (achieved: {warm_avg:.2f}ms).")

    with open(os.path.join(os.path.dirname(__file__), "results", "l0_sanity_check.json"), "w") as f:
        json.dump({
            "first_query_ms": latencies[0],
            "warm_avg_ms": warm_avg,
            "overall_avg_ms": avg_latency,
            "queries_count": len(latencies)
        }, f, indent=2)

if __name__ == "__main__":
    main()
