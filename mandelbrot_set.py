import concurrent.futures
import time
import os
import sys

try:
    import numpy as np
    import matplotlib.pyplot as plt
    HAS_PLOTTING = True
except ImportError:
	HAS_PLOTTING = False


def mandelbrot(x, y, max_iterations):
	"""
	Compute Mandelbrot iteration count for a single point.
	"""
	z = 0 + 0j
	c = complex(x, y)
	for iteration in range(max_iterations):
		if abs(z) >= 2:
			return iteration
		z = z * z + c
	return max_iterations


def build_domain(xcenter, ycenter, bound, ncols, nrows):
	x_values = [xcenter - bound + i * (2 * bound) / (ncols - 1) for i in range(ncols)]
	y_values = [ycenter - bound + j * (2 * bound) / (nrows - 1) for j in range(nrows)]
	return x_values, y_values


def compute_rows(row_indices, x_values, y_values, max_iterations):
	rows = []
	for j in row_indices:
		y = y_values[j]
		row = [mandelbrot(x, y, max_iterations) for x in x_values]
		rows.append((j, row))
	return rows


def run_serial(x_values, y_values, max_iterations):
	'''Run the Mandelbrot benchmark in a single thread.'''
	iteration_array = [[0] * len(x_values) for _ in range(len(y_values))]
	for j, y in enumerate(y_values):
		iteration_array[j] = [mandelbrot(x, y, max_iterations) for x in x_values]
	return iteration_array


def run_threads(num_workers, x_values, y_values, max_iterations, chunk_size=8):
	'''Run the Mandelbrot benchmark with a thread pool.'''
	nrows = len(y_values)
	iteration_array = [[0] * len(x_values) for _ in range(nrows)]
	row_groups = [list(range(i, nrows, num_workers)) for i in range(num_workers)]

	with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
		futures = [executor.submit(compute_rows, group, x_values, y_values, max_iterations)
				   for group in row_groups if group]
		for future in concurrent.futures.as_completed(futures):
			for j, row in future.result():
				iteration_array[j] = row

	return iteration_array


def plot_mandelbrot(iteration_array, x_values, y_values, cmap="nipy_spectral"):
    """
    Render the Mandelbrot set using Matplotlib.
    """
    if not HAS_PLOTTING:
        print("Matplotlib or NumPy not installed. Skipping plot.")
        return

    iteration_np = np.array(iteration_array)
    fig, ax = plt.subplots(figsize=(8, 8))
    extent = [x_values[0], x_values[-1], y_values[0], y_values[-1]]
    img = ax.imshow(iteration_np, cmap=cmap, extent=extent, origin="lower", aspect="auto")
    ax.set_xlabel("Real axis")
    ax.set_ylabel("Imaginary axis")
    ax.set_title("Mandelbrot set")
    fig.colorbar(img, ax=ax, label="Escape time")
    plt.tight_layout()
    plt.show()


def time_function(func, *args, **kwargs):
    '''
    Time the execution of a function with the given arguments.
    '''
    start = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = time.perf_counter() - start
    return result, elapsed


def main():
	'''Main benchmark entry point.'''
	nrows = 600
	ncols = 600
	xcenter = -0.4601222
	ycenter = 0.570286
	bound = 0.002
	max_iterations = 1000

	x_values, y_values = build_domain(xcenter, ycenter, bound, ncols, nrows)
	max_threads = min(os.cpu_count() or 1, 8)

	print(f"CPU cores: {os.cpu_count()}")
	print(f"Grid: {nrows}x{ncols}, iterations: {max_iterations}")
	print(f"GIL is {'ENABLED' if sys._is_gil_enabled() else 'DISABLED'}")

	serial_array, serial_time = time_function(run_serial, x_values, y_values, max_iterations)
	print(f"Serial run: {serial_time:.3f} seconds")

	print("\nThreaded benchmark")
	for workers in [1, 2, 4, max_threads]:
		_, elapsed = time_function(run_threads, workers, x_values, y_values, max_iterations)
		print(f"{workers:2d} threads: {elapsed:.3f} seconds")

	print("\nRendering Mandelbrot set...")
	plot_mandelbrot(serial_array, x_values, y_values)


if __name__ == "__main__":
	main()
