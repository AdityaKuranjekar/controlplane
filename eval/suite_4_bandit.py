import json
import numpy as np
from gateway.cache.bandit_cost_model import CacheBandit
from gateway.cache.embeddings import embed

CANDIDATE_THRESHOLDS = [0.75, 0.82, 0.88, 0.94]  # conservative -> aggressive

def load_replay_stream():
    """Reuse the same 300-query fixture from L1 — same queries, offline replay only."""
    sample = json.load(open("eval/fixtures/banking77_300.json"))
    paraphrases = json.load(open("eval/fixtures/paraphrases.json"))
    stream = []
    for row in sample:
        stream.append(row["text"])
        stream.extend(paraphrases.get(str(row["id"]), []))
    print(f"DEBUG: len(stream) = {len(stream)}")
    return stream

def simulate_cache_check(query: str, seen_embeddings: list, threshold: float):
    """Lightweight in-memory simulation, independent of the live FAISS store,
    so this script can run standalone without the gateway process running."""
    vec = embed(query)
    if not seen_embeddings:
        seen_embeddings.append(vec)
        return False, 0.0
    sims = [float(np.dot(vec, e)) for e in seen_embeddings]  # vectors are unit-norm
    best_sim = max(sims)
    seen_embeddings.append(vec)
    return best_sim >= threshold, best_sim

def main():
    stream = load_replay_stream()
    bandit = CacheBandit(CANDIDATE_THRESHOLDS)
    seen_embeddings_per_arm = {arm.name: [] for arm in bandit.arms}

    # "best fixed arm in hindsight" for regret computation
    per_arm_cumulative_reward = {arm.name: 0.0 for arm in bandit.arms}
    bandit_cumulative_reward = 0.0
    regret_curve = []

    for t, query in enumerate(stream):
        chosen_arm = bandit.select_arm()
        hit, sim = simulate_cache_check(query, seen_embeddings_per_arm[chosen_arm.name], chosen_arm.threshold)
        reward = bandit.composite_reward(hit, sim, chosen_arm.threshold)
        chosen_arm.update(reward)
        bandit_cumulative_reward += reward

        # also evaluate every arm against this same query for the regret baseline
        for arm in bandit.arms:
            if arm.name != chosen_arm.name:
                h2, s2 = simulate_cache_check(query, seen_embeddings_per_arm[arm.name], arm.threshold)
                r2 = bandit.composite_reward(h2, s2, arm.threshold)
            else:
                r2 = reward
            per_arm_cumulative_reward[arm.name] += r2

        best_fixed_reward_so_far = max(per_arm_cumulative_reward.values())
        regret = best_fixed_reward_so_far - bandit_cumulative_reward
        regret_curve.append({"round": t, "regret": round(regret, 4), "chosen_arm": chosen_arm.name})

    best_fixed_arm_in_hindsight = max(per_arm_cumulative_reward, key=per_arm_cumulative_reward.get)
    bandit_favored_arm_obj = max(bandit.arms, key=lambda a: a.alpha / (a.alpha + a.beta))
    bandit_favored_arm = bandit_favored_arm_obj.name

    result = {
        "candidate_thresholds": CANDIDATE_THRESHOLDS,
        "best_fixed_arm_in_hindsight": best_fixed_arm_in_hindsight,
        "bandit_favored_arm": bandit_favored_arm,
        "final_arm_stats": [{"threshold": a.threshold, "alpha": round(a.alpha, 2), "beta": round(a.beta, 2), "ratio": round(a.alpha/(a.alpha+a.beta), 4)}
                              for a in bandit.arms],
        "regret_curve": regret_curve,
    }
    json.dump(result, open("eval/results/l4_bandit_metrics.json", "w"), indent=2)
    print(f"Final regret: {regret_curve[-1]['regret']}")
    print(f"Best fixed arm in hindsight: {best_fixed_arm_in_hindsight}")
    print(f"Bandit favored arm:          {bandit_favored_arm}")
    print(f"Match?                       {'YES' if best_fixed_arm_in_hindsight == bandit_favored_arm else 'NO'}")
    print(f"Arm stats: {result['final_arm_stats']}")

if __name__ == "__main__":
    main()
