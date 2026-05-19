import threading
import time
import os
import sys


def is_prime(n):
    """
    Basic primality test using trial division.
    """
    if n in (2, 3):
        return True
    if (n < 2) or (n % 2 == 0):
        return False

    limit = int(n**0.5) + 1
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
    numbers = [
        100000000003, 100000000019, 100000000033, 100000000087, 100000000093, 100000000117, 100000000123, 100000000181, 100000000207, 100000000223, 100000000249, 100000000253, 100000000279, 100000000309, 100000000333, 100000000339,
        100000000363, 100000000381, 100000000399, 100000000409, 100000000427, 100000000451, 100000000477, 100000000491, 100000000507, 100000000513, 100000000543, 100000000553, 100000000577, 100000000623, 100000000633, 100000000681,
        100000000693, 100000000699, 100000000707, 100000000727, 100000000733, 100000000793, 100000000801, 100000000813, 100000000819, 100000000833, 100000000843, 100000000867, 100000000893, 100000000909, 100000000927, 100000000941,
        100000000963, 100000000979, 100000000993, 100000001007, 100000001019, 100000001033, 100000001049, 100000001067, 100000001081, 100000001103, 100000001117, 100000001129, 100000001141, 100000001153, 100000001163, 100000001179, 100000001193, 100000001207, 100000001219, 100000001233, 100000001241, 100000001259, 100000001273, 100000001291, 100000001303, 100000001319, 100000001333, 100000001349, 100000001361, 100000001373, 100000001387, 100000001399, 100000001413, 100000001427, 100000001439, 100000001451,
        100000001463, 100000001483, 100000001499, 100000001513, 100000001523, 100000001539, 100000001551, 100000001569, 100000001583, 100000001599, 100000001611, 100000001627, 100000001639, 100000001653, 100000001667, 100000001679,
        100000001693, 100000001709, 100000001721, 100000001733, 100000001747, 100000001759, 100000001773, 100000001787, 100000001799, 100000001811, 100000001827, 100000001839, 100000001853, 100000001867, 100000001879, 100000001891, 100000001909, 100000001923, 100000001937, 100000001953, 100000001967, 100000001979, 100000001993, 100000002007, 100000002019, 100000002033, 100000002049, 100000002061,100000002073, 100000002087
    ]
    max_threads = min(os.cpu_count() or 1, 8)

    print(f"CPU cores: {os.cpu_count()}")
    print(f"Numbers to test: {len(numbers)}")
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
