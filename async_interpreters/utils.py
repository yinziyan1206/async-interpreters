__author__ = "ziyan.yin"
__date__ = "2024-10-17"


import functools
import inspect
import marshal
import pickle
from collections.abc import Callable
from types import FunctionType, MethodType, ModuleType


def load_func(func: Callable) -> list[str]:
    importers = []
    
    for name, obj in inspect.getmembers(__import__(func.__module__)):
        if isinstance(obj, ModuleType) and obj.__name__ != 'builtins':
            importers.append(f"import {obj.__name__} as {name}")
        elif isinstance(obj, FunctionType) and obj.__module__ not in ("__main__", "builtins"):
            importers.append(f"from {obj.__module__} import {obj.__name__} as {name}")
    
    if isinstance(func, FunctionType | MethodType):
        if func.__closure__:
            raw_closure_contents = tuple(x.cell_contents for x in func.__closure__)
            importers.append("from types import CellType")
            importers.append(
                f"closure = tuple(CellType(x) for x in pickle.loads({pickle.dumps(raw_closure_contents)}))"  # type: ignore
            )
        importers.append(f"func_code = marshal.loads({marshal.dumps(func.__code__)})")  # type: ignore
        importers.append("func = FunctionType(func_code, locals(), closure=closure)")
        if isinstance(func, MethodType):
            importers.append(f"self = pickle.loads({pickle.dumps(func.__self__)})")  # type: ignore
            importers.append("from types import MethodType")
            importers.append("func = MethodType(func, self)")
    elif isinstance(func, functools.partial):
        importers.append("import functools")
        inner_importers = load_func(func.func)
        importers.extend(inner_importers)
        importers.append(f"func_args = pickle.loads({pickle.dumps(func.args)})")  # type: ignore
        importers.append(f"func_kwargs = pickle.loads({pickle.dumps(func.keywords)})")  # type: ignore
        importers.append("func = functools.partial(func, *func_args, **func_kwargs)")
    elif inner_func := getattr(func, "__call__", None):
        inner_importers = load_func(inner_func)
        importers.extend(inner_importers)
    else:
        raise TypeError(f"{func} is not callable")

    return importers
