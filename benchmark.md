# BENCHMARK

## CODE

```python

import asyncio
from multiprocessing import Process
from threading import Thread
import time
from async_interpreters import WorkersPool

workers = WorkersPool(max_size=10, timeout=5)

def calc_sum(a, b):
    sum = a
    for i in range(b):
        sum += i
    return sum


async def usage():
    await workers.run_sync(calc_sum, 10, 10_000_000)


def thread_benchmark():
    tasks = [Thread(target=calc_sum, args=(10, 10_000_000)) for _ in range(10)]
    t = time.perf_counter()
    for task in tasks:
        task.start()
    for task in tasks:
        task.join()
    print("thread", time.perf_counter() - t)


def process_benchmark():
    tasks = [Process(target=calc_sum, args=(10, 10_000_000)) for _ in range(10)]
    t = time.perf_counter()
    for task in tasks:
        task.start()
    for task in tasks:
        task.join()
    print("process", time.perf_counter() - t)


async def benchmark():
    t = time.perf_counter()
    await asyncio.gather(*(usage() for _ in range(10)))
    print("subinterpreters(with asyncio)", time.perf_counter() - t)

```

> thread 2.4889633000129834
> process 1.1637972999888007
> subinterpreters(with asyncio) 0.4967340999864973
>