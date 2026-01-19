# Work in Container Scenario (Agent Workflow)

This document defines the expected end-to-end workflow for agents working on tasks
inside a Docker container. This scenario ensures complete task execution with clear
git history, proper branching, and a final pull request.

## Core Principles

- **Container-first**: All work happens inside the Docker container environment.
- **Git discipline**: Each iteration gets its own commit with clear messages.
- **Branch isolation**: Work on a dedicated branch, never on `main`.
- **Iterative improvement**: Follow the instruction document (e.g., `VIDEO_CREATION_SCENARIO.md`) iteratively.
- **Version selection**: If instructed to select the best version, use git to return to that commit.
- **Complete history**: Every meaningful change is committed for traceability.
- **PR-ready**: End with a pull request containing detailed work summary.

## Prerequisites

- Docker container running (see `DOCKER.md` for setup)
- Git configured in container (name and email)
- Access to repository (SSH or HTTPS)
- OpenAI API key set (if using GPT-5.2 critique)

## Initial Setup (First Steps)

### 1. Verify Repository Status

```bash
# Check that repository is cloned and accessible
cd /workspace
pwd  # Should be /workspace
git status  # Should show clean working tree or current state
git remote -v  # Verify remote is configured
git log --oneline -5  # Verify git history exists
```

If repository is not cloned or missing:
- Check `DOCKER.md` for setup instructions
- Ensure `REPO_URL` environment variable is set correctly
- Rebuild container if necessary: `docker-compose build`

### 2. Configure Git (if needed)

```bash
# Set git user (if not already configured)
git config --global user.name "mrtsepa"
git config --global user.email "tsepa.stas@gmail.com"

# Verify configuration
git config --list | grep user
```

### 3. Create Working Branch

```bash
# Fetch latest changes from remote
git fetch origin

# Create and checkout a new branch for this task
# Use descriptive branch name based on task
BRANCH_NAME="agent-task-$(date +%Y%m%d-%H%M%S)"
# Or use a more descriptive name:
# BRANCH_NAME="feature/softmax-bars-scene"  # Example

git checkout -b ${BRANCH_NAME}
git push -u origin ${BRANCH_NAME}  # Push branch to remote

# Verify branch
git branch  # Should show * next to your branch
```

### 4. Set Up Agent Workspace

```bash
# Set unique agent ID (for multiagent workflows)
export AGENT_ID=${AGENT_ID:-"container-$(hostname)"}

# Create namespaced scratchpad
mkdir -p agent_scratchpad/${AGENT_ID}

# Verify environment
echo "Agent ID: ${AGENT_ID}"
echo "Working branch: $(git branch --show-current)"
echo "Workspace: $(pwd)"
```

## Task Execution Loop

Follow the instruction document (e.g., `@docs/VIDEO_CREATION_SCENARIO.md`) iteratively.
For each iteration cycle, create a commit.

### Iteration Structure

Each iteration follows this pattern:

1. **Read and understand the instruction**
   - Review the instruction document (e.g., `docs/VIDEO_CREATION_SCENARIO.md`)
   - Understand the current state and next steps

2. **Make changes**
   - Implement code changes, scene updates, or fixes
   - Follow the instruction document's workflow
   - Keep changes focused and incremental

3. **Test and verify**
   - Run tests if applicable
   - Render scenes if working on video creation
   - Verify changes work as expected

4. **Commit the iteration**
   ```bash
   # Stage changes
   git add .
   
   # Create descriptive commit message
   # Format: "iteration-N: brief description of changes"
   ITERATION_N=1  # Increment for each iteration
   COMMIT_MSG="iteration-${ITERATION_N}: implement initial scene structure"
   
   git commit -m "${COMMIT_MSG}"
   
   # Optional: Push to remote for backup
   git push origin ${BRANCH_NAME}
   ```

5. **Review and critique** (if applicable)
   - Follow instruction document's review process
   - Use GPT-5.2 critique if specified
   - Document findings

6. **Decide next action**
   - If improvements needed: Continue to next iteration
   - If satisfied: Proceed to finalization
   - If selecting best version: Use git to return to that commit (see below)

### Example: Video Creation Iteration

```bash
# Iteration 1: Initial implementation
git add src/ai_video_studio/manim_scenes/scenes/my_scene.py
git commit -m "iteration-1: implement initial scene structure"

# Iteration 2: Fix layout issues
git add src/ai_video_studio/manim_scenes/scenes/my_scene.py
git commit -m "iteration-2: fix title positioning and spacing"

# Iteration 3: Improve animations
git add src/ai_video_studio/manim_scenes/scenes/my_scene.py
git commit -m "iteration-3: smooth animation timing and transitions"

# Iteration 4: Color and styling improvements
git add src/ai_video_studio/manim_scenes/scenes/my_scene.py
git commit -m "iteration-4: improve color contrast and visual hierarchy"
```

## Version Selection (If Required)

If the instruction document asks you to select the best version from multiple iterations:

### 1. Review Commit History

```bash
# View commit history with messages
git log --oneline --graph -10

# View detailed changes for each commit
git log --stat -5
```

### 2. Identify Best Version

```bash
# List commits with their messages
git log --oneline --all

# Example output:
# abc1234 iteration-4: improve color contrast and visual hierarchy
# def5678 iteration-3: smooth animation timing and transitions
# ghi9012 iteration-2: fix title positioning and spacing
# jkl3456 iteration-1: implement initial scene structure
```

### 3. Return to Selected Commit

```bash
# Option A: Reset to selected commit (if no other work needed)
SELECTED_COMMIT="abc1234"  # Use the commit hash
git reset --hard ${SELECTED_COMMIT}

# Option B: Create a new branch from selected commit (preserves history)
SELECTED_COMMIT="abc1234"
git checkout -b ${BRANCH_NAME}-final ${SELECTED_COMMIT}
git push -u origin ${BRANCH_NAME}-final

# Option C: Cherry-pick selected commit onto current branch
SELECTED_COMMIT="abc1234"
git cherry-pick ${SELECTED_COMMIT}
```

### 4. Document Selection

```bash
# Add a note about why this version was selected
git commit --allow-empty -m "version-selection: selected iteration-4 as best version

Reason: Best balance of visual clarity, animation smoothness, and color contrast.
Score: 9.5/10 from GPT-5.2 critique."
```

## Finalization and Pull Request

### 1. Final Verification

```bash
# Ensure all changes are committed
git status  # Should show "nothing to commit, working tree clean"

# Verify branch is up to date with remote
git fetch origin
git status  # Should show "Your branch is up to date"

# Run final checks
# - Linting (if applicable)
# - Tests (if applicable)
# - Final render/review (if applicable)
```

### 2. Prepare PR Summary

Create a summary document of your work:

```bash
# Create PR summary file
cat > agent_scratchpad/${AGENT_ID}/pr_summary.md << 'EOF'
# Pull Request Summary

## Task Description
[Brief description of what was accomplished]

## Changes Made
- [List key changes]
- [List files modified/created]
- [List iterations completed]

## Iterations
1. **iteration-1**: [Description]
2. **iteration-2**: [Description]
3. **iteration-3**: [Description]
...

## Selected Version
[If applicable] Selected iteration-N as final version.
Reason: [Why this version was chosen]

## Deliverables
- [List final deliverables]
- [Link to outputs if applicable]

## Testing
- [What was tested]
- [How it was verified]

## Notes
[Any additional notes or considerations]
EOF
```

### 3. Create Pull Request

```bash
# Push final commits
git push origin ${BRANCH_NAME}

# Create PR using GitHub CLI (if available)
gh pr create \
  --title "feat: [Task Description]" \
  --body-file agent_scratchpad/${AGENT_ID}/pr_summary.md \
  --base main

# Or create PR manually via GitHub web interface
echo "Create PR at: https://github.com/[org]/[repo]/compare/${BRANCH_NAME}?expand=1"
```

### 4. Alternative: PR via Git Commands

If GitHub CLI is not available, prepare PR details:

```bash
# Display PR information
echo "=== Pull Request Details ==="
echo "Branch: ${BRANCH_NAME}"
echo "Base: main"
echo ""
echo "Title: feat: [Task Description]"
echo ""
echo "Description:"
cat agent_scratchpad/${AGENT_ID}/pr_summary.md
echo ""
echo "Commits:"
git log origin/main..${BRANCH_NAME} --oneline
echo ""
echo "Files changed:"
git diff --stat origin/main..${BRANCH_NAME}
```

## Complete Workflow Example

```bash
# === INITIAL SETUP ===
cd /workspace
git status
git checkout -b agent-task-20241201-120000
export AGENT_ID="container-task-001"
mkdir -p agent_scratchpad/${AGENT_ID}

# === ITERATION 1 ===
# Make changes following VIDEO_CREATION_SCENARIO.md
git add .
git commit -m "iteration-1: implement initial scene structure"
git push origin agent-task-20241201-120000

# === ITERATION 2 ===
# Make improvements based on review
git add .
git commit -m "iteration-2: fix layout and spacing issues"
git push origin agent-task-20241201-120000

# === ITERATION 3 ===
# Further improvements
git add .
git commit -m "iteration-3: improve animations and transitions"
git push origin agent-task-20241201-120000

# === VERSION SELECTION (if needed) ===
git log --oneline -5
# Select iteration-3 as best
git reset --hard <iteration-3-commit-hash>
git push origin agent-task-20241201-120000 --force

# === FINALIZATION ===
git status  # Verify clean
# Create PR summary
# Create pull request
gh pr create --title "feat: Add new scene" --body-file agent_scratchpad/${AGENT_ID}/pr_summary.md
```

## Best Practices

### Commit Messages

- Use clear, descriptive messages
- Format: `iteration-N: brief description`
- Include context about what changed and why
- Reference instruction document if applicable

### Branch Naming

- Use descriptive names: `feature/scene-name`, `fix/issue-description`
- Or timestamp-based: `agent-task-YYYYMMDD-HHMMSS`
- Avoid generic names: `test`, `work`, `fix`

### Commit Frequency

- Commit after each meaningful iteration
- Don't commit broken code (unless documenting a WIP state)
- Don't accumulate too many changes in one commit
- Aim for 3-10 commits per task (depending on complexity)

### Version Selection

- Document why a version was selected
- Preserve git history (prefer new branch over force push)
- Include selection criteria and scores if applicable

### PR Quality

- Write clear, comprehensive PR descriptions
- List all iterations and their purposes
- Include links to outputs/reviews if applicable
- Reference related issues or tasks
- Ensure code is tested and reviewed

## Troubleshooting

### Repository Not Cloned

```bash
# Check if repo exists
ls -la /workspace

# If missing, check environment variables
echo $REPO_URL

# Rebuild container with correct REPO_URL
# See DOCKER.md for instructions
```

### Git Not Configured

```bash
# Configure git user
git config --global user.name "mrtsepa"
git config --global user.email "tsepa.stas@gmail.com"
```

### Cannot Push to Remote

```bash
# Check remote configuration
git remote -v

# Verify SSH access (for SSH remotes)
ssh -T git@github.com

# Check branch tracking
git branch -vv

# Set upstream if needed
git push -u origin ${BRANCH_NAME}
```

### Lost Commit History

```bash
# View reflog to find lost commits
git reflog

# Recover from reflog
git checkout -b recovery-branch <commit-hash-from-reflog>
```

## Integration with Other Scenarios

This scenario works seamlessly with:

- **VIDEO_CREATION_SCENARIO.md**: Follow its iteration loop, commit after each cycle
- **MULTIAGENT_WORKFLOW.md**: Use unique `AGENT_ID` and branch names
- **DOCKER.md**: Ensure container is properly set up before starting

## Checklist

Before starting:
- [ ] Container is running and accessible
- [ ] Repository is cloned and accessible
- [ ] Git is configured (user.name, user.email)
- [ ] Working branch is created
- [ ] Agent ID is set
- [ ] Instruction document is reviewed

During work:
- [ ] Each iteration is committed with clear message
- [ ] Changes are pushed to remote regularly
- [ ] Review artifacts are stored in scratchpad
- [ ] Progress is documented

Before PR:
- [ ] All changes are committed
- [ ] Working tree is clean
- [ ] Final version is selected (if applicable)
- [ ] PR summary is prepared
- [ ] Pull request is created

## Notes

- **Persistent storage**: Outputs and scratchpad are mounted from host, so they persist
- **Git history**: All commits are preserved in container and pushed to remote
- **Multiagent**: Use unique branch names and agent IDs to avoid conflicts
- **Backup**: Push commits regularly to avoid losing work
- **Cleanup**: After PR is merged, branch can be deleted: `git push origin --delete ${BRANCH_NAME}`

