__author__ = "ziyan.yin"
__date__ = "2024-10-16"

import dataclasses


@dataclasses.dataclass
class FunctionParams:
    args: tuple | None = None
    kwargs: dict | None = None
    