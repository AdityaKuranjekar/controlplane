import numpy as np

def calibrate_threshold(cal_scores_hallucinated: list[float], target_fnr: float) -> float:
    """
    Given contradiction scores for KNOWN-hallucinated claims from a calibration split,
    find the threshold λ such that flagging score >= λ catches (1 - target_fnr)
    fraction of them — i.e. achieves FNR <= target_fnr on this calibration set,
    with the standard conformal finite-sample correction.

    This is a simple split-conformal quantile method: not full conformal prediction
    machinery, but the same core idea (empirical quantile -> distribution-free guarantee
    on held-out data of the same distribution).
    """
    scores = np.array(sorted(cal_scores_hallucinated))
    n = len(scores)
    if n == 0:
        return 0.5 # Fallback
    
    # we want P(score >= lambda) >= 1 - target_fnr among hallucinated claims
    # i.e. lambda = the target_fnr-quantile of the score distribution
    # finite-sample correction: use ceil((n+1)*(1-target_fnr))/n -th order statistic (standard split-conformal adjustment)
    idx = int(np.ceil((n + 1) * target_fnr)) - 1
    idx = max(0, min(idx, n - 1))
    return float(scores[idx])

def evaluate_at_threshold(scores_hallucinated: list[float], scores_supported: list[float], threshold: float) -> dict:
    tp = sum(1 for s in scores_hallucinated if s >= threshold)  # correctly flagged hallucinations
    fn = len(scores_hallucinated) - tp                            # missed hallucinations
    fp = sum(1 for s in scores_supported if s >= threshold)      # supported claims wrongly flagged
    tn = len(scores_supported) - fp

    achieved_fnr = fn / max(1, len(scores_hallucinated))
    achieved_fpr = fp / max(1, len(scores_supported))
    precision = tp / max(1, tp + fp)
    recall = tp / max(1, tp + fn)
    f1 = 2 * precision * recall / max(1e-9, precision + recall)

    return {"threshold": threshold, "achieved_fnr": achieved_fnr, "achieved_fpr": achieved_fpr,
            "precision": precision, "recall": recall, "f1": f1, "tp": tp, "fn": fn, "fp": fp, "tn": tn}
