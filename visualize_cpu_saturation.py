#!/usr/bin/env python3
"""
Visualization script for CPU saturation and performance metrics.
Compares GIL enabled vs disabled benchmarks.
"""
import subprocess
import re
import os
import platform
import datetime
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def parse_benchmark_output(output):
    """Parse benchmark output and extract timing data."""
    results = {
        'cpu_bound': {},
        'io_bound': {}
    }
    
    # Extract CPU-bound results
    cpu_section = re.search(r'=== CPU-Bound Benchmarks ===(.+?)(?:=== I/O-Bound|$)', output, re.DOTALL)
    if cpu_section:
        matches = re.findall(r'Threads:\s*(\d+)\s*\|\s*Time:\s*([\d.]+)s', cpu_section.group(1))
        for threads, time_val in matches:
            results['cpu_bound'][int(threads)] = float(time_val)
    
    # Extract I/O-bound results
    io_section = re.search(r'=== I/O-Bound Benchmarks ===(.+?)(?:=== Results|$)', output, re.DOTALL)
    if io_section:
        matches = re.findall(r'Threads:\s*(\d+)\s*\|\s*Time:\s*([\d.]+)s', io_section.group(1))
        for threads, time_val in matches:
            results['io_bound'][int(threads)] = float(time_val)
    
    return results

def run_benchmark_with_gil(gil_flag):
    """Run benchmark script with specific GIL setting."""
    python_exe = 'python'
    script_path = 'benchmark_with_cpu_saturation.py'
    
    try:
        result = subprocess.run(
            [python_exe, '-X', f'gil={gil_flag}', script_path],
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        print(f"Benchmark timed out for GIL={gil_flag}")
        return ""
    except Exception as e:
        print(f"Error running benchmark: {e}")
        return ""

def get_system_info():
    """Get system information for display."""
    info = {
        'platform': platform.platform(),
        'processor': platform.processor(),
        'cpu_count': os.cpu_count(),
        'python': platform.python_version(),
    }
    return info

def plot_comparison(results_gil0, results_gil1):
    """Create comprehensive comparison plots."""
    system_info = get_system_info()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Prepare data
    threads = sorted(results_gil0['cpu_bound'].keys())
    cpu_gil0 = [results_gil0['cpu_bound'][t] for t in threads]
    cpu_gil1 = [results_gil1['cpu_bound'][t] for t in threads]
    io_gil0 = [results_gil0['io_bound'][t] for t in threads]
    io_gil1 = [results_gil1['io_bound'][t] for t in threads]
    
    # Calculate speedups
    cpu_speedup_0 = [cpu_gil0[0] / t if t > 0 else 0 for t in cpu_gil0]
    cpu_speedup_1 = [cpu_gil1[0] / t if t > 0 else 0 for t in cpu_gil1]
    io_speedup_0 = [io_gil0[0] / t if t > 0 else 0 for t in io_gil0]
    io_speedup_1 = [io_gil1[0] / t if t > 0 else 0 for t in io_gil1]
    
    # Create figure with 4 subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'GIL Impact: CPU & I/O Saturation Analysis\n{timestamp}', fontsize=16, fontweight='bold')
    
    # CPU-Bound Execution Time
    ax = axes[0, 0]
    x = np.arange(len(threads))
    width = 0.35
    ax.bar(x - width/2, cpu_gil0, width, label='GIL Disabled', color='#FF6B6B', alpha=0.8)
    ax.bar(x + width/2, cpu_gil1, width, label='GIL Enabled', color='#4169E1', alpha=0.8)
    ax.set_xlabel('Thread Count')
    ax.set_ylabel('Execution Time (s)')
    ax.set_title('CPU-Bound: Execution Time')
    ax.set_xticks(x)
    ax.set_xticklabels(threads)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    # CPU-Bound Speedup
    ax = axes[0, 1]
    ax.plot(threads, cpu_speedup_0, marker='o', linewidth=2, markersize=8, label='GIL Disabled', color='#FF6B6B')
    ax.plot(threads, cpu_speedup_1, marker='s', linewidth=2, markersize=8, label='GIL Enabled', color='#4169E1')
    ax.axhline(y=1, color='gray', linestyle='--', alpha=0.5, label='Baseline (1 thread)')
    ax.set_xlabel('Thread Count')
    ax.set_ylabel('Speedup (1 thread baseline)')
    ax.set_title('CPU-Bound: Speedup Analysis')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log', base=2)
    
    # I/O-Bound Execution Time
    ax = axes[1, 0]
    ax.bar(x - width/2, io_gil0, width, label='GIL Disabled', color='#FF6B6B', alpha=0.8)
    ax.bar(x + width/2, io_gil1, width, label='GIL Enabled', color='#4169E1', alpha=0.8)
    ax.set_xlabel('Thread Count')
    ax.set_ylabel('Execution Time (s)')
    ax.set_title('I/O-Bound: Execution Time')
    ax.set_xticks(x)
    ax.set_xticklabels(threads)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    # I/O-Bound Speedup
    ax = axes[1, 1]
    ax.plot(threads, io_speedup_0, marker='o', linewidth=2, markersize=8, label='GIL Disabled', color='#FF6B6B')
    ax.plot(threads, io_speedup_1, marker='s', linewidth=2, markersize=8, label='GIL Enabled', color='#4169E1')
    ax.axhline(y=1, color='gray', linestyle='--', alpha=0.5, label='Baseline (1 thread)')
    ax.set_xlabel('Thread Count')
    ax.set_ylabel('Speedup (1 thread baseline)')
    ax.set_title('I/O-Bound: Speedup Analysis')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log', base=2)
    
    # Add system info text
    info_text = f"""
System Info:
  Platform: {system_info['platform']}
  CPU Cores: {system_info['cpu_count']}
  Python: {system_info['python']}
    """
    fig.text(0.02, 0.02, info_text, fontsize=9, family='monospace', 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout(rect=[0, 0.05, 1, 0.96])
    plt.savefig('cpu_saturation_comparison.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: cpu_saturation_comparison.png")
    plt.show()

def main():
    print("=" * 60)
    print("CPU Saturation & GIL Impact Benchmark")
    print("=" * 60)
    
    # Check if benchmark script exists
    if not Path('benchmark_with_cpu_saturation.py').exists():
        print("Error: benchmark_with_cpu_saturation.py not found!")
        return
    
    print("\nRunning benchmark with GIL DISABLED...")
    output_gil0 = run_benchmark_with_gil(0)
    results_gil0 = parse_benchmark_output(output_gil0)
    
    print("\nRunning benchmark with GIL ENABLED...")
    output_gil1 = run_benchmark_with_gil(1)
    results_gil1 = parse_benchmark_output(output_gil1)
    
    # Verify we got results
    if not results_gil0['cpu_bound'] or not results_gil1['cpu_bound']:
        print("Error: Could not parse benchmark results!")
        print("\nDebug output (GIL=0):")
        print(output_gil0[-500:] if output_gil0 else "No output")
        print("\nDebug output (GIL=1):")
        print(output_gil1[-500:] if output_gil1 else "No output")
        return
    
    print("\n" + "=" * 60)
    print("Generating comparison plots...")
    plot_comparison(results_gil0, results_gil1)
    print("=" * 60)

if __name__ == '__main__':
    main()
