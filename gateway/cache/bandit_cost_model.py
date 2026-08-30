"""
Offline Thompson-sampling bandit over candidate cache similarity thresholds.
Replayed against the L1 fixture stream — NOT wired into the live gateway.
Demonstrates the mechanism FrugalGPT/semantic-caching papers describe as
the production upgrade path from L1's fixed τ_cache.
"""
import numpy as np

class ThresholdArm:
    def __init__(self, threshold: float, name: str):
        self.threshold = threshold
        self.name = name
        # Beta distribution parameters for Thompson sampling (success/failure counts)
        self.alpha = 1.0
        self.beta = 1.0

    def sample(self) -> float:
        return np.random.beta(self.alpha, self.beta)

    def update(self, reward: float):
        # reward in [0,1]; treat as a Bernoulli-ish signal for Beta updating
        self.alpha += reward
        self.beta += (1 - reward)


class CacheBandit:
    def __init__(self, candidate_thresholds: list[float]):
        self.arms = [ThresholdArm(t, f"tau_{t}") for t in candidate_thresholds]

    def select_arm(self) -> ThresholdArm:
        sampled_values = [arm.sample() for arm in self.arms]
        return self.arms[int(np.argmax(sampled_values))]

    def composite_reward(self, cache_hit: bool, similarity: float, threshold: float,
                          false_hit_penalty: float = 0.0) -> float:
        """
        R = w_acc * verified - w_lat * latency_proxy - w_cost * token_cost - w_fatigue * false_alert
        Simplified for the offline replay: reward the arm highly when it correctly
        decides to serve from cache (saves cost+latency) and penalize when a served
        cache hit was later flagged as a poor match (false_hit_penalty, e.g. from
        L2's grounding gate disagreeing with a cached answer).
        """
        if not cache_hit:
            return 0.3  # neutral-ish: cascade was used, no cache-specific signal either way
        
        # If cache was hit, similarity should be >= threshold.
        # We penalize false hits heavily. If no penalty, reward scales with similarity.
        base_reward = similarity  # higher similarity -> more confident the hit was good
        return max(0.0, base_reward - false_hit_penalty)
