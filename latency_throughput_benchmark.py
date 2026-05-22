import threading
import time
import os
import sys
from statistics import mean, stdev


def cpu_task(n):
    """CPU-bound task for benchmarking."""
    total = 0
    for i in range(n):
        total += (i * i) % 97
    return total


def worker(n):
    """Worker function that calls the CPU-bound task."""
    cpu_task(n)


def measure_latency(num_threads, n, iterations=3):
    """
    Measure latency (time per operation) across multiple runs.
    Returns: list of elapsed times
    """
    latencies = []
    for _ in range(iterations):
        threads = []
        start = time.perf_counter()

        for _ in range(num_threads):
            t = threading.Thread(target=worker, args=(n,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        elapsed = time.perf_counter() - start
        latencies.append(elapsed)
    
    return latencies


def measure_throughput(num_threads, n, duration=5):
    """
    Measure throughput (operations per second).
    Runs operations continuously for `duration` seconds and counts them.
    Returns: operations per second
    """
    operations = 0
    start = time.perf_counter()
    
    while time.perf_counter() - start < duration:
        threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=worker, args=(n,))
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()
        
        operations += 1
    
    elapsed = time.perf_counter() - start
    throughput = operations / elapsed
    return throughput


def print_results(thread_counts, latencies_dict, throughput_dict):
    """Pretty print latency and throughput results."""
    print(f"\n{'='*80}")
    print("LATENCY vs THROUGHPUT ANALYSIS")
    print(f"{'='*80}\n")
    
    print(f"{'Threads':<10} {'Avg Latency (s)':<20} {'Stdev (s)':<15} {'Throughput (ops/s)':<20}")
    print(f"{'-'*80}")
    
    for threads in thread_counts:
        latencies = latencies_dict[threads]
        avg_latency = mean(latencies)
        stdev_latency = stdev(latencies) if len(latencies) > 1 else 0
        throughput = throughput_dict[threads]
        
        print(f"{threads:<10} {avg_latency:<20.4f} {stdev_latency:<15.4f} {throughput:<20.2f}")
    
    print(f"{'-'*80}\n")


def main():
    """Main benchmark entry point."""
    n = 30_000_000
    max_threads = min(os.cpu_count() or 1, 8)
    thread_counts = [1, 2, 4, max_threads]
    
    print(f"CPU cores: {os.cpu_count()}")
    print(f"Iterations per thread: {n:_}")
    print(f"GIL is {'ENABLED' if sys._is_gil_enabled() else 'DISABLED'}")
    print(f"\nWarmup run...")
    
    # Warmup
    worker(n)
    
    print(f"Measuring latency (3 iterations per thread count)...")
    latencies_dict = {}
    for threads in thread_counts:
        print(f"  {threads} threads...", end="", flush=True)
        latencies_dict[threads] = measure_latency(threads, n, iterations=3)
        print(" done")
    
    print(f"\nMeasuring throughput (5 seconds per thread count)...")
    throughput_dict = {}
    for threads in thread_counts:
        print(f"  {threads} threads...", end="", flush=True)
        throughput_dict[threads] = measure_throughput(threads, n, duration=5)
        print(" done")
    
    # Print results
    print_results(thread_counts, latencies_dict, throughput_dict)
    
    # Analysis
    print(f"{'='*80}")
    print("ANALYSIS")
    print(f"{'='*80}")
    print("\nLatency (lower is better):")
    print("  - Measures how long each batch of operations takes")
    print("  - Lower latency = faster response time per operation")
    
    baseline_latency = mean(latencies_dict[1])
    for threads in thread_counts[1:]:
        avg_latency = mean(latencies_dict[threads])
        speedup = baseline_latency / avg_latency
        print(f"  - {threads} threads: {speedup:.2f}x speedup vs 1 thread")
    
    print(f"\nThroughput (higher is better):")
    print("  - Measures how many operations per second")
    print("  - Higher throughput = more work done per unit time")
    
    baseline_throughput = throughput_dict[1]
    for threads in thread_counts[1:]:
        throughput = throughput_dict[threads]
        speedup = throughput / baseline_throughput
        print(f"  - {threads} threads: {speedup:.2f}x speedup vs 1 thread")
    
    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    main()
