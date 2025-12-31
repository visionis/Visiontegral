"""
4d_hypervolume.py - High-Dimensional Convergence Benchmark
Author: Visionis
Standard: Industrial HPC
"""

import numpy as np
import time
from core.engine import VisiontegralEngine
from core.manifolds import HyperSphere

class HypersphereBenchmark:
    """Rigorous validation of the Visiontegral engine in 4D space."""
    
    @staticmethod
    def execute():
        engine = VisiontegralEngine()
        radius = 1.0
        dim = 4
        
        # Analytical solution: (pi^2 * r^4) / 2
        theoretical_value = (np.pi**2 * radius**4) / 2
        
        # Indicator function: 1 if inside hypersphere, 0 otherwise
        sphere = HyperSphere(dimension=dim, radius=radius)
        def target_fn(p): return sphere.contains(p).astype(float)

        bounds = [(-1.1, 1.1)] * dim # Tight bounding box for efficiency
        
        print(f"🚀 [Visionis Benchmark] Starting 4D Integration...")
        start = time.perf_counter()
        
        # Running with 10M samples for extreme precision
        result = engine.run(target_fn, bounds, samples=10_000_000)
        
        duration = time.perf_counter() - start
        error = abs(result.value - theoretical_value)
        
        print(f"\n--- RESULTS ---")
        print(f"Theoretical: {theoretical_value:.8f}")
        print(f"Calculated:  {result.value:.8f}")
        print(f"Abs Error:   {error:.2e}")
        print(f"Execution:   {duration:.2f}s")
        print(f"Performance: {10/duration:.2f}M samples/sec")

if __name__ == "__main__":
    HypersphereBenchmark.execute()

