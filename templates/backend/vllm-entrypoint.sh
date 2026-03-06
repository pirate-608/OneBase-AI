#!/bin/bash
# OneBase vLLM Entrypoint
# Pre-validates environment, logs startup info, and launches the vLLM OpenAI-compatible server.

set -e

MODEL="${VLLM_MODEL_NAME:-}"

if [ -z "$MODEL" ]; then
    echo "[OneBase] ERROR: VLLM_MODEL_NAME not set. Cannot start vLLM."
    exit 1
fi

echo "[OneBase] ============================================="
echo "[OneBase]  vLLM Server Startup"
echo "[OneBase]  Model: ${MODEL}"
echo "[OneBase] ============================================="

# 1. Check for HuggingFace token (required for gated models like Llama, Mistral, etc.)
if [ -n "$HF_TOKEN" ]; then
    echo "[OneBase] HuggingFace token detected. Gated model access enabled."
    export HUGGING_FACE_HUB_TOKEN="$HF_TOKEN"
elif [ -n "$HUGGING_FACE_HUB_TOKEN" ]; then
    echo "[OneBase] HuggingFace token detected (HUGGING_FACE_HUB_TOKEN)."
else
    echo "[OneBase] No HuggingFace token set. If the model is gated, the download will fail."
    echo "[OneBase] Set HF_TOKEN in your .env file to access gated models."
fi

# 2. Check if model weights are already cached
CACHE_DIR="/root/.cache/huggingface/hub"
MODEL_CACHE=$(echo "$MODEL" | sed 's|/|--|g')
if [ -d "${CACHE_DIR}/models--${MODEL_CACHE}" ]; then
    echo "[OneBase] Model weights found in cache. Fast startup expected."
else
    echo "[OneBase] Model weights not cached. First download may take a while..."
fi

# 3. Collect extra vLLM args from env
EXTRA_ARGS="${VLLM_EXTRA_ARGS:-}"

echo "[OneBase] Starting vLLM OpenAI server..."

# 4. Launch vLLM - exec replaces shell process for proper signal handling
exec python -m vllm.entrypoints.openai.api_server \
    --model "$MODEL" \
    --host 0.0.0.0 \
    --port 8000 \
    $EXTRA_ARGS
