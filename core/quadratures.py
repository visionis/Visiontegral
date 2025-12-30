"""
quadratures.py - Deterministic Integration Methods
Author: Visionis
Description: Wrappers for Gaussian Quadrature and adaptive integration.
"""

import numpy as np
import time
from scipy import integrate
from typing import Callable
from .engine import BaseIntegrator, IntegrationResult, VisiontegralError

class AdaptiveQuadratureSolver(BaseIntegrator):
    """
    Uses Scipy's 'nquad' (Adaptive Gaussian Quadrature).
    Best for low dimensions (D < 5) and high precision requirements.
    """
    
    def __init__(self, limit: int = 50, epsabs: float = 1.49e-8):
        self.limit = limit    # Recursion depth limit
        self.epsabs = epsabs  # Absolute error tolerance

    def integrate(self, func: Callable, bounds: np.ndarray) -> IntegrationResult:
        dim = len(bounds)
        
        # Scipy nquad expects bounds as a list of lists [[min, max], ...]
        scipy_bounds = bounds.tolist()
        
        # Wrapper to make the user function compatible with nquad's argument unpacking
        def func_wrapper(*args):
            # nquad passes arguments as x0, x1, x2... we need a vector
            return func(np.array([args]))[0]

        start_t = time.perf_counter()
        
        try:
            val, error = integrate.nquad(
                func_wrapper, 
                scipy_bounds, 
                opts={'limit': self.limit, 'epsabs': self.epsabs}
            )
        except Exception as e:
            raise VisiontegralError(f"Quadrature integration failed: {str(e)}")
            
        exec_time = time.perf_counter() - start_t

        return IntegrationResult(
            value=val,
            error_estimate=error,
            dimension=dim,
            samples=0, # Quadrature implies functional evaluations, not random samples
            execution_time=exec_time
        )

