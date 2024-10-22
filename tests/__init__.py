__author__ = "ziyan.yin"
__date__ = "2024-10-16"


from async_interpreters import WorkersPool

workers = WorkersPool(max_size=10)


def calc_add(a: int, b: int) -> int:
    sum = a
    for i in range(b):
        sum += i
    return sum
