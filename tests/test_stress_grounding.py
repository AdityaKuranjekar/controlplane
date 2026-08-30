import json
import os
from gateway.ground.grounding_gate import GroundingGate

def test_stress_grounding():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    fixture_path = os.path.join(current_dir, "..", "eval", "fixtures", "segmenter_stress_sample.json")
    
    with open(fixture_path, "r") as f:
        records = json.load(f)
        
    stress_03 = next(r for r in records if r["id"] == "stress_03")
    
    gate = GroundingGate(stress_03["context_chunks"], threshold=0.20)
    events = []
    
    answer_words = stress_03["answer"].split(" ")
    for word in answer_words:
        evs = gate.feed_token(word + " ")
        events.extend(evs)
        
    final = gate.finalize()
    if final:
        events.append(final)
        
    print("\nStress Test Results for stress_03:")
    print(f"Context: {stress_03['context_chunks']}")
    print(f"Answer: {stress_03['answer']}")
    print("-" * 50)
    for ev in events:
        print(f"Sentence: {ev['sentence']}")
        print(f"Score: {ev['score']}")
        print(f"Flagged: {ev['flagged']}")
        print("-" * 50)
        
    # We expect "The city was previously known as Kyoto." to be flagged.
    fabricated = [ev for ev in events if "Kyoto" in ev["sentence"]]
    assert len(fabricated) > 0
    assert fabricated[0]["flagged"] == True
    print("SUCCESS: Fabricated sentence was correctly flagged!")

if __name__ == "__main__":
    test_stress_grounding()
