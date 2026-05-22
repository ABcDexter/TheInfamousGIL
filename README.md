# TheInfamousGIL

## About
This repository demonstrates the infamous Python GIL (Global Interpreter Lock), its impact on threading, and the new GIL-free Python (3.13+). It includes benchmarks, visualizations, and reference counting demos.

## Benchmarks & Demos
- `thread_benchmark.py`: CPU and I/O-bound threading benchmarks, with and without the GIL.
- `prime_benchmark.py`: Multi-threaded prime search benchmark.
- `mandelbrot_set.py`: Mandelbrot set computation and visualization, with threading.
- `plot_benchmarks.py`: Runs benchmarks with both `-X gil=0` and `-X gil=1` and plots comparative results, including system info.
- `breaking_thread.py`: Shows how threading can break atomicity and reference counting without the GIL.
- `reference_counting.py`: Demonstrates Python reference counting, memory addresses, and `sys.getrefcount`/`ctypes` tricks.
- `basic_thread.py`: Simple thread creation and joining example.

## How to Install Python 3.14 (or 3.13+) with GIL-Free Support

### Using `uv` (Recommended for Linux/macOS)
1. Install [uv](https://github.com/astral-sh/uv):
	```sh
	curl -Ls https://astral.sh/uv/install.sh | sh
	# or see https://github.com/astral-sh/uv for other install methods
	```
2. Install GIL-free Python:
	```sh
	uv py --install 3.14t-dev
	# or latest available tagged as `-t-dev` (free-threaded dev build)
	```
3. Run with:
	```sh
	uv py -X gil=0 script.py
	```

### Using `pyenv`
1. Install [pyenv](https://github.com/pyenv/pyenv):
	```sh
	curl https://pyenv.run | bash
	# Follow the instructions to add pyenv to your PATH and shell
	```
2. Install GIL-free Python (if available):
	```sh
	pyenv install 3.14t-dev
	# or the latest available free-threaded dev build
	pyenv global 3.14t-dev
	```
3. Run with:
	```sh
	python -X gil=0 script.py
	```

> **Note:** Not all pyenv builds may have the `-t-dev` (free-threaded dev) variant. Check with `pyenv install --list | grep t-dev$` or see [pyenv docs](https://github.com/pyenv/pyenv).

## Usage
1. Install dependencies:
	```sh
	pip install matplotlib psutil
	```
2. Run a benchmark and plot results:
	```sh
	python plot_benchmarks.py thread_benchmark.py
	python plot_benchmarks.py prime_benchmark.py
	python plot_benchmarks.py mandelbrot_set.py
	```
	This will run each script with both GIL enabled and disabled, and show a comparative plot.

3. Try the reference counting and breaking-thread demos:
	```sh
	python reference_counting.py
	python -X gil=0 breaking_thread.py
	```

## What You'll See
- How the GIL affects CPU-bound and I/O-bound threading
- How reference counting works in CPython
- How GIL-free Python changes threading behavior
- System info and Python version on every plot

---
For more, see the code and comments in each script!
