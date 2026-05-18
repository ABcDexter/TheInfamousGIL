import threading
import time
import os
import sys

def cpu_task(n):
    """
    A simple CPU-bound task that performs a large number of calculations.
    """
    total = 0
    for i in range(n):
        total += (i * i) % 97
    return total

def worker(n):
    '''
    Worker function that calls the CPU-bound task.
    '''
    cpu_task(n)

def run(num_threads, n):
    """
    Run the benchmark with the specified number of threads and iterations.
    """
    threads = []
    start = time.perf_counter()

    for _ in range(num_threads):
        t = threading.Thread(target=worker, args=(n,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return time.perf_counter() - start

def main():
    '''Main function to run the benchmark.'''
    n = 30_000_000
    max_threads = min(os.cpu_count() or 1, 8)
    
    print(f"CPU cores: {os.cpu_count()}")
    print(f"Iterations per thread: {n:_}")
    print(f'''GIL is {"ENABLED" if sys._is_gil_enabled() else "DISABLED"} ''')

    for threads in [1, 2, 4, max_threads]:
        elapsed = run(threads, n)
        print(f"{threads:2d} threads: {elapsed:.2f} seconds")

if __name__ == "__main__":
    # call main 
    main()
