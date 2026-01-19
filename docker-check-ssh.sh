#!/bin/bash
# Quick check if SSH agent forwarding is ready for Docker

echo "Checking SSH agent forwarding setup..."

if [ -z "$SSH_AUTH_SOCK" ]; then
    echo "❌ SSH_AUTH_SOCK is not set"
    echo "   Run: ./docker-setup-ssh.sh"
    exit 1
fi

if ! ssh-add -l &>/dev/null; then
    echo "❌ No SSH keys loaded in agent"
    echo "   Run: ./docker-setup-ssh.sh"
    exit 1
fi

echo "✓ SSH_AUTH_SOCK: $SSH_AUTH_SOCK"
echo "✓ Loaded keys:"
ssh-add -l

echo ""
echo "✓ Ready for Docker! You can run:"
echo "   docker-compose build"
echo "   docker-compose up"

