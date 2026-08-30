"""
One-time export. Run manually: `python controlplane/models/export_onnx.py`
Produces an ONNX INT8 quantized NLI model you load via onnxruntime.
"""
from optimum.onnxruntime import ORTModelForSequenceClassification, ORTQuantizer
from optimum.onnxruntime.configuration import AutoQuantizationConfig
from transformers import AutoTokenizer

MODEL_ID = "cross-encoder/nli-deberta-v3-xsmall"
OUT_DIR = "controlplane/models/nli-deberta-v3-xsmall-onnx"
OUT_DIR_INT8 = "controlplane/models/nli-deberta-v3-xsmall-int8"

def export():
    # Step 1: export to plain ONNX (fp32)
    model = ORTModelForSequenceClassification.from_pretrained(MODEL_ID, export=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model.save_pretrained(OUT_DIR)
    tokenizer.save_pretrained(OUT_DIR)

    # Step 2: dynamic INT8 quantization (weights only, no calibration data needed)
    quantizer = ORTQuantizer.from_pretrained(OUT_DIR)
    qconfig = AutoQuantizationConfig.avx2(is_static=False, per_channel=False)
    quantizer.quantize(save_dir=OUT_DIR_INT8, quantization_config=qconfig)
    tokenizer.save_pretrained(OUT_DIR_INT8)
    print(f"Done. INT8 model at {OUT_DIR_INT8}")

if __name__ == "__main__":
    export()
