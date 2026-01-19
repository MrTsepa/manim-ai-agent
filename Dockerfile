# Dockerfile for AI Video Studio
# Provides environment for video creation workflow with Manim, ffmpeg, and Codex SDK

FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    AGENT_ID=default \
    UV_SYSTEM_PYTHON=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    openssh-client \
    ca-certificates \
    gnupg \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list \
    && apt-get update && apt-get install -y --no-install-recommends \
    nodejs \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    ffmpeg \
    libcairo2-dev \
    libpango1.0-dev \
    libpangocairo-1.0-0 \
    libgirepository1.0-dev \
    fonts-dejavu \
    fonts-dejavu-core \
    fonts-dejavu-extra \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mkdir -p /root/.cargo/bin /root/.local/bin && \
    (test -f /root/.cargo/bin/uv || test -f /root/.local/bin/uv || which uv) && \
    uv --version || /root/.local/bin/uv --version || /root/.cargo/bin/uv --version
ENV PATH="/root/.cargo/bin:/root/.local/bin:$PATH"

# Install Codex CLI and SDK
RUN npm install -g @openai/codex@latest @openai/codex-sdk

# Set up SSH for GitHub access
RUN mkdir -p /root/.ssh && \
    chmod 700 /root/.ssh && \
    ssh-keyscan -t rsa,ecdsa,ed25519 github.com >> /root/.ssh/known_hosts 2>/dev/null || \
    ssh-keyscan -t rsa github.com >> /root/.ssh/known_hosts 2>/dev/null || true && \
    chmod 644 /root/.ssh/known_hosts

# Set working directory
WORKDIR /workspace

# Clone repository using SSH agent forwarding (BuildKit --ssh flag)
ARG REPO_URL
ARG REPO_BRANCH=main
ARG REPO_REF=HEAD

RUN --mount=type=ssh \
    if [ -z "$REPO_URL" ]; then \
        echo "Error: REPO_URL build argument is required. Build with: docker build --build-arg REPO_URL=<url> ."; \
        exit 1; \
    fi && \
    echo "Cloning repository: $REPO_URL (branch: ${REPO_BRANCH})" && \
    git clone --depth 1 --branch "${REPO_BRANCH}" "$REPO_URL" /workspace/repo_temp && \
    cd /workspace/repo_temp && \
    if [ "$REPO_REF" != "HEAD" ]; then \
        git fetch --depth 1 origin "$REPO_REF" 2>/dev/null || git fetch origin "$REPO_REF" && \
        git checkout "$REPO_REF"; \
    fi && \
    echo "Repository cloned successfully." && \
    cd /workspace && \
    cp -r /workspace/repo_temp/* /workspace/ && \
    cp -r /workspace/repo_temp/.[!.]* /workspace/ 2>/dev/null || true && \
    rm -rf /workspace/repo_temp && \
    echo "Files copied to workspace."

# Create output directories
RUN mkdir -p output/videos agent_scratchpad samples_artifacts

# Install Python dependencies
RUN if [ -f pyproject.toml ]; then \
        if [ -f uv.lock ]; then \
            uv sync --frozen; \
        else \
            uv sync; \
        fi; \
    fi

# Make scripts executable
RUN chmod +x scripts/*.py 2>/dev/null || true

# Install Codex SDK locally
RUN mkdir -p /usr/local/lib/codex-sdk-runner && \
    cd /usr/local/lib/codex-sdk-runner && \
    npm init -y && \
    npm install @openai/codex-sdk

# Copy scripts
COPY docker-entrypoint.sh /entrypoint.sh
COPY codex-sdk-runner.js /usr/local/bin/codex-sdk
RUN chmod +x /entrypoint.sh /usr/local/bin/codex-sdk

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]

