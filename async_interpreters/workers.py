__author__ = "ziyan.yin"
__date__ = "2024-10-16"

import asyncio
import os
import pickle
import sys
import threading
from collections import deque
from collections.abc import Callable
from pathlib import Path
from typing import Any

from test.support import interpreters

from async_interpreters import utils
from async_interpreters.data import FunctionStructure
from async_interpreters.params import CALL_CODE, ENV_CODE, SHARED_TYPES


class Worker:
    
    def __init__(self, timeout: int = 60) -> None:
        self._interp = interpreters.create()
        self.recevier, self.sender = interpreters.create_channel()
        
        self.timeout = timeout * 100
        self._init_interpreter()
        self.raw_func: str | None = None
        self._should_exit = False
    
    def run_string(self, code: str, **shared_kwds: SHARED_TYPES) -> Any:
        return interpreters._interpreters.run_string(self._interp.id, code, shared=shared_kwds)
    
    def _init_interpreter(self) -> None:
        self.run_string(ENV_CODE, _cid=self.sender.id)
    
    def import_func(self, func: Callable) -> None:
        main_module = sys.modules["__main__"]
        main_module_name = Path(getattr(main_module, "__file__", "")).stem
        importers = [f"import {main_module_name} as __main__"]
        
        importers.extend(utils.load_func(func))
            
        self.raw_func = CALL_CODE.format(
            importer="\n    ".join(importers)
        )
        
    def execute(self, *args: Any, **kwds: Any) -> Any:
        try:
            if self.raw_func:
                print(self.raw_func)
                self.run_string(self.raw_func)
                self.raw_func = None
            shared = {
                "func_data": pickle.dumps(FunctionStructure(args=args, kwargs=kwds))
            }
            
            code = """_run(func_data)"""
            ret = self.run_string(code, **shared)
        except Exception:
            self._should_exit = True
            raise
        if ret:
            self._should_exit = True
            raise RuntimeError(ret)

    async def __call__(self, *args: Any, **kwds: Any) -> Any:
        _thread = threading.Thread(target=self.execute, args=args, kwargs=kwds, daemon=True)
        _thread.start()
        
        try:
            counter = 0
            while not self._should_exit:
                if res := self.recevier.recv_nowait(default=None):
                    _thread.join()
                    return pickle.loads(res)
                await asyncio.sleep(0.01)
                counter += 1
                if counter > self.timeout:
                    _thread.join(0)
                    raise TimeoutError
        finally:
            _thread.join()
            self.raw_func = None

    def close(self) -> None:
        if self._interp.is_running():
            self._interp.close()
            
    def __del__(self) -> None:
        self.close()
        self._interp = None


class WorkersPool:
    
    def __init__(self, max_size: int = -1, timeout: int = 60) -> None:
        if interpreters._interpreters.get_current() != interpreters._interpreters.get_main():
            return
        if max_size <= 0:
            max_size = os.cpu_count() or 2
        self._pool = deque(Worker(timeout=timeout) for _ in range(max_size))
    
    @property
    def is_empty(self) -> bool:
        return len(self._pool) == 0
    
    async def run_sync(self, func: Callable, *args: Any, **kwds: Any) -> Any:
        while self.is_empty:
            await asyncio.sleep(0.01)
        worker = self._pool.popleft()
        worker.import_func(func)
        res = await worker(*args, **kwds)
        self._pool.append(worker)
        return res

    def close(self) -> None:
        for worker in self._pool:
            worker.close()
    
    def __del__(self) -> None:
        if getattr(self, "_pool", None):
            self.close()
            self._pool.clear()
