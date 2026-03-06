#!/bin/bash
# OneBase Ollama Entrypoint
# Starts Ollama server, waits for readiness, then auto-pulls required models.

set -e

# 1. Start Ollama server in background
ollama serve &
SERVER_PID=$!

# 2. Wait for API to become available
echo "[OneBase] Waiting for Ollama API..."
MAX_ATTEMPTS=30
for i in $(seq 1 $MAX_ATTEMPTS); do
    if curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "[OneBase] Ollama API ready."
        break
    fi
    if [ "$i" -eq "$MAX_ATTEMPTS" ]; then
        echo "[OneBase] ERROR: Ollama API not ready after ${MAX_ATTEMPTS}s, giving up."
        exit 1
    fi
    sleep 1
done

# 3. Auto-pull models specified via environment variables
pull_model() {
    local model="$1"
    if [ -z "$model" ]; then return; fi

    # Check if model already exists locally
    if ollama list 2>/dev/null | grep -q "^${model}"; then
        echo "[OneBase] Model '${model}' already available, skipping pull."
    else
        echo "[OneBase] Pulling model '${model}'... (this may take a while on first run)"
        ollama pull "$model"
        echo "[OneBase] Model '${model}' ready."
    fi
}

pull_model "$OLLAMA_REASONING_MODEL"
pull_model "$OLLAMA_EMBEDDING_MODEL"

echo "[OneBase] All models ready. Ollama is serving on :11434"

# 4. Keep the server process in foreground
wait $SERVER_PID
