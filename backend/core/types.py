# core/types.py
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Result:
    """
    A class to represent the result of an operation.
    """

    success: bool
    message: str = ""
    data: Optional[Any] = None
