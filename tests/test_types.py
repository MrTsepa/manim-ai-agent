"""Tests for core data types."""

from ai_video_studio.core.types import (
    SceneActionSpec,
    SceneObjectSpec,
    SceneSpec,
    ScriptSegment,
)


class TestScriptSegment:
    """Tests for ScriptSegment dataclass."""

    def test_create_minimal(self):
        """Test creating a segment with required fields only."""
        segment = ScriptSegment(id="seg1", text="Hello world")
        assert segment.id == "seg1"
        assert segment.text == "Hello world"
        assert segment.start_time is None
        assert segment.end_time is None

    def test_create_with_times(self):
        """Test creating a segment with timing information."""
        segment = ScriptSegment(
            id="seg1",
            text="Hello world",
            start_time=0.0,
            end_time=2.5,
        )
        assert segment.start_time == 0.0
        assert segment.end_time == 2.5


class TestSceneObjectSpec:
    """Tests for SceneObjectSpec dataclass."""

    def test_create_minimal(self):
        """Test creating an object spec with required fields only."""
        obj = SceneObjectSpec(id="obj1", type="point")
        assert obj.id == "obj1"
        assert obj.type == "point"
        assert obj.content is None
        assert obj.params is None

    def test_create_with_params(self):
        """Test creating an object spec with parameters."""
        obj = SceneObjectSpec(
            id="surface1",
            type="surface",
            params={"function": "paraboloid", "color": "BLUE_E"},
        )
        assert obj.params["function"] == "paraboloid"
        assert obj.params["color"] == "BLUE_E"


class TestSceneActionSpec:
    """Tests for SceneActionSpec dataclass."""

    def test_create_minimal(self):
        """Test creating an action spec with required fields only."""
        action = SceneActionSpec(
            time=0.0,
            action_type="create",
            target_id="obj1",
        )
        assert action.time == 0.0
        assert action.action_type == "create"
        assert action.target_id == "obj1"
        assert action.params is None

    def test_create_with_params(self):
        """Test creating an action spec with parameters."""
        action = SceneActionSpec(
            time=1.5,
            action_type="move_to",
            target_id="ball",
            params={"position": [1.0, 2.0, 3.0]},
        )
        assert action.params["position"] == [1.0, 2.0, 3.0]


class TestSceneSpec:
    """Tests for SceneSpec dataclass."""

    def test_create_complete_scene(self):
        """Test creating a complete scene specification."""
        spec = SceneSpec(
            id="test_scene",
            title="Test Scene",
            duration=5.0,
            narration_segment_ids=["seg1", "seg2"],
            objects=[
                SceneObjectSpec(id="obj1", type="point"),
                SceneObjectSpec(id="obj2", type="surface"),
            ],
            actions=[
                SceneActionSpec(time=0.0, action_type="create", target_id="obj1"),
                SceneActionSpec(time=1.0, action_type="create", target_id="obj2"),
            ],
        )
        assert spec.id == "test_scene"
        assert spec.title == "Test Scene"
        assert spec.duration == 5.0
        assert len(spec.narration_segment_ids) == 2
        assert len(spec.objects) == 2
        assert len(spec.actions) == 2

    def test_empty_scene(self):
        """Test creating a scene with empty lists."""
        spec = SceneSpec(
            id="empty",
            title="Empty Scene",
            duration=0.0,
            narration_segment_ids=[],
            objects=[],
            actions=[],
        )
        assert spec.objects == []
        assert spec.actions == []
