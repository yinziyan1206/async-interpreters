__author__ = "ziyan.yin"
__date__ = "2024-10-16"

import pytest

from tests import calc_add, workers


def calc_add_local(a, b):
    sum = a
    for i in range(b):
        sum += i
    return sum


@pytest.mark.asyncio
async def test_main_method():
    ret = await workers.run_sync(calc_add_local, 5, 100)
    assert ret == 4955


@pytest.mark.asyncio
async def test_remote_method():
    ret = await workers.run_sync(calc_add, 5, 100)
    assert ret == 4955
