"""
Synchronous wrapper for the Soroush Plus User Account (Self) API.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Optional, Any, List, Union, Callable, BinaryIO

from .async_client import AsyncClient as _AsyncClient


class Client:
    """
    Synchronous client for interacting with Soroush Plus as a user.
    Exposes both high-level methods and raw TL request execution.
    """

    def __init__(self, session_string: Optional[str] = None, session_file: str = "pysoroush_account") -> None:
        self._async = _AsyncClient(session_string=session_string, session_file=session_file)
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def _get_loop(self) -> asyncio.AbstractEventLoop:
        if self._loop is None or self._loop.is_closed():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        return self._loop

    def _run(self, coro):
        return self._get_loop().run_until_complete(coro)

    # === Raw TL API access ===
    def __call__(self, request: Any) -> Any:
        return self._run(self._async(request))

    def raw(self, request: Any) -> Any:
        return self._run(self._async.raw(request))

    # === Connection ===
    def connect(self) -> None: self._run(self._async.connect())
    def disconnect(self) -> None:
        self._run(self._async.disconnect())
        if self._loop and not self._loop.is_closed(): self._loop.close()
    def is_connected(self) -> bool: return self._run(self._async.is_connected())
    def run_until_disconnected(self) -> None:
        try: self._run(self._async.run_until_disconnected())
        except KeyboardInterrupt: self._run(self._async.disconnect())
    def catch_up(self) -> None: return self._run(self._async.catch_up())

    # === Auth ===
    def start(self, phone: str, code_callback=None, password: Optional[str] = None) -> None:
        self._run(self._async.start(phone=phone, code_callback=code_callback, password=password))
    def is_authorized(self) -> bool: return self._run(self._async.is_authorized())
    def log_out(self) -> None: self._run(self._async.log_out())

    # === User info ===
    def get_me(self) -> Any: return self._run(self._async.get_me())
    def get_entity(self, entity: Union[str, int, Any]) -> Any: return self._run(self._async.get_entity(entity))
    def get_input_entity(self, entity: Union[str, int, Any]) -> Any: return self._run(self._async.get_input_entity(entity))
    def get_peer_id(self, entity: Union[str, int, Any]) -> int: return self._run(self._async.get_peer_id(entity))
    def get_full_user(self, entity: Union[str, int, Any]) -> Any: return self._run(self._async.get_full_user(entity))
    def get_full_channel(self, entity: Union[str, int, Any]) -> Any: return self._run(self._async.get_full_channel(entity))
    def get_profile_photos(self, entity: Union[str, int, Any], limit: int = 100) -> Any: return self._run(self._async.get_profile_photos(entity, limit))
    def get_dialogs(self, limit: int = 100) -> List[Any]: return self._run(self._async.get_dialogs(limit))
    def get_participants(self, entity: Any, limit: int = 100) -> Any: return self._run(self._async.get_participants(entity, limit))

    def iter_dialogs(self, limit: Optional[int] = None):
        return self._run(self._async.get_dialogs(limit or 100))

    def iter_participants(self, entity: Any, limit: Optional[int] = None, **kwargs):
        return self._run(self._async.get_participants(entity, limit or 100))

    # === Sending ===
    def send_message(self, entity: Any, text: str, **kwargs) -> Any: return self._run(self._async.send_message(entity, text, **kwargs))
    def send_scheduled_message(self, entity: Any, text: str, schedule_date: datetime) -> Any: return self._run(self._async.send_scheduled_message(entity, text, schedule_date))
    def send_file(self, entity: Any, file, **kwargs) -> Any: return self._run(self._async.send_file(entity, file, **kwargs))
    def send_photo(self, entity: Any, file, caption: Optional[str] = None) -> Any: return self._run(self._async.send_photo(entity, file, caption))
    def send_document(self, entity: Any, file, caption: Optional[str] = None) -> Any: return self._run(self._async.send_document(entity, file, caption))
    def send_sticker(self, entity: Any, file) -> Any: return self._run(self._async.send_sticker(entity, file))
    def send_location(self, entity: Any, latitude: float, longitude: float) -> Any: return self._run(self._async.send_location(entity, latitude, longitude))
    def send_contact(self, entity: Any, phone_number: str, first_name: str, last_name: str = "") -> Any: return self._run(self._async.send_contact(entity, phone_number, first_name, last_name))
    def send_poll(self, entity: Any, question: str, options: List[str], **kwargs) -> Any: return self._run(self._async.send_poll(entity, question, options, **kwargs))
    def forward_messages(self, entity: Any, messages: Any, from_entity: Any) -> Any: return self._run(self._async.forward_messages(entity, messages, from_entity))
    def send_reaction(self, entity: Any, message_id: int, emoji: str) -> Any: return self._run(self._async.send_reaction(entity, message_id, emoji))

    # === Reading ===
    def get_messages(self, entity: Any, limit: int = 100, **kwargs) -> List[Any]: return self._run(self._async.get_messages(entity, limit, **kwargs))
    def search_messages(self, entity: Any, query: str, limit: int = 100) -> List[Any]: return self._run(self._async.search_messages(entity, query, limit))
    def get_messages_views(self, entity: Any, message_ids: List[int], increment: bool = False) -> Any: return self._run(self._async.get_messages_views(entity, message_ids, increment))

    def iter_messages(self, entity: Any, limit: Optional[int] = None, **kwargs):
        offset_id = 0
        remaining = limit
        while True:
            size = min(100, remaining) if remaining else 100
            batch = self.get_messages(entity, limit=size, offset_id=offset_id, **kwargs)
            if not batch: return
            for msg in batch:
                yield msg
                if remaining is not None:
                    remaining -= 1
                    if remaining <= 0: return
            offset_id = batch[-1].id

    # === Managing messages ===
    def edit_message(self, entity: Any, message: Any, text: str, **kwargs) -> Any: return self._run(self._async.edit_message(entity, message, text, **kwargs))
    def delete_messages(self, entity: Any, message_ids: Any, revoke: bool = True) -> Any: return self._run(self._async.delete_messages(entity, message_ids, revoke))
    def clear_history(self, entity: Any, max_id: int = 0, just_clear: bool = False, revoke: bool = True) -> Any: return self._run(self._async.clear_history(entity, max_id, just_clear, revoke))
    def save_draft(self, entity: Any, text: str) -> Any: return self._run(self._async.save_draft(entity, text))
    def pin_message(self, entity: Any, message: Any, notify: bool = True) -> Any: return self._run(self._async.pin_message(entity, message, notify))
    def unpin_message(self, entity: Any, message: Optional[Any] = None) -> Any: return self._run(self._async.unpin_message(entity, message))
    def mark_as_read(self, entity: Any) -> bool: return self._run(self._async.mark_as_read(entity))
    def send_chat_action(self, entity: Any, action: str = "typing") -> Any: return self._run(self._async.send_chat_action(entity, action))

    # === Chat & Channels ===
    def create_group(self, title: str, users: List[Any]) -> Any: return self._run(self._async.create_group(title, users))
    def create_channel(self, title: str, about: str = "", megagroup: bool = False) -> Any: return self._run(self._async.create_channel(title, about, megagroup))
    def join_chat(self, entity: Any) -> Any: return self._run(self._async.join_chat(entity))
    def join_chat_invite(self, invite_hash: str) -> Any: return self._run(self._async.join_chat_invite(invite_hash))
    def leave_chat(self, entity: Any) -> Any: return self._run(self._async.leave_chat(entity))
    def export_chat_invite_link(self, entity: Any) -> str: return self._run(self._async.export_chat_invite_link(entity))
    def add_chat_user(self, chat: Any, user: Any, forward_limit: int = 100) -> Any: return self._run(self._async.add_chat_user(chat, user, forward_limit))
    def invite_to_channel(self, channel: Any, users: List[Any]) -> Any: return self._run(self._async.invite_to_channel(channel, users))
    def get_stats(self, entity: Any, dark: bool = True) -> Any: return self._run(self._async.get_stats(entity, dark))

    # === Folders & Chats ===
    def get_folders(self) -> Any: return self._run(self._async.get_folders())
    def edit_folder(self, folder_id: int, title: str, **kwargs) -> Any: return self._run(self._async.edit_folder(folder_id, title, **kwargs))
    def pin_dialog(self, entity: Any, pin: bool = True) -> Any: return self._run(self._async.pin_dialog(entity, pin))
    def unpin_dialog(self, entity: Any) -> Any: return self._run(self._async.unpin_dialog(entity))
    def mute_chat(self, entity: Any, mute_until: Optional[datetime] = None) -> Any: return self._run(self._async.mute_chat(entity, mute_until))
    def unmute_chat(self, entity: Any) -> Any: return self._run(self._async.unmute_chat(entity))
    def archive_chat(self, entity: Any) -> Any: return self._run(self._async.archive_chat(entity))
    def unarchive_chat(self, entity: Any) -> Any: return self._run(self._async.unarchive_chat(entity))

    # === Admin & Blocks ===
    def kick_participant(self, entity: Any, user: Any) -> Any: return self._run(self._async.kick_participant(entity, user))
    def edit_admin(self, entity: Any, user: Any, **kwargs) -> Any: return self._run(self._async.edit_admin(entity, user, **kwargs))
    def block_user(self, user: Any) -> bool: return self._run(self._async.block_user(user))
    def unblock_user(self, user: Any) -> bool: return self._run(self._async.unblock_user(user))

    # === Profile ===
    def update_profile(self, first_name=None, last_name=None, about=None) -> bool: return self._run(self._async.update_profile(first_name, last_name, about))
    def update_username(self, username: str) -> bool: return self._run(self._async.update_username(username))
    def set_profile_photo(self, file) -> Any: return self._run(self._async.set_profile_photo(file))
    def delete_profile_photos(self, photos: List[Any]) -> Any: return self._run(self._async.delete_profile_photos(photos))

    # === Media download ===
    def download_media(self, message_or_media: Any, file: Optional[str] = None, **kwargs) -> Optional[str]: return self._run(self._async.download_media(message_or_media, file, **kwargs))
    def download_profile_photo(self, entity: Any, file: Optional[str] = None) -> Optional[str]: return self._run(self._async.download_profile_photo(entity, file))

    # === Event handlers ===
    def on_message(self, pattern=None, chats=None, from_users=None) -> Callable: return self._async.on_message(pattern, chats, from_users)
    def on_edited_message(self, chats=None) -> Callable: return self._async.on_edited_message(chats)
    def on_deleted_message(self, chats=None) -> Callable: return self._async.on_deleted_message(chats)
    def on_callback(self) -> Callable: return self._async.on_callback()
    def on_user_update(self) -> Callable: return self._async.on_user_update()
    def on_chat_action(self, chats=None) -> Callable: return self._async.on_chat_action(chats)
    def on_message_read(self, chats=None) -> Callable: return self._async.on_message_read(chats)
    def on_album(self, chats=None) -> Callable: return self._async.on_album(chats)
    def on_raw(self) -> Callable: return self._async.on_raw()
