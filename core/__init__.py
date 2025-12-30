"""
Visiontegral Core Module
------------------------
High-performance multidimensional integration library.

Author: Visionis
Version: 1.0.0-alpha
License: MIT
"""

# Importing main components for easy access
from .engine import VisiontegralEngine, IntegrationResult, VisiontegralError
from .manifolds import HyperSphere, HyperRectangle, BaseManifold
from .monte_carlo import MonteCarloSolver
from .quadratures import AdaptiveQuadratureSolver

# Defining what gets exported when someone does 'from core import *'
__all__ = [
    "VisiontegralEngine",
    "IntegrationResult",
    "VisiontegralError",
    "MonteCarloSolver",
    "AdaptiveQuadratureSolver",
    "HyperSphere",
    "HyperRectangle",
    "BaseManifold"
]

