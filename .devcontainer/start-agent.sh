#!/usr/bin/env bash
# Bring the agent up inside the codespace.
#
#   .devcontainer/start-agent.sh                config, proxy, then Claude Code
#   .devcontainer/start-agent.sh --proxy-only   config and proxy, no Claude Code
#
# Safe to run as many times as you like. If the agent stops answering, this is
# the "turn it off and on again" command — run it and carry on.
set -euo pipefail

FCC_DIR="${HOME}/.fcc"
PROXY_PORT=8082
LOG="${HOME}/fcc-server.log"

proxy_is_up() { (exec 3<>"/dev/tcp/127.0.0.1/${PROXY_PORT}") 2>/dev/null; }

write_env() {
    mkdir -p "$FCC_DIR"
    umask 077
    {
        for var in NVIDIA_NIM_API_KEY OPENROUTER_API_KEY GROQ_API_KEY \
                   CEREBRAS_API_KEY GEMINI_API_KEY OLLAMA_BASE_URL; do
            value="${!var:-}"
            [ -n "$value" ] && printf '%s="%s"\n' "$var" "$value"
        done
        printf 'MODEL="%s"\n' "${MODEL:-nvidia_nim/nvidia/nemotron-3-super-120b-a12b}"
        [ -n "${MODEL_HAIKU:-}" ] && printf 'MODEL_HAIKU="%s"\n' "$MODEL_HAIKU"
        [ -n "${MODEL_SONNET:-}" ] && printf 'MODEL_SONNET="%s"\n' "$MODEL_SONNET"
    } > "$FCC_DIR/.env"
}

if [ -n "${NVIDIA_NIM_API_KEY:-}${OPENROUTER_API_KEY:-}${OLLAMA_BASE_URL:-}" ]; then
    write_env
else
    echo "!! No provider key found."
    echo "!! Add NVIDIA_NIM_API_KEY as a Codespaces secret and rebuild, or set one"
    echo "!! in the Admin UI once the proxy is up: http://localhost:${PROXY_PORT}/admin"
fi

if proxy_is_up; then
    echo "proxy already up. admin UI: http://localhost:${PROXY_PORT}/admin"
else
    echo "starting fcc-server..."
    nohup fcc-server > "$LOG" 2>&1 &
    for _ in $(seq 1 90); do
        proxy_is_up && break
        sleep 1
    done

    if proxy_is_up; then
        echo "proxy up. admin UI: http://localhost:${PROXY_PORT}/admin"
    else
        echo "!! fcc-server did not come up. Last 30 lines of its log:"
        tail -n 30 "$LOG" || true
        echo "!! Tell the facilitator. You can still read code and run pytest."
        exit 1
    fi
fi

[ "${1:-}" = "--proxy-only" ] && exit 0

exec fcc-claude
