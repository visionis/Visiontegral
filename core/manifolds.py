"""
manifolds.py - Geometric Definitions for Visiontegral
Author: Visionis
Description: Defines n-dimensional geometric manifolds and boundaries.
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Optional, Tuple
from dataclasses import dataclass

@dataclass
class ManifoldStats:
    """Container for analytical properties of the manifold (if known)."""
    exact_volume: Optional[float] = None
    center_mass: Optional[np.ndarray] = None

class BaseManifold(ABC):
    """
    Abstract Base Class for all geometric shapes in N-dimensions.
    """
    def __init__(self, dimension: int):
        self.dimension = dimension

    @abstractmethod
    def contains(self, points: np.ndarray) -> np.ndarray:
        """
        Vectorized check if points define the interior of the manifold.
        :param points: (N, D) array of points.
        :return: (N,) boolean array.
        """
        pass

    @property
    def stats(self) -> ManifoldStats:
        """Returns analytical statistics for validation purposes."""
        return ManifoldStats()

class HyperRectangle(BaseManifold):
    """Represents an N-dimensional box (orthotope)."""
    def __init__(self, bounds: np.ndarray):
        """
        :param bounds: (D, 2) array where [[min, max], ...]
        """
        super().__init__(dimension=len(bounds))
        self.bounds = np.array(bounds, dtype=np.float64)

    def contains(self, points: np.ndarray) -> np.ndarray:
        # Check if points are within [min, max] for all dimensions
        # Logic: (p >= min) & (p <= max) for all columns
        in_bounds = np.all((points >= self.bounds[:, 0]) & (points <= self.bounds[:, 1]), axis=1)
        return in_bounds

    @property
    def stats(self) -> ManifoldStats:
        volume = np.prod(self.bounds[:, 1] - self.bounds[:, 0])
        return ManifoldStats(exact_volume=volume)

class HyperSphere(BaseManifold):
    """Represents an N-dimensional ball."""
    def __init__(self, dimension: int, radius: float = 1.0, center: Optional[np.ndarray] = None):
        super().__init__(dimension)
        self.radius = radius
        self.center = center if center is not None else np.zeros(dimension)
        
        if len(self.center) != dimension:
            raise ValueError(f"Center dimension {len(self.center)} does not match manifold dimension {dimension}.")

    def contains(self, points: np.ndarray) -> np.ndarray:
        # Efficient Euclidean distance calculation
        # formula: sum((x_i - c_i)^2) <= r^2
        sq_dist = np.sum((points - self.center) ** 2, axis=1)
        return sq_dist <= (self.radius ** 2)

    @property
    def stats(self) -> ManifoldStats:
        """Calculates exact volume using Gamma function for validation."""
        from scipy.special import gamma
        n = self.dimension
        r = self.radius
        vol = (np.pi ** (n / 2)) / gamma(n / 2 + 1) * (r ** n)
        return ManifoldStats(exact_volume=vol)

