"""
InputFile type for uploading files to Soroush Plus.
"""

from __future__ import annotations

import os
from typing import Optional, Union, IO


class InputFile:
    """
    Represents a file to be uploaded.
    Can accept a local file path (str), bytes, or a file-like object.
    """

    def __init__(self, file: Union[str, bytes, IO], filename: Optional[str] = None) -> None:
        self.file = file
        self.filename = filename
        self._file_obj: Optional[IO] = None

    def _open(self) -> IO:
        if isinstance(self.file, str):
            if not os.path.exists(self.file):
                raise FileNotFoundError(f"File not found: {self.file}")
            
            if self.filename is None:
                self.filename = os.path.basename(self.file)
                
            self._file_obj = open(self.file, "rb")
            return self._file_obj
        
        elif isinstance(self.file, bytes):
            import io
            self._file_obj = io.BytesIO(self.file)
            if self.filename is None:
                self.filename = "file.bin"
            return self._file_obj
        
        else:
            # Assume it's already a file-like object (e.g., open('file.jpg', 'rb'))
            if self.filename is None:
                self.filename = getattr(self.file, "name", "file.bin")
            return self.file

    def close(self) -> None:
        if self._file_obj and not self._file_obj.closed:
            self._file_obj.close()
            self._file_obj = None

    def __enter__(self) -> "InputFile":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
