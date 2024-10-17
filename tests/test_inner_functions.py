__author__ = "ziyan.yin"
__date__ = "2024-10-16"

import pytest

from tests import  calc_add, workers


@pytest.mark.asyncio
async def test_inner_method():
    a = 5
    
    def calc_add_local(b):
        sum = a
        for i in range(b):
            sum += i
        return sum

    ret = await workers.run_sync(calc_add_local, 100, locals={"a": 5})
    assert ret == 4955


@pytest.mark.asyncio
async def test_inner_method_2():
    a = 5
    
    def calc_add_local(b):
        return calc_add(a, b)

    ret = await workers.run_sync(calc_add_local, 100, locals={"a": 5})
    assert ret == 4955
