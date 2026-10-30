"""
File type for downloading files.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ._base import BaseType


@dataclass
class File(BaseType):
    file_id: str
    file_unique_id: str
    file_size: Optional[int] = None
    file_path: Optional[str] = None
