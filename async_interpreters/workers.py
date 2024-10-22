__author__ = "ziyan.yin"
__date__ = "2024-10-16"

import asyncio
import os
import pickle
import anyio
from collections import deque
from collections.abc import Callable
from typing import Any

import anyio.to_thread
from test.support import interpreters

from async_interpreters import utils
from async_interpreters.data import FunctionParams
from async_interpreters.params import CALL_CODE, ENV_CODE, SHARED_TYPES


class Worker:
    
    def __init__(self) -> None:
        self._interp = interpreters.create()
        self.recevier, self.sender = interpreters.create_channel()
        
        self._init_interpreter()
        self.raw_func: str | None = None
    
    def run_string(self, code: str, **shared_kwds: SHARED_TYPES) -> Any:
        return interpreters._interpreters.run_string(self._interp.id, code, shared=shared_kwds)
    
    def _init_interpreter(self) -> None:
        self.run_string(ENV_CODE, _cid=self.sender.id)
    
    def reload_func(self, func: Callable) -> None:
        importers = utils.load_main()
        importers.extend(utils.load_func(func))
        
        self._load_func(importers)
        
    def _load_func(self, importers: list[str]) -> None:
        self.raw_func = CALL_CODE.format(
            importer="\n    ".join(importers)
        )
        
    def execute(self, params: FunctionParams) -> None:
        try:
            if self.raw_func:
                self.run_string(self.raw_func)
                self.raw_func = None
            shared = {
                "func_data": pickle.dumps(params)
            }
            
            code = """_run(func_data)"""
            ret = self.run_string(code, **shared)
        except Exception:
            raise
        if ret:
            raise RuntimeError(ret)

    def close(self) -> None:
        if self._interp.is_running():
            self._interp.close()
            
    def __del__(self) -> None:
        self.close()
        self._interp = None


class WorkersPool:
    
    def __init__(self, max_size: int = -1) -> None:
        if interpreters._interpreters.get_current() != interpreters._interpreters.get_main():
            return
        if max_size <= 0:
            max_size = os.cpu_count() or 2
        self._pool = deque(Worker() for _ in range(max_size))
    
    @property
    def is_empty(self) -> bool:
        return len(self._pool) == 0
    
    async def acquire(self) -> Worker:
        while self.is_empty:
            await asyncio.sleep(0.01)
        return self._pool.popleft()
    
    def release(self, worker: Worker) -> None:
        self._pool.append(worker)
    
    async def run_sync(self, func: Callable, *args: Any, **kwds: Any) -> Any:
        worker = await self.acquire()
        worker.reload_func(func)
        try:
            await anyio.to_thread.run_sync(
                worker.execute,
                FunctionParams(args=args, kwargs=kwds)
            )
            if res := worker.recevier.recv_nowait(default=None):
                return pickle.loads(res)
            return None
        finally:
            self.release(worker)

    def close(self) -> None:
        for worker in self._pool:
            worker.close()
    
    def __del__(self) -> None:
        if getattr(self, "_pool", None):
            self.close()
            self._pool.clear()
