"""Layout components for managing title and content separation in Manim scenes."""

from typing import Optional

from manim import (
    DOWN, ORIGIN, UP, WHITE, Text, VGroup, Write, 
    Rectangle, BLACK, config, FadeIn,
)


class TitledSceneLayout:
    """
    A layout manager that keeps title and 3D scene content separated without intersection.
    
    This component creates a two-zone layout:
    - Title zone: Fixed at the top of the frame (fixed to camera, doesn't rotate)
    - Content zone: The main 3D scene area, shifted down slightly
    
    The approach shifts 3D content DOWN slightly so it doesn't overlap with
    the title at the top of the frame.
    
    Usage:
        In your ThreeDScene.construct():
        
        layout = TitledSceneLayout(self, title="My Scene Title")
        layout.setup()
        
        # Content will be shifted down automatically
    """
    
    # Layout constants
    TITLE_HEIGHT_RATIO = 0.12  # Title takes 12% of frame height
    CONTENT_SHIFT_DOWN = 2.0  # Shift 3D content down to avoid title overlap
    TITLE_FONT_SIZE = 42
    TITLE_BUFFER = 0.3  # Distance from top edge
    
    def __init__(
        self,
        scene,  # ThreeDScene instance
        title: str,
        title_font: str = "Menlo",
        title_color=WHITE,
        title_font_size: Optional[int] = None,
        show_separator: bool = False,
    ):
        """
        Initialize the titled scene layout.
        
        Args:
            scene: The Manim ThreeDScene instance
            title: The title text to display
            title_font: Font family for the title
            title_color: Color of the title text
            title_font_size: Override font size (uses default if None)
            show_separator: Whether to show a subtle separator line below title
        """
        self.scene = scene
        self.title_text = title
        self.title_font = title_font
        self.title_color = title_color
        self.title_font_size = title_font_size or self.TITLE_FONT_SIZE
        self.show_separator = show_separator
        
        self._title_mobject = None
        self._separator = None
    
    @property
    def title(self):
        """Get the title mobject after setup."""
        return self._title_mobject
    
    @property  
    def content_origin(self):
        """
        Get the adjusted origin point for 3D content.
        
        Returns a point shifted down to avoid the title area.
        """
        return [0, -self.CONTENT_SHIFT_DOWN, 0]
    
    def setup(self, animate_title: bool = True, run_time: float = 0.4):
        """
        Set up the layout, creating title and adjusting the viewport.
        
        This should be called at the start of construct() before adding
        3D content.
        
        Args:
            animate_title: Whether to animate the title appearance
            run_time: Animation duration for title write
        """
        # Calculate frame dimensions
        frame_height = config.frame_height
        frame_width = config.frame_width
        
        # Create title in the safe zone at the top
        self._title_mobject = Text(
            self.title_text,
            font_size=self.title_font_size,
            color=self.title_color,
            font=self.title_font,
        )
        
        # Position title at the top, with buffer to stay clear of content
        title_y_position = frame_height / 2 - self.TITLE_BUFFER - self._title_mobject.height / 2
        self._title_mobject.move_to([0, title_y_position, 0])
        
        # Fix title to camera frame so it doesn't rotate with 3D view
        self.scene.add_fixed_in_frame_mobjects(self._title_mobject)
        
        # Animate or add title
        if animate_title:
            self.scene.play(Write(self._title_mobject), run_time=run_time)
        else:
            self.scene.add(self._title_mobject)
        
        # Optionally add separator
        if self.show_separator:
            separator_y = title_y_position - self._title_mobject.height / 2 - 0.15
            self._separator = Rectangle(
                width=frame_width * 0.6,
                height=0.01,
                fill_opacity=0.3,
                stroke_width=0,
                color=self.title_color,
            ).move_to([0, separator_y, 0])
            self.scene.add_fixed_in_frame_mobjects(self._separator)
            self.scene.add(self._separator)
    
    def shift_content_down(self, mobject):
        """
        Shift a mobject down to avoid title intersection.
        
        For 3D scenes with overhead camera angles, we shift in the negative Z
        direction to move content visually downward on screen.
        
        Args:
            mobject: The Manim mobject to shift
            
        Returns:
            The shifted mobject (for chaining)
        """
        import numpy as np
        # In 3D scenes viewed from above, negative Z moves content down on screen
        mobject.shift(np.array([0, 0, -self.CONTENT_SHIFT_DOWN]))
        return mobject
    
    def get_camera_adjustments(self):
        """
        Get camera adjustments (currently none needed).
        
        The content-shift approach doesn't require camera adjustments.
        This method is kept for API compatibility.
        
        Returns:
            Empty dict (no camera adjustments needed)
        """
        return {}


def setup_titled_3d_scene(
    scene,
    title: str,
    camera_phi: float = 70,
    camera_theta: float = -50,
    camera_distance: float = 7,
    **layout_kwargs
) -> TitledSceneLayout:
    """
    Convenience function to set up a titled 3D scene with proper camera and layout.
    
    This combines camera setup and layout initialization in one call.
    
    Args:
        scene: The ThreeDScene instance
        title: Title text to display
        camera_phi: Camera elevation angle in degrees
        camera_theta: Camera azimuth angle in degrees  
        camera_distance: Camera distance from origin
        **layout_kwargs: Additional args passed to TitledSceneLayout
        
    Returns:
        TitledSceneLayout instance for further customization
        
    Example:
        def construct(self):
            layout = setup_titled_3d_scene(self, "Loss = Height")
            
            # Add your 3D content - it will be shifted down automatically
            surface = create_surface()
            layout.shift_content_down(surface)
            self.play(Create(surface))
    """
    from manim import DEGREES
    
    # Set up layout
    layout = TitledSceneLayout(scene, title, **layout_kwargs)
    
    # Adjust camera orientation 
    scene.set_camera_orientation(
        phi=camera_phi * DEGREES,
        theta=camera_theta * DEGREES,
        distance=camera_distance,
    )
    
    # Set up the layout (creates title)
    layout.setup()
    
    return layout

