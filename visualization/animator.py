"""
animator.py - The Visiontegral Cinematic Visualization Engine
------------------------------------------------------------
State-of-the-art mathematical rendering system using Manim.
Designed for high-impact presentations and scientific storytelling.

Author: Visionis
License: MIT
"""

import numpy as np
import logging
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple, Union

# Third-party libraries (Graceful degradation check could be added here)
from manim import *
from core.engine import IntegrationResult

# --- Configuration Layer ---

@dataclass(frozen=True)
class ThemeConfig:
    """Defines the visual identity of the animation."""
    background_color: str = "#0F172A"  # Deep Space Blue
    surface_color_a: str = BLUE_D
    surface_color_b: str = TEAL_D
    point_color: str = YELLOW_E
    axis_color: str = GREY_B
    text_font: str = "Arial"  # System safe font
    hud_color: str = WHITE

@dataclass
class RenderSettings:
    """Controls quality and performance parameters."""
    max_visible_points: int = 2000  # Cap points to prevent lag
    camera_rotation_speed: float = 0.05
    run_time_creation: float = 3.0
    run_time_points: float = 4.0

# --- The Engine ---

class VisiontegralScene(ThreeDScene):
    """
    Base scene class extended with Visiontegral specific capabilities.
    Acts as a wrapper around Manim's engine.
    """
    def __init__(self, theme: ThemeConfig = ThemeConfig(), settings: RenderSettings = RenderSettings(), **kwargs):
        super().__init__(**kwargs)
        self.theme = theme
        self.settings = settings
        self.camera.background_color = self.theme.background_color
        self.logger = logging.getLogger("VisiontegralAnimator")

    def create_hud(self, result: IntegrationResult):
        """Creates a futuristic Heads-Up Display (HUD) fixed to the screen corners."""
        # Note: In 3D scenes, adding fixed 2D elements requires careful layering.
        
        info_group = VGroup()
        
        # Title
        title = Text("VISIONTEGRAL", font=self.theme.text_font, weight=BOLD, font_size=32)
        title.set_color(self.theme.surface_color_b)
        title.to_corner(UL)
        
        # Stats Block
        stats_text = (
            f"Dimension: {result.dimension}D\n"
            f"Value: {result.value:.6f}\n"
            f"Error: ±{result.error_estimate:.6e}\n"
            f"Samples: {result.samples:,}"
        )
        stats = Text(stats_text, font=self.theme.text_font, font_size=20, line_spacing=1.2)
        stats.set_color(self.theme.hud_color)
        stats.to_corner(DL)
        
        # Add a background box for readability
        bg_box = SurroundingRectangle(stats, color=self.theme.axis_color, fill_opacity=0.2, buff=0.2)
        
        # Combine HUD elements and fix them to camera frame (2D layer)
        self.add_fixed_in_frame_mobjects(title, bg_box, stats)
        
        return VGroup(title, bg_box, stats)

    def visualize_integration(self, 
                            func: Callable[[np.ndarray], float], 
                            bounds: List[Tuple[float, float]], 
                            result: IntegrationResult):
        """
        Main orchestration method for generating the integration movie.
        """
        self.logger.info("Starting visualization render sequence...")

        if len(bounds) != 2:
            self.logger.warning("Visualizer currently optimizes 2D -> 1D projections. Higher dims will be sliced.")
            # Future-proof: Logic for slicing higher dimensions could go here.

        # 1. Setup Axes (The Stage)
        x_min, x_max = bounds[0]
        y_min, y_max = bounds[1]
        
        # Auto-scale Z axis based on function samples (smart scaling)
        test_points = np.array([[x_min, y_min], [x_max, y_max], [(x_min+x_max)/2, (y_min+y_max)/2]])
        z_vals = [func(p.reshape(1, -1))[0] for p in test_points]
        z_max_est = max(z_vals) * 1.5 if z_vals else 5.0

        axes = ThreeDAxes(
            x_range=[x_min, x_max, (x_max-x_min)/5],
            y_range=[y_min, y_max, (y_max-y_min)/5],
            z_range=[0, z_max_est, z_max_est/5],
            axis_config={"include_tip": False, "color": self.theme.axis_color}
        )
        
        labels = axes.get_axis_labels(x_label="x", y_label="y", z_label="f(x,y)")
        
        # 2. Setup Camera
        self.set_camera_orientation(phi=70 * DEGREES, theta=-30 * DEGREES)
        
        # 3. Create Surface (The Math)
        def param_surface(u, v):
            val = func(np.array([[u, v]]))[0]
            return axes.c2p(u, v, val)

        surface = Surface(
            param_surface,
            u_range=[x_min, x_max],
            v_range=[y_min, y_max],
            resolution=(32, 32), # Optimized resolution
            should_make_jagged=False
        )
        
        surface.set_style(fill_opacity=0.7)
        surface.set_fill_by_checkerboard(self.theme.surface_color_a, self.theme.surface_color_b, opacity=0.7)

        # 4. Monte Carlo Particles (The Data)
        particles = VGroup()
        # Intelligent Downsampling: Don't render 1M points, render enough to "look" like 1M
        render_count = min(result.samples, self.settings.max_visible_points)
        
        raw_points = np.random.uniform(
            [x_min, y_min], [x_max, y_max], 
            size=(render_count, 2)
        )
        
        for p in raw_points:
            z = func(np.array([p]))[0]
            if z > 0: # Only visualize points that contribute to volume
                pt_pos = axes.c2p(p[0], p[1], np.random.uniform(0, z)) # Random height under curve
                particles.add(Dot(point=pt_pos, radius=0.04, color=self.theme.point_color, fill_opacity=0.6))

        # --- ACTION: The Animation Sequence ---
        
        # Phase 1: Grid Entry
        self.play(Create(axes), Write(labels), run_time=1.5)
        
        # Phase 2: Surface Morphing
        self.play(Create(surface), run_time=self.settings.run_time_creation)
        self.wait(0.5)
        
        # Phase 3: HUD Activation (Cyberpunk style entry)
        self.create_hud(result)
        
        # Phase 4: Data Rain (Monte Carlo)
        # Using LaggedStart for a "filling up" effect
        self.play(
            LaggedStartMap(FadeIn, particles, lag_ratio=0.001), 
            run_time=self.settings.run_time_points,
            rate_func=linear
        )
        
        # Phase 5: Cinematic Orbit
        self.logger.info("Entering ambient rotation mode.")
        self.begin_ambient_camera_rotation(rate=self.settings.camera_rotation_speed)
        self.wait(4) # Let it rotate for a while
        self.stop_ambient_camera_rotation()
        
        # Outro
        self.play(FadeOut(Group(axes, surface, particles, labels)))

