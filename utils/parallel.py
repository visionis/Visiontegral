"""
parallel.py - Hardware-Aware Computation Manager
Author: Visionis
Description: Multi-core distribution for intensive integration tasks.
"""

import concurrent.futures
import numpy as np
from typing import Callable, List, Tuple

class ParallelCompute:
    """Manages high-throughput parallel execution for Monte Carlo sampling."""

    @staticmethod
    def distribute_task(task: Callable, 
                        args_list: List[Tuple], 
                        max_workers: int = None) -> List[Any]:
        """
        Executes tasks across multiple CPU cores using ProcessPoolExecutor.
        Avoids GIL (Global Interpreter Lock) for heavy math operations.
        """
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(task, *args) for args in args_list]
            return [f.result() for f in concurrent.futures.as_completed(futures)]

    @staticmethod
    def chunk_samples(total_samples: int, cpu_count: int) -> List[int]:
        """Calculates optimal sample chunks for balanced load distribution."""
        return [total_samples // cpu_count] * cpu_count

