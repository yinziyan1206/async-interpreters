__author__ = "ziyan.yin"
__date__ = "2024-10-16"

import pytest

from tests import calc_add, workers


@pytest.mark.asyncio
async def test_basic_lambda():
    ret = await workers.run_sync(lambda x, y: x + y, 5, 100)
    assert ret == 105


@pytest.mark.asyncio
async def test_lambda_with_dependency():
    ret = await workers.run_sync(lambda x, y: calc_add(x, y), 5, 100)
    assert ret == 4955