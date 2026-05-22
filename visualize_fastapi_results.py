###########
# Imports #
###########
import re
import os
import platform
import datetime
import subprocess

import matplotlib.pyplot as plt
import numpy as np


#########################################
# Parse wrk Output
#########################################

def parse_wrk_output(filepath):
    """
    Parse the output of wrk benchmark and extract relevant metrics.
    
    Returns a dict with keys:
    - 'tests': list of test names (e.g. "CPU Sequential", "IO Bound")
    - 'rps': list of requests per second
    - 'latency': list of latency in milliseconds
    - 'timeouts': list of socket timeouts
    """
    with open(filepath, "r") as f:
        text = f.read()

    sections = re.split(r"=+\n", text)

    tests = []
    rps = []
    latency = []
    timeouts = []

    current_test = None

    for section in sections:

        title_match = re.search(
            r"(CPU Sequential|CPU Threaded|IO Bound|Mixed)",
            section
        )

        if title_match:
            current_test = title_match.group(1)

        rps_match = re.search(
            r"Requests/sec:\s+([\d.]+)",
            section
        )

        latency_match = re.search(
            r"Latency\s+([\d.]+)(ms|s|us)",
            section
        )

        timeout_match = re.search(
            r"timeout\s+(\d+)",
            section
        )

        if current_test and rps_match:

            tests.append(current_test)

            rps.append(
                float(rps_match.group(1))
            )

            # -----------------------
            # Convert latency to ms
            # -----------------------

            latency_value = 0

            if latency_match:

                value = float(latency_match.group(1))
                unit = latency_match.group(2)

                if unit == "s":
                    latency_value = value * 1000

                elif unit == "ms":
                    latency_value = value

                elif unit == "us":
                    latency_value = value / 1000

            latency.append(latency_value)

            # -----------------------
            # Timeouts
            # -----------------------

            if timeout_match:
                timeouts.append(
                    int(timeout_match.group(1))
                )
            else:
                timeouts.append(0)

    return {
        "tests": tests,
        "rps": rps,
        "latency": latency,
        "timeouts": timeouts,
    }


#########################################
# System Information
#########################################

def get_system_info():
    """
    Gather system information for display on the plots.
    """
    #TODO grab this logic from plot_benchmarks.py to avoid duplication
    info = {}

    info["OS"] = platform.platform()
    info["CPU_count"] = os.cpu_count()

    try:

        if platform.system() == "Darwin":

            info["CPU_model"] = subprocess.check_output(
                ["sysctl", "-n", "machdep.cpu.brand_string"]
            ).decode().strip()

        elif platform.system() == "Linux":

            with open("/proc/cpuinfo") as f:

                for line in f:

                    if "model name" in line:
                        info["CPU_model"] = line.split(":")[1].strip()
                        break

        else:
            info["CPU_model"] = platform.processor()

    except Exception:

        info["CPU_model"] = "Unknown"

    info["Python"] = platform.python_version()

    info["Timestamp"] = datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    return info


#########################################
# Add system info box
#########################################

def add_sysinfo(sysinfo):

    text = "\n".join([
        "System Specs:",
        f"CPU: {sysinfo['CPU_model']}",
        f"Cores: {sysinfo['CPU_count']}",
        f"OS: {sysinfo['OS']}",
        f"Python: {sysinfo['Python']}",
        f"Timestamp: {sysinfo['Timestamp']}",
    ])

    plt.gcf().text(
        0.01,
        0.01,
        text,
        fontsize=8,
        family='monospace',
        bbox=dict(
            facecolor='white',
            alpha=0.7,
            edgecolor='gray'
        )
    )


#########################################
# Plot Comparison
#########################################

def plot_comparison(gil, nogil, sysinfo):

    tests = gil["tests"]

    x = np.arange(len(tests))

    width = 0.35

    #####################################
    # Requests/sec
    #####################################

    plt.figure(figsize=(12, 6))

    plt.bar(
        x - width/2,
        gil["rps"],
        width,
        label="GIL ENABLED"
    )

    plt.bar(
        x + width/2,
        nogil["rps"],
        width,
        label="GIL DISABLED"
    )

    plt.xticks(x, tests)

    plt.ylabel("Requests/sec")

    plt.title("FastAPI Benchmark - Throughput")

    plt.legend()

    add_sysinfo(sysinfo)

    plt.tight_layout()

    plt.show()

    #####################################
    # Latency
    #####################################

    plt.figure(figsize=(12, 6))

    plt.bar(
        x - width/2,
        gil["latency"],
        width,
        label="GIL ENABLED"
    )

    plt.bar(
        x + width/2,
        nogil["latency"],
        width,
        label="GIL DISABLED"
    )

    plt.xticks(x, tests)

    plt.ylabel("Latency (ms)")

    plt.title("FastAPI Benchmark - Latency")

    plt.legend()

    add_sysinfo(sysinfo)

    plt.tight_layout()

    plt.show()

    #####################################
    # Timeouts
    #####################################

    plt.figure(figsize=(12, 6))

    plt.bar(
        x - width/2,
        gil["timeouts"],
        width,
        label="GIL ENABLED"
    )

    plt.bar(
        x + width/2,
        nogil["timeouts"],
        width,
        label="GIL DISABLED"
    )

    plt.xticks(x, tests)

    plt.ylabel("Socket Timeouts")

    plt.title("FastAPI Benchmark - Timeouts")

    plt.legend()

    add_sysinfo(sysinfo)

    plt.tight_layout()

    plt.show()


#########################################
# Main
#########################################

if __name__ == "__main__":

    gil = parse_wrk_output("gil_enabled.txt")

    nogil = parse_wrk_output("gil_disabled.txt")

    sysinfo = get_system_info()

    plot_comparison(
        gil,
        nogil,
        sysinfo
    )