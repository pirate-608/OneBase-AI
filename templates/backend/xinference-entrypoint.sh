#!/bin/bash
# OneBase Xinference Entrypoint
# Starts Xinference server, waits for readiness, then auto-launches required models.

set -e

# 1. Start Xinference server in background
echo "[OneBase] Starting Xinference server..."
xinference-local -H 0.0.0.0 -p 9997 &
SERVER_PID=$!

# 2. Wait for API to become available
echo "[OneBase] Waiting for Xinference API..."
MAX_ATTEMPTS=60
for i in $(seq 1 $MAX_ATTEMPTS); do
    if curl -sf http://localhost:9997/v1/models > /dev/null 2>&1; then
        echo "[OneBase] Xinference API ready."
        break
    fi
    if [ "$i" -eq "$MAX_ATTEMPTS" ]; then
        echo "[OneBase] ERROR: Xinference API not ready after ${MAX_ATTEMPTS}s, giving up."
        exit 1
    fi
    sleep 1
done

# 3. Auto-launch models specified via environment variables
launch_model() {
    local model="$1"
    local model_type="$2"   # LLM | embedding
    if [ -z "$model" ]; then return; fi

    # Check if model is already running
    local running
    running=$(curl -sf http://localhost:9997/v1/models 2>/dev/null || echo '{"data":[]}')
    if echo "$running" | grep -q "\"id\":\"$model\""; then
        echo "[OneBase] Model '${model}' (${model_type}) already running, skipping."
        return
    fi

    echo "[OneBase] Launching ${model_type} model '${model}'... (this may take a while on first run)"

    # Use Xinference CLI to launch the model
    if [ "$model_type" = "embedding" ]; then
        xinference launch --model-name "$model" --model-type embedding 2>&1 && \
            echo "[OneBase] Embedding model '${model}' launched." || \
            echo "[OneBase] WARNING: Failed to launch embedding model '${model}'. You may need to launch it manually via the Xinference UI."
    else
        xinference launch --model-name "$model" 2>&1 && \
            echo "[OneBase] LLM model '${model}' launched." || \
            echo "[OneBase] WARNING: Failed to launch LLM model '${model}'. You may need to launch it manually via the Xinference UI."
    fi
}

launch_model "$XINFERENCE_REASONING_MODEL" "LLM"
launch_model "$XINFERENCE_EMBEDDING_MODEL" "embedding"

echo "[OneBase] All models ready. Xinference is serving on :9997"

# 4. Keep the server process in foreground
wait $SERVER_PID
