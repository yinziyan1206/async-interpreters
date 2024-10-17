__author__ = "ziyan.yin"
__date__ = "2024-10-16"

import pytest

from tests import workers


@pytest.mark.asyncio
async def test_basic_lambda():
    ret = await workers.run_sync(lambda x, y: x + y, 5, 100)
    assert ret == 105
