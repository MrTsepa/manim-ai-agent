# Docker Setup for AI Video Studio

This document explains how to run the AI Video Studio video creation scenario agent in Docker.

## Prerequisites

- Docker installed and running
- Docker Compose (optional, but recommended)
- OpenAI API key (for GPT-5.2 critique script and Codex CLI)
- Git repository URL (the Dockerfile clones the repo during build)
- **For private repositories**: SSH agent forwarding enabled (ssh-agent running with keys added)

## Quick Start

### Using Docker Compose (Recommended)

1. **Set up environment variables:**

   Create a `.env` file in the project root:
   ```bash
   # Required: Repository URL to clone (use SSH format for private repos)
   REPO_URL=git@github.com:your-org/ai-video-studio.git
   # Or use HTTPS for public repos:
   # REPO_URL=https://github.com/your-org/ai-video-studio.git
   # Optional: Branch or ref to checkout
   REPO_BRANCH=main
   REPO_REF=HEAD
   
   # Required: OpenAI API key
   OPENAI_API_KEY=your-api-key-here
   # Optional: Agent ID for multiagent workflows
   AGENT_ID=my-agent-id
   ```

   **For private repositories with SSH agent forwarding:**
   
   The `docker-compose.yml` uses SSH agent forwarding to securely access GitHub without copying keys.
   Set up SSH agent forwarding before building:
   
   **Option 1: Use the helper script (recommended):**
   ```bash
   ./docker-setup-ssh.sh
   ```
   
   **Option 2: Manual setup:**
   ```bash
   # Start ssh-agent if not already running
   eval $(ssh-agent)
   
   # Add your SSH key to the agent
   ssh-add ~/.ssh/id_rsa  # or id_ed25519, id_ed25519_sk, etc.
   
   # Test SSH access to GitHub
   ssh -T git@github.com
   
   # Ensure SSH_AUTH_SOCK is set (usually set automatically by ssh-agent)
   echo $SSH_AUTH_SOCK
   ```
   
   **Note:** 
   - On macOS with Docker Desktop, the SSH agent socket is automatically forwarded at `/run/host-services/ssh-auth.sock`
   - On Linux, ensure `SSH_AUTH_SOCK` is set in your environment (set by ssh-agent)

2. **Build and run:**

   ```bash
   docker-compose up --build
   ```

   This will:
   - Clone the repository from `REPO_URL` into the container using SSH agent forwarding
   - Build the Docker image with all dependencies
   - Install Codex CLI globally
   - Start an interactive container
   - Mount output directories for persistence
   - Forward SSH agent for GitHub access at runtime

4. **Inside the container, run the workflow:**

   ```bash
   # List available scenes
   uv run python -m ai_video_studio.pipeline.cli list-scenes

   # Render a scene at low quality
   uv run python -m ai_video_studio.pipeline.cli render-scene ParabolicMotionScene --quality low_quality

   # Create review GIF
   export AGENT_ID=${AGENT_ID:-default}
   mkdir -p agent_scratchpad/${AGENT_ID}
   ffmpeg -loglevel error -i output/videos/480p15/ParabolicMotionScene.mp4 \
     -vf "fps=10,scale=320:-1:flags=lanczos" \
     -y agent_scratchpad/${AGENT_ID}/review.gif

   # Extract frames
   ffmpeg -loglevel error -y -ss 00:00:03 -i output/videos/480p15/ParabolicMotionScene.mp4 \
     -vframes 1 -update 1 agent_scratchpad/${AGENT_ID}/frame_3s.png
   ffmpeg -loglevel error -y -ss 00:00:06 -i output/videos/480p15/ParabolicMotionScene.mp4 \
     -vframes 1 -update 1 agent_scratchpad/${AGENT_ID}/frame_6s.png

   # Get GPT-5.2 critique
   python scripts/gpt52_video_critique.py \
     --gif agent_scratchpad/${AGENT_ID}/review.gif \
     --frames agent_scratchpad/${AGENT_ID}/frame_3s.png agent_scratchpad/${AGENT_ID}/frame_6s.png
   
   # Use Codex CLI
   codex --help
   ```

### Using Docker Directly

1. **Build the image:**

   ```bash
   # For private repos with SSH agent forwarding:
   # Ensure ssh-agent is running and your key is added first:
   # eval $(ssh-agent) && ssh-add ~/.ssh/id_rsa
   
   docker build \
     --build-arg REPO_URL=git@github.com:your-org/ai-video-studio.git \
     --build-arg REPO_BRANCH=main \
     --ssh default \
     -t ai-video-studio .
   
   # For public repos with HTTPS (no SSH needed):
   docker build \
     --build-arg REPO_URL=https://github.com/your-org/ai-video-studio.git \
     --build-arg REPO_BRANCH=main \
     -t ai-video-studio .
   ```

2. **Run the container:**

   ```bash
   # With SSH agent forwarding (recommended for private repos):
   # Ensure ssh-agent is running: eval $(ssh-agent) && ssh-add ~/.ssh/id_rsa
   
   docker run -it --rm \
     -e OPENAI_API_KEY=your-api-key-here \
     -e AGENT_ID=my-agent-id \
     -e SSH_AUTH_SOCK=${SSH_AUTH_SOCK:-/run/host-services/ssh-auth.sock} \
     -v ${SSH_AUTH_SOCK:-/run/host-services/ssh-auth.sock}:${SSH_AUTH_SOCK:-/run/host-services/ssh-auth.sock} \
     -v $(pwd)/output:/workspace/output \
     -v $(pwd)/agent_scratchpad:/workspace/agent_scratchpad \
     ai-video-studio
   ```
   
   **Note:** On macOS Docker Desktop, the SSH agent socket path is `/run/host-services/ssh-auth.sock`.
   On Linux, use `$SSH_AUTH_SOCK` from your environment.

## What's Included

The Docker image includes:

- **Python 3.11** - Required Python version
- **Node.js and npm** - For Codex CLI installation
- **Codex CLI** - OpenAI Codex CLI installed globally (`@openai/codex`)
- **uv** - Python package manager (faster than pip)
- **Git** - For cloning the repository
- **OpenSSH Client** - For SSH access to private GitHub repositories
- **Manim dependencies:**
  - LaTeX (texlive) for math rendering
  - Cairo and Pango for graphics
  - Fonts (DejaVu Sans Mono as Menlo alternative)
- **ffmpeg** - For video processing and GIF creation
- **ImageMagick** - Additional image processing tools
- **Repository code** - Cloned from the specified `REPO_URL` during build
- **All Python dependencies** from `pyproject.toml`

## Volume Mounts

The docker-compose.yml mounts:

- **SSH agent socket** - For SSH agent forwarding (more secure than mounting keys)
- **Output directory** (`./output`) - For rendered videos (persists on host)
- **Agent scratchpad** (`./agent_scratchpad`) - For review artifacts (persists on host)
- **Samples artifacts** (`./samples_artifacts`) - For approved samples (persists on host)

**Note:** 
- By default, the project code is cloned into the container during build. To use local code for development, uncomment the project directory mount in `docker-compose.yml`:
  ```yaml
  volumes:
    - .:/workspace  # Uncomment this line to override cloned repo with local code
  ```
- SSH agent forwarding is used instead of mounting SSH keys for better security. Your SSH keys never leave your host machine.

## Multiagent Workflows

For multiagent workflows, set unique `AGENT_ID` environment variables:

```bash
# Agent 1
docker-compose run -e AGENT_ID=agent-1 video-studio bash

# Agent 2
docker-compose run -e AGENT_ID=agent-2 video-studio bash
```

Each agent will have its own namespaced scratchpad: `agent_scratchpad/agent-1/`, `agent_scratchpad/agent-2/`, etc.

## Troubleshooting

### LaTeX Errors

If you see LaTeX-related errors, the minimal LaTeX installation might need additional packages. You can extend the Dockerfile to install more texlive packages:

```dockerfile
texlive-latex-base \
texlive-latex-extra \
texlive-fonts-recommended \
texlive-fonts-extra \
texlive-latex-recommended \
```

### Font Issues

The Docker image uses DejaVu Sans Mono as an alternative to macOS's Menlo font. If you need specific fonts, you can:

1. Install additional fonts in the Dockerfile
2. Mount a fonts directory from your host
3. Use system fonts available in the container

### Permission Issues

If you encounter permission issues with mounted volumes, ensure your user has write permissions, or adjust the Dockerfile to create directories with appropriate permissions.

## Development Tips

- **Repository cloning**: The repo is cloned during image build. To use local code, mount your project directory.
- **Codex CLI**: Use `codex` command for AI-assisted coding tasks. Requires `OPENAI_API_KEY`.
- **Persistent data**: Outputs persist on your host machine via volume mounts
- **Isolated environment**: Each container has its own Python environment
- **Fast iteration**: Use low quality renders (`--quality low_quality`) for quick feedback
- **Rebuild for updates**: If you need the latest code from the repo, rebuild the image with `docker-compose build`

## Example Complete Workflow

```bash
# 1. Start container
docker-compose up -d

# 2. Execute commands
docker-compose exec video-studio bash -c "
  export AGENT_ID=test-agent
  mkdir -p agent_scratchpad/\${AGENT_ID}
  
  # Render scene
  uv run python -m ai_video_studio.pipeline.cli render-scene ParabolicMotionScene --quality low_quality
  
  # Create review artifacts
  ffmpeg -loglevel error -i output/videos/480p15/ParabolicMotionScene.mp4 \
    -vf 'fps=10,scale=320:-1:flags=lanczos' \
    -y agent_scratchpad/\${AGENT_ID}/review.gif
  
  # Get critique
  python scripts/gpt52_video_critique.py \
    --gif agent_scratchpad/\${AGENT_ID}/review.gif \
    --summary
"

# 3. Check outputs on host
ls -lh output/videos/480p15/
ls -lh agent_scratchpad/test-agent/
```

