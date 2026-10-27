import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from huggingface_hub import snapshot_download
from transformers import pipeline


MODEL_NAME = "HuggingFaceTB/SmolLM2-135M-Instruct"
DEFAULT_MODEL_DIR = (
    Path(__file__).resolve().parent
    / "model"
    / MODEL_NAME.replace("/", "_")
)
MODEL_DIR = Path(os.environ.get("MODEL_DIR", str(DEFAULT_MODEL_DIR)))


def ensure_model_exists():
    """Use the local model if complete; otherwise download it from Hugging Face."""
    has_config = (MODEL_DIR / "config.json").is_file()
    has_weights = any(MODEL_DIR.glob("*.safetensors")) or any(
        MODEL_DIR.glob("pytorch_model*.bin")
    )

    if has_config and has_weights:
        print(f"Using existing model at {MODEL_DIR}", flush=True)
    else:
        print(f"Model not found or incomplete at {MODEL_DIR}; downloading {MODEL_NAME}...", flush=True)
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        snapshot_download(repo_id=MODEL_NAME, local_dir=str(MODEL_DIR))
        print(f"Model downloaded to {MODEL_DIR}", flush=True)


ensure_model_exists()
ai = pipeline("text-generation", model=str(MODEL_DIR))

app = FastAPI()


@app.get("/ask")
def ask(question: str):
    message = [{"role": "user", "content": question}]
    result = ai(message, max_new_tokens=100)
    return {"answer": result[0]["generated_text"][-1]["content"]}


if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
