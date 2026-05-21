import argparse
import threading
import time
import os
import sys
import argparse

def is_prime(n):
    """
    Basic primality test using trial division. (Deterministic but not optimized for large numbers.)
    """
    if n in (2, 3):
        return True
    if (n < 2) or (n % 2 == 0):
        return False

    #limit = n//20_000+1 #
    limit =  int(n**0.5) + 1
    for divisor in range(3, limit, 2):
        if n % divisor == 0:
            return False

    return True


def search_primes_single_thread(numbers):
    '''
    Search primes in a single thread.
    '''
    return [n for n in numbers if is_prime(n)]


def check_prime_subset(numbers, results):
    '''
    Worker that checks a subset of numbers for primality.
    '''
    for number in numbers:
        if is_prime(number):
            results.append(number)


def run_prime_threads(num_threads, numbers):
    '''
    Run a multi-threaded prime search using the given number of threads.
    '''
    results = []
    threads = []
    chunks = [numbers[i::num_threads] for i in range(num_threads)]
    
    for chunk in chunks:
        t = threading.Thread(target=check_prime_subset, args=(chunk, results))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return results


def main():
    '''Main function to run the primality benchmark.'''
    # parse the arg for the upper limit of numbers to check for primality
    N = argparse.ArgumentParser(description="Benchmark for prime number search with threading.")
    N.add_argument('--N', type=int, default=10**6, help='Maximum number to check for primality (default: 1,000,000)')
    args = N.parse_args()
    numbers = [2] + [n for n in range(3, args.N, 2)]  # Odd numbers in the range
    max_threads = min(os.cpu_count() or 1, 8)

    print(f"CPU cores: {os.cpu_count()}")
    print(f"Numbers to test: {len(numbers):_}")
    print(f"GIL is {'ENABLED' if sys._is_gil_enabled() else 'DISABLED'}")

    start = time.perf_counter()
    single_results = search_primes_single_thread(numbers)
    single_elapsed = time.perf_counter() - start
    print(f"Single-threaded: {single_elapsed:.3f} seconds. Found {len(single_results)} primes.")

    print("\nMulti-threaded benchmark")
    for threads in [1, 2, 4, max_threads]:
        start = time.perf_counter()
        threaded_results = run_prime_threads(threads, numbers)
        elapsed = time.perf_counter() - start
        print(f"{threads:2d} threads: {elapsed:.3f} seconds. Found {len(threaded_results)} primes.")


def profile_main():
    '''
    Profile the benchmark run to inspect the time spent in prime checking.
    '''
    start = time.perf_counter()
    main()
    print(f"Total benchmark time: {time.perf_counter() - start:.3f} seconds")


if __name__ == "__main__":
    main()
