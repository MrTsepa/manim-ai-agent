"""Reusable visual primitives for Manim scenes."""

import numpy as np
from manim import Arrow3D, BLUE_C, BLUE_D, BLUE_E, ORANGE, RED, Sphere, Surface


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

