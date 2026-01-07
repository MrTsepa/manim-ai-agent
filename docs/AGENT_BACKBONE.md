# AI Video Studio Backbone — Coding Agent Guide

This document defines the **backbone** of an AI-first, 3blue1brown-style video studio focused on AI topics.  

You (coding agent) will gradually evolve this into a fully agentic pipeline.  
The first goal is to support **pilot videos** with a semi-automated workflow.

---

## 1. High-level Goal

Build a Python-based system that can:

1. Take a **topic description** (e.g. “Demystifying Attention in Transformers”).
2. Use LLMs (outside of this repo) to produce:
   - A **script** (narration text).
   - A **scene specification** (structured description of what appears on screen).
3. Convert scene specifications into **Manim scenes** (Python code).
4. Render scenes to **video clips**.
5. (Optional in MVP) Sync **voiceover** with scenes using a voiceover library.
6. Provide simple **CLI commands** to run the pipeline.

Later, this will be extended to a **multi-agent, end-to-end system**, but initial focus is on a **solid, testable backbone**.

---

## 2. Tech Stack Assumptions

You should assume and build around:

- **Language**: Python 3.11+  
- **Animation engine**: Manim Community Edition (`manim`)  
- **Voiceover** (later stages): `manim-voiceover` or similar  
- **Project layout**: modern Python package with `pyproject.toml`  
- **Editor**: Cursor (you are the coding agent inside Cursor)  

Avoid hard-coding any proprietary API keys.  
Use environment variables and a `.env` file if needed.

---

## 3. Initial Project Structure

You should maintain/gradually create this structure:

```text
ai_video_studio/
  pyproject.toml
  README.md
  docs/
    AGENT_BACKBONE.md        # this file
  src/
    ai_video_studio/
      __init__.py

      config/
        __init__.py
        settings.py          # basic paths, environment config

      core/
        __init__.py
        types.py             # dataclasses / pydantic models for Script, SceneSpec, etc.
        io.py                # read/write JSON, YAML, etc.
        logging_utils.py     # logging setup

      manim_scenes/
        __init__.py
        base_scene.py        # base scene class with helpers
        primitives.py        # reusable visual primitives (tokens, vectors, etc.)
        demo_scenes.py       # simple demo scenes

      pipeline/
        __init__.py
        generate_scenes.py   # spec -> manim code
        render_scenes.py     # run manim, manage outputs
        cli.py               # CLI entrypoints

  scripts/
    dev_render_demo.sh       # optional helper scripts

  .env.example
  .gitignore
Your job is to create and maintain these files over time.
Not all files must be implemented at once – follow the roadmap below.
4. Core Data Models (MVP)
Define simple, explicit types that describe the content.
Put them in src/ai_video_studio/core/types.py.
4.1 Script-level
@dataclass
class ScriptSegment:
    id: str
    text: str
    start_time: float | None = None   # optional
    end_time: float | None = None     # optional
Later, segments can be aligned with scenes and voiceover timing.
4.2 Scene Specifications
We’ll start with a minimal scene spec that is easy for LLMs and humans to read:
@dataclass
class SceneObjectSpec:
    id: str
    type: str          # e.g. "text", "vector", "point_cloud", "matrix", etc.
    content: str | None = None
    params: dict[str, Any] | None = None

@dataclass
class SceneActionSpec:
    time: float        # seconds from scene start
    action_type: str   # e.g. "create", "fade_out", "move_to", "transform", "highlight"
    target_id: str     # object id
    params: dict[str, Any] | None = None

@dataclass
class SceneSpec:
    id: str
    title: str
    duration: float
    narration_segment_ids: list[str]
    objects: list[SceneObjectSpec]
    actions: list[SceneActionSpec]
Later, we can add camera motions, layers, etc.
5. Manim Backbone
5.1 Base Scene
Create a base Manim scene in manim_scenes/base_scene.py:
Wrap Scene or MovingCameraScene.
Provide helper methods to:
Create text with consistent style.
Create common primitives (axes, vectors, arrows, boxes).
Map SceneActionSpec → actual Manim animations.
Example (high-level idea):
class SpecDrivenScene(Scene):
    def __init__(self, scene_spec: SceneSpec, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_spec = scene_spec
        self.objects: dict[str, Mobject] = {}

    def construct(self):
        self._create_objects()
        self._play_actions()

    def _create_objects(self):
        # Use self.scene_spec.objects to create Mobjects and store in self.objects

    def _play_actions(self):
        # Iterate over actions in time order and call self.play(...)
You (agent) will fill in the actual implementation over time.
5.2 Visual Primitives
In manim_scenes/primitives.py, define reusable functions:
create_token_row(tokens: list[str]) -> VGroup
create_loss_landscape_axes(...) -> VGroup
create_attention_matrix(...) -> Mobject
etc.
These functions will be the building blocks the LLM will reference in specs.
6. Pipeline Backbone
6.1 Scene Spec → Manim Code
In pipeline/generate_scenes.py:
Implement functions that:
Load SceneSpec from JSON/YAML.
Generate a Python file containing a Manim scene class that instantiates SpecDrivenScene with that spec.
OR: keep scenes as data and build dynamic scenes (preferred for now).
MVP strategy:
Start with a single Python module (demo_scenes.py) where we manually create a few SceneSpec instances and corresponding SpecDrivenScene classes.
Once stable, we can add automated code generation.
6.2 Rendering
In pipeline/render_scenes.py:
Implement a function render_scene(scene_class: type[Scene], output_dir: Path, quality: str):
Use manim programmatically via Scene.render() or via a subprocess call to manim CLI.
Provide a small CLI wrapper in pipeline/cli.py:
python -m ai_video_studio.pipeline.cli render --scene demo_loss_landscape
Basic CLI goals:
render --scene <name>
Future: render-all, render-from-spec <file.json>, etc.
7. MVP Roadmap for the Coding Agent
Follow these steps in order.
Each step should result in compilable, reasonably tested code.
Step 1 — Project skeleton
 Create pyproject.toml with:
Package name: ai_video_studio
Dependencies: manim, pydantic or dataclasses, python-dotenv (optional)
 Create base folder structure as described above.
 Add simple README.md describing how to install and run a demo.
Step 2 — Core types & config
 Implement core/types.py with:
ScriptSegment
SceneObjectSpec
SceneActionSpec
SceneSpec
 Implement config/settings.py:
Default paths (e.g., output directory).
Helper function to load .env if needed.
Step 3 — Basic Manim demo (no specs yet)
 Implement a simple, hard-coded demo scene in manim_scenes/demo_scenes.py:
Show a function on axes.
Animate a point moving along the curve.
 Add CLI command render-demo that renders this demo scene.
This ensures that Manim is correctly wired up before spec-driven logic.
Step 4 — Spec-driven scene prototype
 Implement SpecDrivenScene in base_scene.py.
 In demo_scenes.py, create a small SceneSpec instance in Python.
 Use SpecDrivenScene to construct the scene from that SceneSpec.
 Extend the CLI with:
render-spec-demo which renders the spec-driven scene.
Step 5 — External scene spec file
 Implement JSON read/write in core/io.py.
 Create a demo_scene_spec.json file in a configs/ or assets/ directory.
 Add CLI command:
render-from-spec --spec-path path/to/json
 The command:
Loads the JSON spec.
Instantiates a SceneSpec.
Renders a generic SpecDrivenScene using this spec.
At this point, the system can render scenes whose definition lives entirely in data.
This is where LLM agents will plug in later.
8. Coding Style & Constraints for the Agent
When modifying or creating code:
Prefer clear, explicit Python over clever tricks.
Add docstrings to public functions and classes.
Keep functions short and focused.
Use type hints consistently.
Where possible, add minimal unit tests (later we can add a tests/ directory).
Example design principles:
Separation of concerns:
Core data models (types) must not depend on Manim.
Manim-specific code lives under manim_scenes/.
Orchestration and CLI live under pipeline/.
No hard-coded absolute paths:
Use Path(__file__).resolve().parent-based paths or config.
9. Future Extensions (for later phases)
Do not implement these yet; just keep them in mind:
Integrate manim-voiceover to sync script segments with animations.
Add support for camera movements in SceneSpec.
Add an “evaluation mode” that exports thumbnails or GIFs for QA.
Add orchestration scripts to connect to external LLMs that:
Generate ScriptSegments.
Generate SceneSpecs.
10. How the Agent Should Use This Document
Treat this file as the single source of truth for project structure and priorities.
When in doubt:
Prefer finishing and polishing existing modules over adding new ones.
Keep this document in sync:
If you significantly change structure or design, update this markdown accordingly.
The immediate next action for you (coding agent) is:
Implement Steps 1–3 of the MVP roadmap, so we have a runnable project with at least one hard-coded Manim demo and a clear place to plug in spec-driven scenes.