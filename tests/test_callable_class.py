__author__ = "ziyan.yin"
__date__ = "2024-10-16"

import pytest

from tests import calc_add, workers


class LocalCall:
    
    def __init__(self, a, b):
        self.a = a
        self.b = b
    
    def __call__(self):
        return self.a + self.b


class CallWithDependency:
    
    def __init__(self, a, b):
        self.a = a
        self.b = b
    
    def __call__(self):
        return calc_add(self.a, self.b)


class CallMethod:
    
    def __init__(self, a, b):
        self.a = a
        self.b = b
    
    def call(self):
        return calc_add(self.a, self.b)


@pytest.mark.asyncio
async def test_basic_callable_class():
    call = LocalCall(5, 100)
    ret = await workers.run_sync(call)
    assert ret == 105


@pytest.mark.asyncio
async def test_callable_class_with_dependency():
    call = CallWithDependency(5, 100)
    ret = await workers.run_sync(call)
    assert ret == 4955


@pytest.mark.asyncio
async def test_class_method():
    call = CallMethod(5, 100)
    ret = await workers.run_sync(call.call)
    assert ret == 4955
