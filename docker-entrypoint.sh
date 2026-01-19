#!/bin/bash
set -e

# Set up SSH for GitHub access at runtime using agent forwarding
if [ -n "$SSH_AUTH_SOCK" ] && [ -S "$SSH_AUTH_SOCK" ]; then
    export SSH_AUTH_SOCK
    echo "SSH agent forwarding enabled via: $SSH_AUTH_SOCK"
    
    # Ensure known_hosts exists for GitHub
    mkdir -p /root/.ssh
    chmod 700 /root/.ssh 2>/dev/null || true
    
    # Add GitHub to known_hosts if not already present
    if [ ! -f /root/.ssh/known_hosts ] || ! grep -q "github.com" /root/.ssh/known_hosts 2>/dev/null; then
        ssh-keyscan -t rsa,ecdsa,ed25519 github.com >> /root/.ssh/known_hosts 2>/dev/null || \
        ssh-keyscan -t rsa github.com >> /root/.ssh/known_hosts 2>/dev/null || true
        chmod 644 /root/.ssh/known_hosts 2>/dev/null || true
    fi
fi

# Set agent ID if provided
if [ -n "$AGENT_ID" ]; then
    export AGENT_ID
    mkdir -p "agent_scratchpad/${AGENT_ID}"
fi

# If no arguments provided, show help
if [ $# -eq 0 ]; then
    echo "AI Video Studio - Video Creation Scenario Agent"
    echo ""
    echo "Available commands:"
    echo "  uv run python -m ai_video_studio.pipeline.cli render-scene <SceneName> --quality low_quality"
    echo "  uv run python -m ai_video_studio.pipeline.cli list-scenes"
    echo "  uv run python -m ai_video_studio.pipeline.cli agent-info"
    echo "  python scripts/gpt52_video_critique.py --gif <path> --frames <frame1> <frame2> ..."
    echo "  codex-sdk <command>  # Codex SDK (uses OPENAI_API_KEY)"
    echo "  codex <command>  # Codex CLI (requires auth setup)"
    echo ""
    echo "Example workflow:"
    echo "  1. Render a scene:"
    echo "     uv run python -m ai_video_studio.pipeline.cli render-scene ParabolicMotionScene --quality low_quality"
    echo "  2. Create review GIF:"
    echo "     ffmpeg -loglevel error -i output/videos/480p15/ParabolicMotionScene.mp4 -vf \"fps=10,scale=320:-1:flags=lanczos\" -y agent_scratchpad/\${AGENT_ID:-default}/review.gif"
    echo "  3. Extract frames:"
    echo "     ffmpeg -loglevel error -y -ss 00:00:03 -i output/videos/480p15/ParabolicMotionScene.mp4 -vframes 1 -update 1 agent_scratchpad/\${AGENT_ID:-default}/frame_3s.png"
    echo "  4. Get critique:"
    echo "     python scripts/gpt52_video_critique.py --gif agent_scratchpad/\${AGENT_ID:-default}/review.gif --frames agent_scratchpad/\${AGENT_ID:-default}/frame_3s.png"
    echo ""
    echo "Environment variables:"
    echo "  AGENT_ID: Set unique agent ID for multiagent workflows (default: default)"
    echo "  OPENAI_API_KEY: Required for GPT-5.2 critique script and Codex SDK"
    exec bash
else
    exec "$@"
fi

