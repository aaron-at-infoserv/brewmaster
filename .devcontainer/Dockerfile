# Brewmaster workshop container: Claude Code + the Free Claude Code proxy,
# ready to run inside a GitHub Codespace.
#
# Everything slow or network-dependent is baked in here so that on the day a
# participant's laptop only ever talks to github.com. Enable Codespaces
# prebuilds on main and starting one takes seconds rather than minutes.
#
# No API key is baked in. Keys arrive as Codespaces secrets — see
# devcontainer.json and .devcontainer/start-agent.sh.

FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

# Tools the agent reaches for, plus what the workshop scripts need.
RUN apt-get update && apt-get install -y --no-install-recommends \
        jq \
        less \
        procps \
        ripgrep \
    && rm -rf /var/lib/apt/lists/*

USER vscode
WORKDIR /home/vscode

# brewmaster's dependencies, pre-installed so nobody waits on PyPI on the day.
# Keep this list in step with pyproject.toml.
RUN pip install --no-cache-dir --user \
        "fastapi>=0.110" \
        "uvicorn>=0.27" \
        "pytest>=8.0" \
        "httpx>=0.27" \
        "ruff>=0.4"

# Installs uv, a pinned Python, Free Claude Code, Claude Code, Codex and Pi.
# There is no TTY during a build, so the installer skips its interactive
# agent-selection prompt and installs everything.
RUN curl -fsSL "https://raw.githubusercontent.com/Alishahryar1/free-claude-code/main/scripts/install.sh" | sh

ENV PATH="/home/vscode/.local/bin:/home/vscode/bin:${PATH}"

# Without this, Claude Code asks to log in even with the proxy configured.
RUN printf '{\n  "hasCompletedOnboarding": true\n}\n' > /home/vscode/.claude.json \
    && mkdir -p /home/vscode/.fcc /home/vscode/.claude

ENV DISABLE_AUTOUPDATER=1 \
    DISABLE_FEEDBACK_COMMAND=1 \
    DISABLE_ERROR_REPORTING=1 \
    CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1
