#!/bin/bash
# Helper script to set up SSH agent forwarding for Docker builds

set -e

echo "Setting up SSH agent forwarding for Docker..."

# Check if ssh-agent is running
if [ -z "$SSH_AUTH_SOCK" ]; then
    echo "Starting ssh-agent..."
    eval $(ssh-agent)
fi

# Check if keys are loaded
if ssh-add -l 2>/dev/null | grep -q "no identities"; then
    echo "No SSH keys found in agent. Adding default keys..."
    
    # Try common key locations
    for key in ~/.ssh/id_ed25519 ~/.ssh/id_rsa ~/.ssh/id_ecdsa; do
        if [ -f "$key" ]; then
            echo "Adding $key..."
            ssh-add "$key"
            break
        fi
    done
    
    # Check again
    if ssh-add -l 2>/dev/null | grep -q "no identities"; then
        echo "Warning: No SSH keys found. Please add your key manually:"
        echo "  ssh-add ~/.ssh/your_key"
        exit 1
    fi
fi

echo "SSH agent is ready:"
ssh-add -l

echo ""
echo "Testing GitHub SSH access..."
if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
    echo "✓ GitHub SSH access confirmed"
else
    echo "⚠ GitHub SSH test completed (this is normal)"
fi

echo ""
echo "SSH_AUTH_SOCK=$SSH_AUTH_SOCK"
echo ""
echo "You can now run:"
echo "  docker-compose build"
echo "  docker-compose up"

