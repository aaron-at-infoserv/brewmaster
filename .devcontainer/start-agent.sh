#!/usr/bin/env bash
# Bring the agent up inside the codespace.
#
#   .devcontainer/start-agent.sh                config, proxy, then Claude Code
#   .devcontainer/start-agent.sh --proxy-only   config and proxy, no Claude Code
#   .devcontainer/start-agent.sh --restart      pick up a changed key or MODEL
#
# Safe to run as many times as you like. If the agent stops answering, this is
# the "turn it off and on again" command — run it and carry on.
#
# Switching provider or model is a --restart, not a trip to the Admin UI. That
# UI only answers loopback clients, so the forwarded Codespaces URL gets a 403
# and always will. Set what you want on the command line instead:
#
#   MODEL=cerebras/llama-3.3-70b .devcontainer/start-agent.sh --restart
#
# Editing ~/.fcc/brewmaster.env by hand does not survive: this script rewrites
# it from the environment on every run.
set -euo pipefail

FCC_DIR="${HOME}/.fcc"
PROXY_PORT=8082
LOG="${HOME}/fcc-server.log"

# Our keys go in our own file. ~/.fcc/.env belongs to fcc - its Admin UI and
# `fcc-init` rewrite it - so writing there destroys whatever fcc has persisted,
# including the proxy auth token, which shows up later as a 401 from a server
# still enforcing a token the client no longer knows. FCC_ENV_FILE is the
# highest-precedence dotenv fcc reads, so ours wins without clobbering theirs.
# devcontainer.json sets this too, so a plain `fcc-claude` in any terminal
# resolves the same file the server started with.
FCC_ENV_FILE="${FCC_ENV_FILE:-${FCC_DIR}/brewmaster.env}"
export FCC_ENV_FILE

proxy_is_up() { (exec 3<>"/dev/tcp/127.0.0.1/${PROXY_PORT}") 2>/dev/null; }

MODE="${1:-}"
case "$MODE" in
    "" | --proxy-only | --restart) ;;
    *)
        echo "usage: start-agent.sh [--proxy-only|--restart]" >&2
        exit 2
        ;;
esac

# A running proxy holds its config from startup, so a changed key or MODEL only
# lands after the old one is gone.
stop_proxy() {
    pkill -f fcc-server 2>/dev/null || true
    for _ in $(seq 1 30); do
        proxy_is_up || return 0
        sleep 1
    done
    echo "!! fcc-server would not stop. Tell the facilitator."
    return 1
}

# LM_STUDIO_BASE_URL is how the room reaches the rented RunPod pod. FCC's
# lmstudio slot is a plain OpenAI-compatible client carrying a fixed credential
# ("lm-studio"), which is exactly the shape vLLM serves — so the pod goes in
# that slot rather than needing a provider of its own. Start vLLM with
# `--api-key lm-studio` and set MODEL=lmstudio/<served-model-name>.
PROVIDER_VARS="GEMINI_API_KEY CEREBRAS_API_KEY GROQ_API_KEY OPENROUTER_API_KEY \
               NVIDIA_NIM_API_KEY OLLAMA_BASE_URL LM_STUDIO_BASE_URL"

have_provider() {
    for var in $PROVIDER_VARS; do
        [ -n "${!var:-}" ] && return 0
    done
    return 1
}

write_env() {
    mkdir -p "$FCC_DIR"
    umask 077
    {
        for var in $PROVIDER_VARS; do
            value="${!var:-}"
            if [ -n "$value" ]; then
                printf '%s="%s"\n' "$var" "$value"
            fi
        done
        printf 'MODEL="%s"\n' "${MODEL:?set MODEL to the provider/model the room is standardised on}"
        # These have to be `if`, not `&&`. A trailing test that comes out false
        # makes the whole function return non-zero, and `set -e` then kills the
        # script here - after .env is written but before the proxy is started.
        if [ -n "${MODEL_HAIKU:-}" ]; then
            printf 'MODEL_HAIKU="%s"\n' "$MODEL_HAIKU"
        fi
        if [ -n "${MODEL_SONNET:-}" ]; then
            printf 'MODEL_SONNET="%s"\n' "$MODEL_SONNET"
        fi
    } > "$FCC_ENV_FILE"
}

if have_provider; then
    write_env
else
    echo "!! No provider key found. Add one as a Codespaces secret and rebuild,"
    echo "!! or pass it here and carry on:"
    echo "!!   GEMINI_API_KEY=your-key .devcontainer/start-agent.sh --restart"
fi

if [ "$MODE" = "--restart" ] && proxy_is_up; then
    echo "stopping fcc-server..."
    stop_proxy
fi

if proxy_is_up; then
    echo "proxy already up on 127.0.0.1:${PROXY_PORT}, serving MODEL=${MODEL:-unset}."
    echo "to change provider or model:"
    echo "  MODEL=<provider>/<model> .devcontainer/start-agent.sh --restart"
else
    echo "starting fcc-server..."
    nohup fcc-server > "$LOG" 2>&1 &
    for _ in $(seq 1 90); do
        proxy_is_up && break
        sleep 1
    done

    if proxy_is_up; then
        echo "proxy up on 127.0.0.1:${PROXY_PORT}, serving MODEL=${MODEL:-unset}."
    else
        echo "!! fcc-server did not come up. Last 30 lines of its log:"
        tail -n 30 "$LOG" || true
        echo "!! Tell the facilitator. You can still read code and run pytest."
        exit 1
    fi
fi

[ "$MODE" = "--proxy-only" ] && exit 0

exec fcc-claude
