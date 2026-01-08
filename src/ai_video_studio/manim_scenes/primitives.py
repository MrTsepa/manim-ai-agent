"""Reusable visual primitives for Manim scenes."""

import numpy as np
from manim import (
    Arrow,
    Arrow3D,
    BLUE,
    BLUE_C,
    BLUE_D,
    BLUE_E,
    DOWN,
    GRAY,
    GREEN,
    LEFT,
    Line,
    ORANGE,
    Rectangle,
    RED,
    RIGHT,
    Sphere,
    Surface,
    Text,
    UP,
    VGroup,
    YELLOW,
)


def create_paraboloid_surface(x_range=(-3, 3), y_range=(-3, 3), resolution=48, color=BLUE_E):
    """
    Create a 3D paraboloid surface (bowl shape) for loss landscape visualization.
    
    Args:
        x_range: Tuple of (min, max) for x-axis
        y_range: Tuple of (min, max) for y-axis
        resolution: Resolution for the surface mesh
        color: Color of the surface
        
    Returns:
        Surface: A Manim Surface object representing a paraboloid
    """
    # Scale down the z values for better visualization
    def paraboloid_func(u, v):
        z = (u * u + v * v) * 0.35  # Scale down height
        return np.array([u, v, z])
    
    surface = Surface(
        paraboloid_func,
        u_range=x_range,
        v_range=y_range,
        resolution=(resolution, resolution),
        fill_opacity=0.85,
        checkerboard_colors=[BLUE_D, BLUE_C],
        stroke_color=BLUE_E,
        stroke_width=0.5,
    )
    return surface


def create_ball(position=(0, 0, 0), color=ORANGE, radius=0.2):
    """
    Create a 3D ball (sphere) to represent a point on the loss landscape.

    Args:
        position: 3D position as (x, y, z) tuple
        color: Color of the ball (default: ORANGE for visibility)
        radius: Radius of the sphere

    Returns:
        Sphere: A Manim Sphere object with enhanced visibility
    """
    ball = Sphere(
        radius=radius,
        resolution=(24, 24),
        fill_color=color,
        fill_opacity=1.0,
        stroke_color=color,
        stroke_width=1,
    ).move_to(position)
    return ball


def create_gradient_arrow(start, end, color=RED):
    """
    Create a 3D arrow representing the gradient direction (steepest descent).
    
    Args:
        start: Starting position as (x, y, z) tuple
        end: Ending position as (x, y, z) tuple
        color: Color of the arrow
        
    Returns:
        Arrow3D: A Manim Arrow3D object
    """
    return Arrow3D(
        start=start,
        end=end,
        color=color,
        resolution=24,
        thickness=0.02,
    )


def get_paraboloid_z(x, y, scale=0.35):
    """
    Calculate the z value on a paraboloid surface for given x, y coordinates.
    
    Args:
        x: x coordinate
        y: y coordinate  
        scale: Scale factor for the paraboloid height
        
    Returns:
        z value on the surface
    """
    return (x * x + y * y) * scale


# =============================================================================
# 2D Physics Primitives
# =============================================================================


def create_ground_line(width: float = 12.4, y_position: float = -0.35, color=GRAY, stroke_width: float = 2):
    """
    Create a horizontal ground line for physics scenes.
    
    Args:
        width: Total width of the ground line
        y_position: Vertical position (negative = below center)
        color: Color of the line
        stroke_width: Thickness of the line
        
    Returns:
        Line: A horizontal line representing the ground
    """
    return Line(
        LEFT * (width / 2),
        RIGHT * (width / 2),
        color=color,
        stroke_width=stroke_width,
    ).shift(DOWN * abs(y_position))


def create_labeled_block(
    label: str,
    width: float = 2.2,
    height: float = 1.2,
    color=BLUE,
    fill_opacity: float = 0.2,
    stroke_width: float = 3,
    font: str = "Menlo",
    font_size: int = 32,
):
    """
    Create a rectangular block with a centered label.
    
    Args:
        label: Text to display in the center of the block
        width: Width of the rectangle
        height: Height of the rectangle
        color: Color of the block outline and label
        fill_opacity: Fill transparency (0 = transparent, 1 = opaque)
        stroke_width: Thickness of the rectangle border
        font: Font family for the label
        font_size: Size of the label text
        
    Returns:
        VGroup: A group containing the rectangle and centered label
    """
    rect = Rectangle(
        width=width,
        height=height,
        color=color,
        fill_opacity=fill_opacity,
        stroke_width=stroke_width,
    )
    text = Text(label, font=font, font_size=font_size, color=color)
    text.move_to(rect.get_center())
    return VGroup(rect, text)


def create_force_arrow(
    start,
    direction,
    length: float = 1.9,
    color=YELLOW,
    buff: float = 0.05,
    max_tip_ratio: float = 0.25,
):
    """
    Create a 2D force arrow for physics diagrams.
    
    Args:
        start: Starting point (numpy array or tuple)
        direction: Direction vector (will be normalized) - use LEFT, RIGHT, UP, DOWN
        length: Length of the arrow
        color: Color of the arrow
        buff: Buffer space at start/end
        max_tip_ratio: Maximum tip length ratio
        
    Returns:
        Arrow: A 2D arrow representing a force
    """
    # Normalize direction and scale by length
    dir_array = np.array(direction[:2] if len(direction) > 2 else direction)
    if len(dir_array) == 2:
        dir_array = np.array([dir_array[0], dir_array[1], 0])
    norm = np.linalg.norm(dir_array)
    if norm > 0:
        dir_array = dir_array / norm
    
    start_array = np.array(start) if not isinstance(start, np.ndarray) else start
    if len(start_array) == 2:
        start_array = np.array([start_array[0], start_array[1], 0])
    
    end = start_array + dir_array * length
    
    return Arrow(
        start=start_array,
        end=end,
        buff=buff,
        color=color,
        max_tip_length_to_length_ratio=max_tip_ratio,
    )


def create_action_reaction_pair(
    contact_point,
    length: float = 1.9,
    color=YELLOW,
    buff: float = 0.05,
    max_tip_ratio: float = 0.25,
):
    """
    Create a pair of equal and opposite force arrows (action-reaction).
    
    Args:
        contact_point: The point where forces meet (numpy array or tuple)
        length: Length of each arrow
        color: Color of both arrows
        buff: Buffer space at start/end
        max_tip_ratio: Maximum tip length ratio
        
    Returns:
        tuple: (action_arrow, reaction_arrow) pointing in opposite directions
    """
    action = create_force_arrow(
        contact_point, RIGHT, length=length, color=color, buff=buff, max_tip_ratio=max_tip_ratio
    )
    reaction = create_force_arrow(
        contact_point, LEFT, length=length, color=color, buff=buff, max_tip_ratio=max_tip_ratio
    )
    return action, reaction

