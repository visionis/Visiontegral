"""
color_maps.py - Advanced Chromatic Orchestrator
Author: Visionis
Description: Scientific-grade color mapping with hardware-accelerated normalization.
"""

from typing import Final, List, Tuple
import numpy as np
from matplotlib import colormaps
from matplotlib.colors import LinearSegmentedColormap, Normalize

class PaletteVault:
    """Immutable store for high-end cinematic palettes."""
    NEON_QUANTUM: Final[List[str]] = ["#00F2FE", "#4FACFE", "#7367F0", "#CE9FFC"]
    DARK_MATTER: Final[List[str]] = ["#121212", "#1E1E2F", "#BB86FC", "#03DAC6"]

class VisionColorMapper:
    """Handles high-dimensional data normalization and color assignment."""
    
    def __init__(self, palette_name: str = "magma"):
        self.cmap = colormaps.get_cmap(palette_name)

    def generate_rgba(self, data: np.ndarray) -> np.ndarray:
        """
        Maps n-dimensional data to RGBA space with vectorized normalization.
        :param data: Input scalar values to map.
        :return: (N, 4) RGBA array.
        """
        if data.size == 0:
            return np.array([])
            
        # Min-Max Normalization with stability epsilon
        min_val, max_val = np.min(data), np.max(data)
        norm = Normalize(vmin=min_val, vmax=max_val + 1e-12)
        return self.cmap(norm(data))

    @staticmethod
    def create_interpolated_gradient(colors: List[str], resolution: int = 256) -> LinearSegmentedColormap:
        """Generates a custom high-resolution gradient for manifold surfaces."""
        return LinearSegmentedColormap.from_list("VisionisGradient", colors, N=resolution)

