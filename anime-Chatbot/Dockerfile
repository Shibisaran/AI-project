FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV MODEL_DIR=/models/HuggingFaceTB_SmolLM2-135M-Instruct
ENV PORT=8000

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir fastapi uvicorn transformers huggingface_hub

COPY api.py /app/api.py

EXPOSE 8000
VOLUME ["/models"]

CMD ["python", "api.py"]
