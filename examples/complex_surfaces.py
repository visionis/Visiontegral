"""
complex_surfaces.py - Cinematic Rendering of Quantum Interference
Author: Visionis
"""

import numpy as np
from core.engine import VisiontegralEngine
from visualization.renderer_3d import ManifoldExplorer

def render_quantum_well():
    # Complex multi-modal function: f(x,y) = cos(x^2+y^2) * exp(-(x^2+y^2)/10)
    def quantum_fn(p):
        r_sq = p[:, 0]**2 + p[:, 1]**2
        return np.cos(r_sq) * np.exp(-r_sq / 10.0)

    bounds = [(-5, 5), (-5, 5)]
    engine = VisiontegralEngine()
    
    print("💎 [Visionis Render] Synthesizing Complex Manifold...")
    result = engine.run(quantum_fn, bounds, samples=500_000)
    
    # Using the Explorer with high-fidelity settings
    explorer = ManifoldExplorer(theme_dark=True)
    explorer.execute_render(
        quantum_fn, 
        bounds, 
        result, 
        resolution=200 # Ultra-high mesh density
    )

if __name__ == "__main__":
    render_quantum_well()

