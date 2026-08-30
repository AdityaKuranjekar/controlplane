import pytest
from gateway.ground.nli_model import contradiction_score

def test_contradiction_score_high_for_contradiction():
    premise = "The Eiffel Tower was completed in 1889 in Paris, France."
    hypothesis = "The Eiffel Tower was built in 1901."
    
    score = contradiction_score(premise, hypothesis)
    assert score > 0.7, f"Expected contradiction score > 0.7, got {score}"

def test_contradiction_score_low_for_entailment():
    premise = "The Eiffel Tower was completed in 1889 in Paris, France."
    hypothesis = "The Eiffel Tower is located in France."
    
    score = contradiction_score(premise, hypothesis)
    assert score < 0.3, f"Expected contradiction score < 0.3, got {score}"
