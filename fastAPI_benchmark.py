#############################
# FastAPI Benchmarking Code #
#############################
import sys
import math
import time
import asyncio
from fastapi import FastAPI
from concurrent.futures import ThreadPoolExecutor

######################
# Benchmarking logic #
######################

app = FastAPI()
# create a thread pool executor for CPU-bound tasks
EXECUTOR = ThreadPoolExecutor(max_workers=8)


def cpu_heavy(n: int = 2_000_000):
    '''
    A CPU-bound task that performs a large number of calculations.
    '''
    total = 0.0
    for i in range(1, n):
        total += math.sqrt(i) * math.sin(i)

    return total

##########################
# Benchmarking Endpoints #
##########################

@app.get("/health")
def health():
    ''' a simple health check endpoint '''
    return {"status": "ok"}


# Sequential CPU endpoint
@app.get("/cpu-seq")
def cpu_seq():
    '''
    A CPU-bound endpoint that runs a heavy computation sequentially.
    '''
    start = time.perf_counter()

    result = cpu_heavy()

    return {
        "mode": "sequential",
        "duration": time.perf_counter() - start,
        "result": result,
    }


# Parallel threaded CPU endpoint
@app.get("/cpu-thread")
def cpu_thread():
    '''
    A CPU-bound endpoint that runs a heavy computation in parallel using threads.
    '''
    start = time.perf_counter()

    futures = [
        EXECUTOR.submit(cpu_heavy, 500_000)
        for _ in range(4)
    ]

    results = [f.result() for f in futures]

    return {
        "mode": "threaded",
        "duration": time.perf_counter() - start,
        "result": sum(results),
    }


# Async IO simulation
@app.get("/io")
async def io_test():
    '''
    An I/O-bound endpoint that simulates waiting for an external resource.
    '''
    await asyncio.sleep(0.05)

    return {
        "mode": "io"
    }


# Mixed workload
@app.get("/mixed")
def mixed():
    '''
    An endpoint that performs both CPU-bound and I/O-bound tasks.
    '''
    start = time.perf_counter()

    cpu_heavy(500_000)

    time.sleep(0.01)

    return {
        "mode": "mixed",
        "duration": time.perf_counter() - start,
    }

@app.get("/gil")
def gil():
    return {
        "gil_enabled": sys._is_gil_enabled()
    }