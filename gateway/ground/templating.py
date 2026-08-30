def make_hypothesis(question: str, answer: str) -> str:
    """
    Templates a question and answer into a grammatically complete declarative sentence.
    This is necessary to provide proper semantic grounding input to the NLI model,
    which expects two complete sentences (premise and hypothesis).
    """
    # Simple templating. Could be improved with an LLM call if latency allows,
    # but deterministic string formatting is fast and usually sufficient for scoring.
    return f"The answer to the question '{question}' is '{answer}'."
