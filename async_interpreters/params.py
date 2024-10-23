__author__ = "ziyan.yin"
__date__ = "2024-10-17"

import sys
from textwrap import dedent as D

SHARED_TYPES = None | str | int | bool | float | bytes

ENV_CODE = D(
    f"""
    import marshal
    import pickle
    import sys
    from test.support import interpreters
    from types import FunctionType
    
    sys.path[:] = {sys.path}

    def _call(func, raw_data):
        func_data = pickle.loads(raw_data)
        return func(*func_data.args, **func_data.kwargs)
    """
)

CALL_CODE = D(
    """
    def _run(cid, raw_data):
        sender = interpreters.SendChannel(cid)
        closure = None
        {importer}
        res = _call(func, raw_data)
        sender.send_nowait(pickle.dumps(res))
    """
)
