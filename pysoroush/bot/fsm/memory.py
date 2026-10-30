"""
In-memory storage for Finite State Machine (FSM).
"""

from typing import Any, Dict, Optional


class MemoryStorage:
    """
    Simple in-memory storage for managing user states and data.
    In a production environment, this can be replaced with Redis or SQLite.
    """

    def __init__(self) -> None:
        self.data: Dict[int, Dict[str, Any]] = {}

    def set_state(self, chat_id: int, state: str) -> None:
        if chat_id not in self.data:
            self.data[chat_id] = {}
        self.data[chat_id]["state"] = state

    def get_state(self, chat_id: int) -> Optional[str]:
        return self.data.get(chat_id, {}).get("state")

    def set_data(self, chat_id: int, key: str, value: Any) -> None:
        if chat_id not in self.data:
            self.data[chat_id] = {}
        if "data" not in self.data[chat_id]:
            self.data[chat_id]["data"] = {}
        self.data[chat_id]["data"][key] = value

    def get_data(self, chat_id: int, key: str, default: Any = None) -> Any:
        return self.data.get(chat_id, {}).get("data", {}).get(key, default)

    def clear(self, chat_id: int) -> None:
        self.data.pop(chat_id, None)


class Context:
    """
    Context object provided to handlers for easy state manipulation.
    """

    def __init__(self, chat_id: int, storage: MemoryStorage) -> None:
        self.chat_id = chat_id
        self.storage = storage

    @property
    def state(self) -> Optional[str]:
        return self.storage.get_state(self.chat_id)

    def set_state(self, state: str) -> None:
        self.storage.set_state(self.chat_id, state)

    def get_data(self, key: str, default: Any = None) -> Any:
        return self.storage.get_data(self.chat_id, key, default)

    def set_data(self, key: str, value: Any) -> None:
        self.storage.set_data(self.chat_id, key, value)

    def clear(self) -> None:
        self.storage.clear(self.chat_id)
