"""Utilities for multiagent workflows.

This module provides utilities for agent identification and workspace
isolation when multiple agents work on the codebase simultaneously.
"""

import os
from pathlib import Path
from typing import Optional


def get_agent_id() -> str:
    """Get the current agent's ID from environment or generate a default.

    The agent ID is used to namespace scratchpad files and other
    agent-specific artifacts to avoid conflicts during parallel work.

    Returns:
        Agent ID from AGENT_ID environment variable, or "default" if not set
    """
    return os.environ.get("AGENT_ID", "default")


def get_agent_scratchpad(base_path: Optional[Path] = None) -> Path:
    """Get the agent-namespaced scratchpad directory.

    Creates the directory if it doesn't exist.

    Args:
        base_path: Optional base path for agent_scratchpad. If not provided,
                   uses the current working directory.

    Returns:
        Path to the agent's namespaced scratchpad directory
    """
    if base_path is None:
        base_path = Path.cwd()

    agent_id = get_agent_id()
    scratchpad = base_path / "agent_scratchpad" / agent_id
    scratchpad.mkdir(parents=True, exist_ok=True)
    return scratchpad


def get_agent_output_dir(base_path: Optional[Path] = None) -> Path:
    """Get the agent-namespaced output directory.

    Creates the directory if it doesn't exist.

    Args:
        base_path: Optional base path for output. If not provided,
                   uses the current working directory.

    Returns:
        Path to the agent's namespaced output directory
    """
    if base_path is None:
        base_path = Path.cwd()

    agent_id = get_agent_id()

    # Default agents share the main output directory
    if agent_id == "default":
        output_dir = base_path / "output"
    else:
        output_dir = base_path / f"output-{agent_id}"

    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def print_agent_info() -> None:
    """Print information about the current agent context.

    Useful for debugging and verifying agent isolation.
    """
    agent_id = get_agent_id()
    scratchpad = get_agent_scratchpad()
    output_dir = get_agent_output_dir()

    print(f"Agent ID: {agent_id}")
    print(f"Scratchpad: {scratchpad}")
    print(f"Output directory: {output_dir}")

    if agent_id == "default":
        print("\n⚠️  Using default namespace. For multiagent work, set AGENT_ID:")
        print('   export AGENT_ID="my-unique-id"')

