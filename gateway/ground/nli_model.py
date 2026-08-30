from gateway.llm.groq_client import stream_completion

def contradiction_score(premise: str, hypothesis: str) -> float:
    """
    Lite version: Uses Groq API instead of local DeBERTa ONNX model.
    """
    # Ask Llama 3 to act as an NLI model
    prompt = f"""You are a strict logical inference model.
Premise: "{premise}"
Hypothesis: "{hypothesis}"
Does the premise contradict the hypothesis?
Answer ONLY with a number between 0.0 and 1.0, where 1.0 means absolute contradiction and 0.0 means no contradiction."""

    messages = [{"role": "user", "content": prompt}]
    
    try:
        # Since we just want a single float, we can consume the stream synchronously for a quick result
        full_response = ""
        for chunk in stream_completion(messages, model="llama-3.1-8b-instant", temperature=0.0):
            full_response += chunk
            
        score = float(full_response.strip())
        return min(max(score, 0.0), 1.0) # Clamp between 0 and 1
    except Exception as e:
        # Fallback if parsing fails
        print(f"NLI Fallback due to parsing error: {e}")
        return 0.0
