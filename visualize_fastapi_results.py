###########
# Imports #
###########
import re
import platform
import datetime
import os
import subprocess
import matplotlib.pyplot as plt

##############################
# Parse wrk Benchmark Output #
##############################

def parse_wrk_output(text):
    """
    Parse wrk benchmark output.

    Returns:
    {
        "tests": [...],
        "requests_per_sec": [...],
        "latency_ms": [...],
        "timeouts": [...]
    }
    """

    sections = re.split(r"=+\n", text)

    tests = []
    requests_per_sec = []
    latency_ms = []
    timeouts = []

    current_test = None

    for section in sections:

        # -----------------------------------------
        # Detect benchmark section name
        # -----------------------------------------
        title_match = re.search(
            r"(CPU Sequential|CPU Threaded|IO Bound|Mixed)",
            section
        )

        if title_match:
            current_test = title_match.group(1)

        # -----------------------------------------
        # Parse Requests/sec
        # -----------------------------------------
        rps_match = re.search(
            r"Requests/sec:\s+([\d.]+)",
            section
        )

        # -----------------------------------------
        # Parse latency
        # -----------------------------------------
        latency_match = re.search(
            r"Latency\s+([\d.]+)(ms|s|us)",
            section
        )

        # -----------------------------------------
        # Parse timeouts
        # -----------------------------------------
        timeout_match = re.search(
            r"timeout\s+(\d+)",
            section
        )

        if current_test and rps_match:

            tests.append(current_test)

            # Requests/sec
            requests_per_sec.append(
                float(rps_match.group(1))
            )

            # Latency conversion -> ms
            latency_value = 0.0

            if latency_match:

                value = float(latency_match.group(1))
                unit = latency_match.group(2)

                if unit == "s":
                    latency_value = value * 1000

                elif unit == "ms":
                    latency_value = value

                elif unit == "us":
                    latency_value = value / 1000

            latency_ms.append(latency_value)

            # Timeouts
            if timeout_match:
                timeouts.append(
                    int(timeout_match.group(1))
                )
            else:
                timeouts.append(0)

    return {
        "tests": tests,
        "requests_per_sec": requests_per_sec,
        "latency_ms": latency_ms,
        "timeouts": timeouts,
    }


#############################
# System Information
#############################

def get_system_info():
    """
    Gather system information for display on the plots.
    """
    #TODO grab this logic from plot_benchmarks.py to avoid duplication
    info = {}

    info['OS'] = platform.platform()
    info['CPU_count'] = os.cpu_count()

    try:
        if platform.system() == 'Darwin':
            info['CPU_model'] = subprocess.check_output(
                ['sysctl', '-n', 'machdep.cpu.brand_string']
            ).decode().strip()

        elif platform.system() == 'Linux':

            with open('/proc/cpuinfo') as f:

                for line in f:

                    if 'model name' in line:
                        info['CPU_model'] = line.split(':')[1].strip()
                        break

        else:
            info['CPU_model'] = platform.processor()

    except Exception:
        info['CPU_model'] = "Unknown"

    info['Python'] = platform.python_version()

    info['Timestamp'] = datetime.datetime.now().strftime(
        '%Y-%m-%d %H:%M:%S'
    )

    return info


#############################
# Plotting Logic
#############################

def plot_results(data, sysinfo):
    '''
    Plot the benchmark results using matplotlib.
    '''
    tests = data["tests"]

    # -------------------------------------
    # Throughput Plot
    # -------------------------------------

    plt.figure(figsize=(10, 6))

    plt.bar(
        tests,
        data["requests_per_sec"]
    )

    plt.ylabel("Requests/sec")
    plt.title("FastAPI Benchmark - Throughput")

    for i, value in enumerate(data["requests_per_sec"]):

        plt.text(
            i,
            value,
            f"{value:.2f}",
            ha='center',
            va='bottom'
        )

    add_sysinfo(sysinfo)

    plt.tight_layout()
    plt.show()

    # -------------------------------------
    # Latency Plot
    # -------------------------------------

    plt.figure(figsize=(10, 6))

    plt.bar(
        tests,
        data["latency_ms"]
    )

    plt.ylabel("Average Latency (ms)")
    plt.title("FastAPI Benchmark - Latency")

    for i, value in enumerate(data["latency_ms"]):

        plt.text(
            i,
            value,
            f"{value:.2f}",
            ha='center',
            va='bottom'
        )

    add_sysinfo(sysinfo)

    plt.tight_layout()
    plt.show()

    # -------------------------------------
    # Timeout Plot
    # -------------------------------------

    plt.figure(figsize=(10, 6))

    plt.bar(
        tests,
        data["timeouts"]
    )

    plt.ylabel("Socket Timeouts")
    plt.title("FastAPI Benchmark - Timeouts")

    for i, value in enumerate(data["timeouts"]):

        plt.text(
            i,
            value,
            str(value),
            ha='center',
            va='bottom'
        )

    add_sysinfo(sysinfo)

    plt.tight_layout()
    plt.show()


#############################
# Add System Info to Plot
#############################

def add_sysinfo(sysinfo):

    text = "\n".join([
        "System Specs:",
        f"CPU: {sysinfo.get('CPU_model')}",
        f"Cores: {sysinfo.get('CPU_count')}",
        f"OS: {sysinfo.get('OS')}",
        f"Python: {sysinfo.get('Python')}",
        f"Timestamp: {sysinfo.get('Timestamp')}",
    ])

    plt.gcf().text(
        0.01,
        0.01,
        text,
        fontsize=9,
        family='monospace',
        bbox=dict(
            facecolor='white',
            alpha=0.7,
            edgecolor='gray'
        )
    )


#############################
# Main
#############################

if __name__ == "__main__":

    # Paste wrk output here
    with open("benchmark_output.txt", "r") as f:
        raw_text = f.read()

    data = parse_wrk_output(raw_text)

    sysinfo = get_system_info()

    plot_results(data, sysinfo)