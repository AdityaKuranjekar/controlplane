import json
import time
import numpy as np
from fastapi.testclient import TestClient
from gateway.main import app

def run():
    print("Loading queries from eval/fixtures/banking77_300.json...")
    with open("eval/fixtures/banking77_300.json") as f:
        queries = json.load(f)
        
    print(f"Running L1 evaluation on {len(queries)} queries...")
    
    hits = 0
    misses = 0
    failed_queries = 0
    
    hit_latencies = []
    miss_latencies = []
    cascade_latencies = []
    
    # We use TestClient as context manager to trigger startup events
    with TestClient(app) as client:
        for i, q in enumerate(queries):
            payload = {
                "model": "controlplane-default",
                "messages": [{"role": "user", "content": q["text"]}],
                "stream": False,
                "cp_profile": "customer_bot"
            }
            
            while True:
                try:
                    resp = client.post("/v1/chat/completions", json=payload)
                    if resp.status_code >= 400:
                        raise RuntimeError(f"Query {i+1} failed with status {resp.status_code}: {resp.text[:200]}")
                    break
                except Exception as e:
                    if '429' in str(e) or 'rate_limit' in str(e).lower():
                        print(f"Rate limited, waiting 15 seconds... (Query {i+1}/{len(queries)})")
                        time.sleep(15)
                    else:
                        print(f"Query {i+1} failed with error: {e}")
                        resp = None
                        break
            
            if resp is None:
                failed_queries += 1
                continue
                        
            headers = resp.headers
            
            cache_status = headers.get("X-CP-Cache", "MISS")
            
            # The header keys are lowercased by TestClient
            total_ms = float(headers.get("x-cp-total-ms", 0.0))
            cascade_ms = float(headers.get("x-cp-cascade-ms", 0.0))
            
            if cache_status == "HIT":
                hits += 1
                hit_latencies.append(total_ms)
            else:
                misses += 1
                miss_latencies.append(total_ms)
                cascade_latencies.append(cascade_ms)
                
            if (i + 1) % 10 == 0:
                print(f"Processed {i + 1}/{len(queries)} queries. Current Hits: {hits}")

    hit_rate = hits / len(queries) if queries else 0.0
    
    metrics = {
        "total_queries": len(queries),
        "cache_hits": hits,
        "cache_misses": misses,
        "failed_queries": failed_queries,
        "hit_rate": round(hit_rate, 4),
        
        "latency_stats": {
            "avg_hit_latency_ms": round(float(np.mean(hit_latencies)), 2) if hits > 0 else 0.0,
            "p50_hit_latency_ms": round(float(np.percentile(hit_latencies, 50)), 2) if hits > 0 else 0.0,
            "p95_hit_latency_ms": round(float(np.percentile(hit_latencies, 95)), 2) if hits > 0 else 0.0,
            
            "avg_miss_latency_ms": round(float(np.mean(miss_latencies)), 2) if misses > 0 else 0.0,
            "p50_miss_latency_ms": round(float(np.percentile(miss_latencies, 50)), 2) if misses > 0 else 0.0,
            "p95_miss_latency_ms": round(float(np.percentile(miss_latencies, 95)), 2) if misses > 0 else 0.0,
            
            "avg_cascade_latency_ms": round(float(np.mean(cascade_latencies)), 2) if misses > 0 else 0.0
        }
    }
    
    print("\nL1 Evaluation Results:")
    print(json.dumps(metrics, indent=2))
    
    with open("eval/results/l1_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
        
    print("Saved to eval/results/l1_metrics.json")

if __name__ == "__main__":
    run()
