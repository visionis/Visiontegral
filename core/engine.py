"""
engine.py - The Central Nervous System of Visiontegral
Author: Visionis
Description: Orchestrates different solvers and manages the integration pipeline.
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, List, Tuple, Optional, Dict, Type

# --- Core Data Structures ---

@dataclass(frozen=True)
class IntegrationResult:
    """Immutable container for finalized integration data."""
    value: float
    error_estimate: float
    dimension: int
    samples: int
    execution_time: float = 0.0

    def __repr__(self) -> str:
        return f"<VisiontegralResult: {self.value:.6f} ± {self.error_estimate:.6e}>"

class VisiontegralError(Exception):
    """Custom exception for library-wide errors."""
    pass

# --- Abstract Base Interface ---

class BaseIntegrator(ABC):
    """Protocol for all integration algorithms (Monte Carlo, Quadrature, etc.)"""
    @abstractmethod
    def integrate(self, func: Callable, bounds: np.ndarray, **kwargs) -> IntegrationResult:
        pass

# --- The Main Engine ---

class VisiontegralEngine:
    """
    The High-Level API. Users interact only with this class.
    It delegates tasks to specialized solvers in monte_carlo.py or quadratures.py.
    """
    def __init__(self):
        # We store references to our specialized solvers
        from .monte_carlo import MonteCarloSolver
        from .quadratures import AdaptiveQuadratureSolver
        
        self._solvers: Dict[str, BaseIntegrator] = {
            "monte_carlo": MonteCarloSolver(),
            "quadrature": AdaptiveQuadratureSolver()
        }
        self.logger = logging.getLogger("VisiontegralEngine")

    def run(self, 
            func: Callable, 
            bounds: List[Tuple[float, float]], 
            method: str = "monte_carlo", 
            **kwargs) -> IntegrationResult:
        """
        Validates inputs and executes the requested integration method.
        """
        # 1. Validation
        if not callable(func):
            raise VisiontegralError("Provided function is not callable.")
        
        bounds_arr = np.array(bounds, dtype=np.float64)
        if bounds_arr.ndim != 2 or bounds_arr.shape[1] != 2:
            raise VisiontegralError("Bounds must be a list of (min, max) tuples.")

        # 2. Solver Selection
        solver = self._solvers.get(method.lower())
        if not solver:
            raise VisiontegralError(f"Method '{method}' is not implemented. Available: {list(self._solvers.keys())}")

        # 3. Execution & Performance Tracking
        self.logger.info(f"Execution started using {method} for {len(bounds)}D space.")
        
        start_t = time.perf_counter()
        result = solver.integrate(func, bounds_arr, **kwargs)
        elapsed = time.perf_counter() - start_t
        
        # Inject execution time into the immutable result via object.__setattr__
        object.__setattr__(result, 'execution_time', elapsed)
        
        return result
