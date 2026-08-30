import pytest
from gateway.ground.templating import make_hypothesis

def test_make_hypothesis_regression():
    question = "What is the capital of France?"
    answer = "Paris"
    
    hypothesis = make_hypothesis(question, answer)
    
    # Assert it's a complete sentence and contains both elements
    assert isinstance(hypothesis, str)
    assert question in hypothesis
    assert answer in hypothesis
    assert hypothesis.startswith("The answer to")
    assert hypothesis.endswith(".")
