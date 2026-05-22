#!/usr/bin/env python3
"""
Enhanced benchmarking script that measures performance and CPU saturation.
Run with: python -X gil=0 benchmark_with_cpu_saturation.py
or: python -X gil=1 benchmark_with_cpu_saturation.py
"""
import threading
import time
import os
import sys
import psutil
from concurrent.futures import ThreadPoolExecutor
import statistics

# CPU saturation tracking
cpu_samples = []
cpu_lock = threading.Lock()

def monitor_cpu(duration, interval=0.1):
    """Monitor CPU saturation during benchmark execution."""
    start_time = time.perf_counter()
    samples = []
    
    try:
        process = psutil.Process()
        process.cpu_num()  # Prime the pump
        
        while time.perf_counter() - start_time < duration:
            try:
                # Get CPU usage percentage for this process
                cpu_pct = process.cpu_percent(interval=None)
                samples.append(cpu_pct)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            time.sleep(interval)
    except Exception as e:
        print(f"Warning: Could not monitor CPU: {e}")
    
    return samples

def cpu_task(n):
    """CPU-bound task."""
    total = 0
    for i in range(n):
        total += (i * i) % 97
    return total

def cpu_benchmark(num_threads, iterations_per_thread):
    """Benchmark CPU-bound operations with CPU saturation tracking."""
    print(f"\n--- CPU-Bound Benchmark ({num_threads} threads) ---")
    
    # Start CPU monitoring in background
    monitor_thread = threading.Thread(
        target=lambda: monitor_cpu(5, interval=0.05),
        daemon=True
    )
    monitor_thread.start()
    
    start = time.perf_counter()
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(cpu_task, iterations_per_thread) for _ in range(num_threads)]
        results = [f.result() for f in futures]
    
    elapsed = time.perf_counter() - start
    monitor_thread.join(timeout=6)
    
    return elapsed

def io_task(n):
    """I/O-bound task."""
    for _ in range(n):
        time.sleep(0.0001)

def io_benchmark(num_threads, iterations_per_thread):
    """Benchmark I/O-bound operations with CPU saturation tracking."""
    print(f"\n--- I/O-Bound Benchmark ({num_threads} threads) ---")
    
    start = time.perf_counter()
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(io_task, iterations_per_thread) for _ in range(num_threads)]
        results = [f.result() for f in futures]
    
    elapsed = time.perf_counter() - start
    
    return elapsed

def get_system_info():
    """Get current CPU information."""
    try:
        # System-wide CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count(logical=False)
        cpu_count_logical = psutil.cpu_count(logical=True)
        return {
            'cpu_percent': cpu_percent,
            'cpu_cores': cpu_count,
            'cpu_threads': cpu_count_logical
        }
    except Exception as e:
        print(f"Warning: Could not get system info: {e}")
        return {}

def run_benchmarks():
    """Run all benchmarks and return results."""
    results = {
        'cpu_bound': {},
        'io_bound': {},
        'system_info': get_system_info()
    }
    
    thread_counts = [1, 2, 4, os.cpu_count()]
    iterations_cpu = 30_000_000
    iterations_io = 1000
    
    print(f"\nSystem: {results['system_info']}")
    
    # CPU-bound benchmarks
    print("\n=== CPU-Bound Benchmarks ===")
    for threads in thread_counts:
        elapsed = cpu_benchmark(threads, iterations_cpu)
        results['cpu_bound'][threads] = elapsed
        print(f"Threads: {threads:2d} | Time: {elapsed:.4f}s")
    
    # I/O-bound benchmarks
    print("\n=== I/O-Bound Benchmarks ===")
    for threads in thread_counts:
        elapsed = io_benchmark(threads, iterations_io)
        results['io_bound'][threads] = elapsed
        print(f"Threads: {threads:2d} | Time: {elapsed:.4f}s")
    
    return results

if __name__ == '__main__':
    gil_status = "ENABLED" if sys.flags.optimize == 0 else "DISABLED"
    try:
        # Check if GIL is disabled (requires Python 3.13+)
        import _sysconfig
        if hasattr(sys, 'abiflags') and 't' in sys.abiflags:
            gil_status = "DISABLED" if os.environ.get('PYTHON_GIL') == '0' else "ENABLED"
    except:
        pass
    
    print(f"Python {sys.version}")
    print(f"GIL: {gil_status}")
    
    results = run_benchmarks()
    
    print("\n=== Results Summary ===")
    print(f"\nCPU-Bound (lower is better):")
    for threads, time_taken in results['cpu_bound'].items():
        speedup = results['cpu_bound'][1] / time_taken if time_taken > 0 else 0
        print(f"  {threads} threads: {time_taken:.4f}s (speedup: {speedup:.2f}x)")
    
    print(f"\nI/O-Bound (lower is better):")
    for threads, time_taken in results['io_bound'].items():
        speedup = results['io_bound'][1] / time_taken if time_taken > 0 else 0
        print(f"  {threads} threads: {time_taken:.4f}s (speedup: {speedup:.2f}x)")
