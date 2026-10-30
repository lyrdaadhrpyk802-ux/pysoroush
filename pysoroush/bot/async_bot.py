"""
High-level asynchronous Bot interface for PySoroush.
"""

from __future__ import annotations

import asyncio
import inspect
from typing import Callable, Dict, List, Optional, Any, Union

from .async_client import AsyncClient
from .types import Update, Message, CallbackQuery
from .exceptions import SoroushError
from .filters import Filter
from .fsm import MemoryStorage, Context


class AsyncBot(AsyncClient):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._handlers: Dict[str, Any] = {"message": [], "command": {}, "callback_query": []}
        self.storage = MemoryStorage()

    def get_context(self, chat_id: int) -> Context:
        return Context(chat_id, self.storage)

    def set_state(self, chat_id: int, state: str) -> None:
        self.storage.set_state(chat_id, state)

    def get_state(self, chat_id: int) -> Optional[str]:
        return self.storage.get_state(chat_id)

    def clear_state(self, chat_id: int) -> None:
        self.storage.clear(chat_id)

    def on_message(self, filter_obj: Optional[Filter] = None) -> Callable:
        def decorator(func: Callable) -> Callable:
            self._handlers["message"].append((filter_obj, func))
            return func
        return decorator

    def command(self, name: str, filter_obj: Optional[Filter] = None) -> Callable:
        def decorator(func: Callable) -> Callable:
            self._handlers["command"][name] = (filter_obj, func)
            return func
        return decorator

    def on_callback(self, filter_obj: Optional[Filter] = None) -> Callable:
        def decorator(func: Callable) -> Callable:
            self._handlers["callback_query"].append((filter_obj, func))
            return func
        return decorator

    async def reply(self, message: Message, text: str, **kwargs: Any) -> Message:
        return await self.send_message(
            chat_id=message.chat.id, text=text, reply_to_message_id=message.message_id, **kwargs
        )

    async def _execute_handler(self, handler: Callable, *args: Any) -> Any:
        sig = inspect.signature(handler)
        if len(sig.parameters) >= 2:
            return await handler(*args)
        else:
            return await handler(args[0])

    async def _process_update(self, update: Update) -> None:
        if update.message:
            msg = update.message
            msg.state = self.get_state(msg.chat.id)
            ctx = self.get_context(msg.chat.id)
            
            if msg.text and msg.text.startswith("/"):
                command_part = msg.text.split()[0][1:]
                command_name = command_part.split("@")[0]
                if command_name in self._handlers["command"]:
                    filter_obj, handler = self._handlers["command"][command_name]
                    if filter_obj is None or filter_obj(msg):
                        if await self._execute_handler(handler, msg, ctx) is True:
                            return

            for filter_obj, handler in self._handlers["message"]:
                if filter_obj is None or filter_obj(msg):
                    if await self._execute_handler(handler, msg, ctx) is True:
                        return

        elif update.callback_query:
            for filter_obj, handler in self._handlers["callback_query"]:
                if filter_obj is None or filter_obj(update.callback_query):
                    if await self._execute_handler(handler, update.callback_query) is True:
                        return

    async def run_polling(self, timeout: int = 30, limit: int = 100) -> None:
        self._debug_log("Starting async bot polling...")
        offset = 0
        try:
            while True:
                try:
                    updates = await self.get_updates(offset=offset, timeout=timeout, limit=limit)
                    for update in updates:
                        offset = update.update_id + 1
                        await self._process_update(update)
                except SoroushError as e:
                    self._debug_log(f"Polling error: {e}. Retrying in 5s...")
                    await asyncio.sleep(5)
        except asyncio.CancelledError:
            self._debug_log("Bot polling cancelled.")
        finally:
            await self.close()

    async def run(self, *args: Any, **kwargs: Any) -> None:
        await self.run_polling(*args, **kwargs)
