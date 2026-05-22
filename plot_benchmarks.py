#############################
# Benchmark Plotting Script #
#############################
import re
import subprocess
import argparse
import platform
import datetime
import os
import matplotlib.pyplot as plt

#####################
# Utility Functions #
#####################
def parse_benchmark_output(text):
    """
    Parse benchmark output and return a dict:
    { 'label': str, 'threads': [int], 'times': [float] }
    """
    lines = text.splitlines()
    label = None
    threads = []
    times = []
    for line in lines:
        m = re.match(r"\s*(\d+) threads: ([\d.]+) seconds", line)
        if m:
            threads.append(int(m.group(1)))
            times.append(float(m.group(2)))
        elif 'GIL is' in line:
            label = line.strip()
    return {'label': label, 'threads': threads, 'times': times}


def plot_benchmarks(benchmarks, sysinfo, script_versions=None):
    """
    Plot the benchmark results using matplotlib. Benchmarks is a list of dicts with keys:
    - 'label': str (e.g. "thread_benchmark.py -X gil=0")
    - 'threads': list of int (e.g. [1, 2, 4, 8])
    - 'times': list of float (e.g. [10.5, 5.2, 3.1, 2.0])
    sysinfo is a dict with system information to display on the plot.
    script_versions is an optional list of strings to include in the system info.
    """
    plt.figure(figsize=(10, 6))
    for bench in benchmarks:
        color = bench.get('color', None)
        plt.plot(bench['threads'], bench['times'], marker='o', label=bench['label'], color=color)
    plt.xlabel('Number of threads')
    plt.ylabel('Time (seconds)')
    plt.title('Threaded Benchmark Results')
    plt.legend()
    plt.grid(True)

    # Compose system info string
    sys_lines = [
        f"System Specs:",
        f"  CPU: {sysinfo.get('CPU_model', sysinfo.get('CPU', 'Unknown'))} ({sysinfo.get('CPU_count', '?')} cores)",
        f"  RAM: {sysinfo.get('RAM_GB', '?')} GB",
        f"  OS: {sysinfo.get('OS', '?')}",
        f"Software Versions:",
        f"  Python: {sysinfo.get('Python', '?')}",
        f"Timestamp: {sysinfo.get('Timestamp', '?')}"
    ]
    if script_versions:
        sys_lines.append(f"Scripts: {', '.join(script_versions)}")
    sysinfo_str = '\n'.join(sys_lines)
    plt.gcf().text(0.01, 0.01, sysinfo_str, fontsize=9, va='bottom', ha='left', family='monospace', bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray'))

    plt.tight_layout(rect=[0, 0.08, 1, 1])
    plt.show()

def get_system_info():
    """
    Gets the system information such as OS, CPU, RAM, and Python version.
    Returns a dictionary with this information.
    """
    info = {}
    info['OS'] = platform.platform()
    info['CPU'] = platform.processor() or platform.machine()
    info['CPU_count'] = os.cpu_count()
    # Try to get RAM info
    try:
        import psutil
        info['RAM_GB'] = round(psutil.virtual_memory().total / (1024**3), 2)
    except ImportError:
        info['RAM_GB'] = 'Unknown (install psutil)'
    # Try to get CPU model (Linux/Mac)
    try:
        if platform.system() == 'Darwin':
            info['CPU_model'] = subprocess.check_output(['sysctl', '-n', 'machdep.cpu.brand_string']).decode().strip()
        elif platform.system() == 'Linux':
            with open('/proc/cpuinfo') as f:
                for line in f:
                    if 'model name' in line:
                        info['CPU_model'] = line.split(':')[1].strip()
                        break
        else:
            info['CPU_model'] = info['CPU']
    except Exception:
        info['CPU_model'] = info['CPU']
    # Python version
    info['Python'] = platform.python_version()
    info['Timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return info

def run_benchmark_script(script_path, python_exe="python", gil_flag=0):
    """
    Runs the given benchmark script with the specified Python executable and GIL flag.
    Returns the standard output of the script.
    """
    try:
        print(f"AB DEBUG: run_benchmark_script() ... Running {script_path} with -X gil={gil_flag}...")
        result = subprocess.run([python_exe, "-X", f"gil={gil_flag}", script_path], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_path}: {e}")
        return ""

def main():
    parser = argparse.ArgumentParser(description="Plot benchmark results from benchmark scripts.")
    parser.add_argument("scripts", nargs="+", help="Benchmark script files to run (e.g. thread_benchmark.py)")
    parser.add_argument("--python", default="python", help="Python executable to use (default: python)")
    args = parser.parse_args()

    sysinfo = get_system_info()
    benchmarks = []
    script_versions = []
    for script in args.scripts:
        for gil_flag, gil_label, color in [
            (0, "GIL DISABLED", "red"),
            (1, "GIL ENABLED", "blue")
        ]:
            print(f"Running {script} with -X gil={gil_flag}...")
            output = run_benchmark_script(script, python_exe=args.python, gil_flag=gil_flag)
            bench = parse_benchmark_output(output)
            if bench['threads']:
                # Patch label to be explicit if not present
                if not bench['label']:
                    bench['label'] = f"{script} ({gil_label})"
                # Attach color for plotting
                bench['color'] = color
                script_versions.append(f"{script} -X gil={gil_flag}")
                benchmarks.append(bench)
            else:
                print(f"No thread timing data found in {script} output for gil={gil_flag}.")

    if not benchmarks:
        print("No benchmark data found in any script output.")
        return
    plot_benchmarks(benchmarks, sysinfo, script_versions)


if __name__ == "__main__":
    main()
