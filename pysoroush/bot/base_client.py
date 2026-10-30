"""
Base client for the Soroush Plus Bot API.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional, Tuple, List

from .constants import (
    BASE_URL, DEFAULT_REQUEST_TIMEOUT, DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_RETRY_BACKOFF, DEFAULT_RETRY_INITIAL_DELAY,
)
from .exceptions import SoroushValidationError
from .types import BaseType, InputFile


class BaseClient:
    def __init__(
        self, token: str, base_url: str = BASE_URL, timeout: int = DEFAULT_REQUEST_TIMEOUT,
        retries: int = DEFAULT_RETRY_ATTEMPTS, backoff: float = DEFAULT_RETRY_BACKOFF, debug: bool = False,
    ) -> None:
        if not token or ":" not in token:
            raise SoroushValidationError("Invalid token. A Soroush bot token must contain a colon ':'.")

        self.token = token
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff
        self.debug = debug

    def _get_method_url(self, method: str) -> str:
        return f"{self.base_url}/bot{self.token}/{method}"

    def _get_retry_delay(self, attempt: int) -> float:
        return DEFAULT_RETRY_INITIAL_DELAY * (self.backoff ** attempt)

    def _debug_log(self, *args: Any, **kwargs: Any) -> None:
        if self.debug:
            print("[PySoroush Debug]", *args, **kwargs)

    def _build_payload(self, **kwargs: Any) -> Dict[str, Any]:
        payload = {}
        for k, v in kwargs.items():
            if v is None:
                continue
            if isinstance(v, BaseType):
                payload[k] = json.dumps(v.to_dict())
            elif isinstance(v, list) and all(isinstance(i, BaseType) for i in v):
                payload[k] = json.dumps([i.to_dict() for i in v])
            elif isinstance(v, (dict, list)):
                payload[k] = json.dumps(v)
            else:
                payload[k] = v
        return payload

    def _prepare_media_and_files(self, **kwargs: Any) -> Tuple[Dict[str, Any], Dict[str, Any], List[Any]]:
        data = {}
        files = {}
        opened_files = []
        for k, v in kwargs.items():
            if v is None:
                continue
            if isinstance(v, InputFile):
                f_obj = v._open()
                opened_files.append(f_obj)
                filename = v.filename or getattr(f_obj, "name", "file.bin")
                files[k] = (filename, f_obj)
            elif isinstance(v, BaseType):
                data[k] = json.dumps(v.to_dict())
            elif isinstance(v, list) and all(isinstance(i, BaseType) for i in v):
                data[k] = json.dumps([i.to_dict() for i in v])
            elif isinstance(v, (dict, list)):
                data[k] = json.dumps(v)
            else:
                data[k] = v
        return data, files, opened_files

    def _prepare_media_group(self, media: List[Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any], List[Any]]:
        """
        Prepares a media group for upload.
        If an InputFile is found inside the media items, it converts it to attach://<name>.
        """
        processed_media = []
        files = {}
        opened_files = []
        
        for i, item in enumerate(media):
            if hasattr(item, "media") and isinstance(item.media, InputFile):
                f_obj = item.media._open()
                opened_files.append(f_obj)
                attach_name = f"file_{i}"
                filename = item.media.filename or getattr(f_obj, "name", "file")
                files[attach_name] = (filename, f_obj)
                
                # Temporarily replace with attach:// and serialize
                original_media = item.media
                item.media = f"attach://{attach_name}"
                processed_media.append(item.to_dict())
                item.media = original_media # restore original
            else:
                processed_media.append(item.to_dict())
                
        return processed_media, files, opened_files
