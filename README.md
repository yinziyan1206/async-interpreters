# async-interpreters
subinterpreters for asyncio

## Usage

```python
from async_interpreters import WorkersPool

workers = WorkersPool(max_size=10, timeout=5)

def calc_sum(a, b):
    sum = a
    for i in range(b):
        sum += i
    return sum


async def usage():
    await workers.run_sync(calc_sum, 10, 100_000_000)


async def benchmark():
    t = time.perf_counter()
    await asyncio.gather(*(usage() for _ in range(10)))
    print(time.perf_counter() - t)

```

