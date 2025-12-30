"""
monte_carlo.py - Stochastic Integration Engine
Author: Visionis
Description: High-performance Monte Carlo integration algorithms.
"""

import numpy as np
import logging
from typing import Callable, Optional
from .engine import BaseIntegrator, IntegrationResult, VisiontegralError

logger = logging.getLogger(__name__)

class MonteCarloSolver(BaseIntegrator):
    """
    Standard Monte Carlo Estimator with Batch Processing.
    Suitable for high-dimensional integration (Dims > 3).
    """
    def __init__(self, samples: int = 1_000_000, batch_size: int = 500_000, seed: Optional[int] = None):
        self.samples = samples
        self.batch_size = batch_size
        self.rng = np.random.default_rng(seed)  # Modern numpy random generator

    def integrate(self, func: Callable, bounds: np.ndarray) -> IntegrationResult:
        dim = len(bounds)
        volume_hypercube = np.prod(bounds[:, 1] - bounds[:, 0])
        
        total_sum = 0.0
        total_sq_sum = 0.0
        processed = 0

        # Process in batches to maintain low memory footprint
        while processed < self.samples:
            current_batch = min(self.batch_size, self.samples - processed)
            
            # Generate random points within bounds
            # Formula: min + (max-min) * random[0,1]
            random_raw = self.rng.random((current_batch, dim))
            points = bounds[:, 0] + (bounds[:, 1] - bounds[:, 0]) * random_raw
            
            try:
                values = func(points)
                
                # Validation checks
                if not np.all(np.isfinite(values)):
                     logger.warning("Non-finite values detected in integration stream.")
                     values = np.nan_to_num(values) # Sanitize

                total_sum += np.sum(values)
                total_sq_sum += np.sum(values ** 2)
                
            except Exception as e:
                raise VisiontegralError(f"Function evaluation failed during Monte Carlo: {e}")

            processed += current_batch

        # Final Statistics
        mean = total_sum / self.samples
        variance = (total_sq_sum / self.samples) - (mean ** 2)
        
        # Standard Error of the Mean (SEM)
        std_error = volume_hypercube * np.sqrt(variance / self.samples)
        integral_result = volume_hypercube * mean
        
        return IntegrationResult(
            value=integral_result,
            error_estimate=std_error,
            dimension=dim,
            samples=self.samples
        )

