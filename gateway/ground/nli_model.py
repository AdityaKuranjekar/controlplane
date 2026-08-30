from optimum.onnxruntime import ORTModelForSequenceClassification
from transformers import AutoTokenizer
from functools import lru_cache
import numpy as np
import os

# Base directory for models relative to the project root
# Using an absolute path or relative to the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
MODEL_DIR = os.path.join(project_root, "controlplane", "models", "nli-deberta-v3-xsmall-int8")

# CONFIRMED from model.config.id2label at export time.
# {0: 'contradiction', 1: 'entailment', 2: 'neutral'}
LABEL_MAP = {"entailment": 1, "neutral": 2, "contradiction": 0}

@lru_cache(maxsize=1)
def get_model_and_tokenizer():
    model = ORTModelForSequenceClassification.from_pretrained(MODEL_DIR, file_name="model_quantized.onnx")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    return model, tokenizer

def contradiction_score(premise: str, hypothesis: str) -> float:
    """
    Returns P(contradiction) normalized over {entailment, contradiction} only,
    per the SelfCheckGPT-NLI paper's approach — ignores the neutral class
    so the score is cleanly bounded [0,1].
    """
    model, tok = get_model_and_tokenizer()
    inputs = tok(premise, hypothesis, return_tensors="pt", truncation=True, max_length=256)
    logits = model(**inputs).logits[0].detach().numpy()

    z_e = logits[LABEL_MAP["entailment"]]
    z_c = logits[LABEL_MAP["contradiction"]]
    
    # softmax over just these two logits (paper's normalization)
    exp_e, exp_c = np.exp(z_e), np.exp(z_c)
    return float(exp_c / (exp_e + exp_c))
