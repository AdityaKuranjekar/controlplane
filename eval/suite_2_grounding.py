import json
import os
from gateway.ground.nli_model import contradiction_score
from gateway.ground.conformal import calibrate_threshold, evaluate_at_threshold

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    fixture_path = os.path.join(current_dir, "fixtures", "haluEval_sample.json")
    
    with open(fixture_path, "r") as f:
        records = json.load(f)

    # split 60% calibration / 40% test
    split_idx = int(len(records) * 0.6)
    cal_records, test_records = records[:split_idx], records[split_idx:]

    def score_records(recs):
        scores = {"hallucinated": [], "supported": []}
        from gateway.ground.templating import make_hypothesis
        for r in recs:
            if not r["context_chunks"]:
                continue
            hypothesis = make_hypothesis(r["question"], r["answer"])
            best = max(contradiction_score(chunk, hypothesis) for chunk in r["context_chunks"])
            scores["hallucinated" if r["label"] == "hallucinated" else "supported"].append(best)
        return scores

    print("Scoring records...")
    cal_scores = score_records(cal_records)
    test_scores = score_records(test_records)

    calibration_curve = []
    
    metrics_at_020 = {}

    for target_fnr in [0.10, 0.20, 0.30]:
        threshold = calibrate_threshold(cal_scores["hallucinated"], target_fnr)
        result = evaluate_at_threshold(test_scores["hallucinated"], test_scores["supported"], threshold)
        
        entry = {
            "target_fnr": target_fnr,
            "achieved_fnr": result["achieved_fnr"],
            "achieved_fpr": result["achieved_fpr"],
            "threshold": result["threshold"],
            "n_calibration": len(cal_records),
            "n_test": len(test_records)
        }
        calibration_curve.append(entry)
        
        if target_fnr == 0.20:
            metrics_at_020 = {
                "f1": result["f1"],
                "precision": result["precision"],
                "recall": result["recall"],
                "confusion_matrix": {
                    "tp": result["tp"],
                    "fn": result["fn"],
                    "fp": result["fp"],
                    "tn": result["tn"]
                }
            }

    results_dir = os.path.join(current_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    
    # Save the files to eval/ directly as requested
    with open(os.path.join(current_dir, "l2_metrics.json"), "w") as f:
        json.dump(metrics_at_020, f, indent=2)
        
    with open(os.path.join(current_dir, "l2_calibration.json"), "w") as f:
        json.dump(calibration_curve, f, indent=2)

    print("Metrics at 0.20 FNR:")
    print(json.dumps(metrics_at_020, indent=2))
    print("Calibration Curve:")
    print(json.dumps(calibration_curve, indent=2))

if __name__ == "__main__":
    main()
