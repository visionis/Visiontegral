import numpy as np
import logging
import functools
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, List, Tuple, Optional, Protocol

# --- Configuration & Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(module)s | %(message)s')
logger = logging.getLogger("VisiontegralCore")

class VisiontegralError(Exception):
    """Base exception for domain-specific errors."""
    pass

# --- Protocols & Interfaces ---
class ProgressCallback(Protocol):
    """Interface for reporting progress to UI/CLI."""
    def __call__(self, progress: float, message: str) -> None: ...

# --- Decorators for Clean Code ---
def measure_performance(func):
    """Decorator to automatically track execution time."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start_time
            # Inject execution time into the result object if it supports it
            if hasattr(result, 'execution_time'):
                object.__setattr__(result, 'execution_time', elapsed)
            logger.info(f"Execution finished in {elapsed:.4f}s")
            return result
        except Exception as e:
            logger.error(f"Execution failed in {func.__name__}: {e}")
            raise e
    return wrapper

# --- Data Structures (Immutable) ---
@dataclass(frozen=True)
class IntegrationResult:
    """
    Thread-safe, immutable container for integration results.
    Frozen=True ensures data integrity after calculation.
    """
    value: float
    error_estimate: float
    dimension: int
    samples: int
    execution_time: float = field(default=0.0) # Set by decorator via bypass

    def __repr__(self) -> str:
        return (f"Visiontegral Result\n"
                f"-------------------\n"
                f"Value     : {self.value:.8f}\n"
                f"Error (±) : {self.error_estimate:.8e}\n"
                f"Dimension : {self.dimension}D\n"
                f"Samples   : {self.samples:,}\n"
                f"Time      : {self.execution_time:.4f}s")

# --- Logic Layer ---
class BaseIntegrator(ABC):
    @abstractmethod
    def integrate(self, func: Callable, bounds: np.ndarray, callback: Optional[ProgressCallback] = None) -> IntegrationResult:
        pass

class MonteCarloIntegrator(BaseIntegrator):
    def __init__(self, samples: int = 1_000_000, batch_size: int = 100_000):
        if samples <= 0: raise VisiontegralError("Samples must be positive.")
        self.samples = samples
        self.batch_size = batch_size

    @measure_performance
    def integrate(self, func: Callable, bounds: np.ndarray, callback: Optional[ProgressCallback] = None) -> IntegrationResult:
        dim = len(bounds)
        volume = np.prod(bounds[:, 1] - bounds[:, 0])
        
        running_sum = 0.0
        running_sq_sum = 0.0
        
        # Batch processing for memory efficiency and progress tracking
        processed_samples = 0
        while processed_samples < self.samples:
            current_batch = min(self.batch_size, self.samples - processed_samples)
            
            # Vectorized generation for the batch
            points = np.random.uniform(bounds[:, 0], bounds[:, 1], size=(current_batch, dim))
            values = func(points)
            
            # Mathematical Safety Check
            if not np.all(np.isfinite(values)):
                 raise VisiontegralError("Non-finite values (NaN/Inf) detected in function output.")

            # Accumulate statistics
            running_sum += np.sum(values)
            running_sq_sum += np.sum(values ** 2)
            
            processed_samples += current_batch
            
            # Update Progress
            if callback:
                progress_pct = processed_samples / self.samples
                callback(progress_pct, f"Processed {processed_samples:,} samples")

        # Final Calculation
        mean = running_sum / self.samples
        variance = (running_sq_sum / self.samples) - (mean ** 2)
        std_error = volume * np.sqrt(variance / self.samples)
        integral_val = volume * mean

        return IntegrationResult(integral_val, std_error, dim, self.samples)

class VisiontegralEngine:
    """Facade for the Visiontegral library."""
    
    def __init__(self):
        self._solvers = {
            "monte_carlo": MonteCarloIntegrator
        }

    def run(self, func: Callable, bounds: List[Tuple[float, float]], method: str = "monte_carlo", **kwargs) -> IntegrationResult:
        """
        Entry point for calculations.
        :param kwargs: Additional arguments for the solver (e.g., samples, callback)
        """
        bounds_arr = np.array(bounds, dtype=np.float64)
        
        # Check dimensionality
        if bounds_arr.ndim != 2 or bounds_arr.shape[1] != 2:
            raise VisiontegralError("Bounds must be a list of (min, max) tuples.")

        solver_cls = self._solvers.get(method)
        if not solver_cls:
            raise VisiontegralError(f"Method '{method}' unavailable.")

        # Instantiate solver with potential kwargs configuration
        solver_instance = solver_cls(samples=kwargs.get('samples', 1_000_000))
        
        logger.info(f"Engine spinning up: {method.upper()} | {len(bounds)} Dimensions")
        return solver_instance.integrate(func, bounds_arr, callback=kwargs.get('callback'))

