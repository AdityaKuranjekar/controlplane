from gateway.cache.bandit_cost_model import CacheBandit

def test_bandit_convergence():
    bandit = CacheBandit([0.7, 0.8, 0.9])
    
    # Synthetic scenario: 0.8 is the perfect arm. 0.7 gives false hits (penalty), 0.9 gives misses (neutral 0.3)
    
    for _ in range(50):
        arm = bandit.select_arm()
        if arm.threshold == 0.8:
            reward = 0.95
        elif arm.threshold == 0.7:
            reward = 0.0 # heavy false hit penalty
        else: # 0.9
            reward = 0.3 # miss
            
        arm.update(reward)
        
    stats = {a.threshold: (a.alpha, a.beta) for a in bandit.arms}
    print("Bandit stats after 50 rounds:")
    for a in bandit.arms:
        print(f"Arm {a.name}: alpha={a.alpha:.2f}, beta={a.beta:.2f}, ratio={a.alpha/(a.alpha+a.beta):.2f}")
        
    best_arm = max(bandit.arms, key=lambda a: a.alpha / (a.alpha + a.beta))
    assert best_arm.threshold == 0.8, f"Bandit did not converge to 0.8! It picked {best_arm.threshold}"
    print("Test passed! Bandit converged to the correct synthetic arm.")

if __name__ == "__main__":
    test_bandit_convergence()
