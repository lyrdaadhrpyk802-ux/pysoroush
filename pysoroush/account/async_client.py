"""
Asynchronous client for the Soroush Plus User Account (Self) API.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import (
    Optional, Any, List, Union, Callable, AsyncIterator, BinaryIO,
)

from splusthon import SoroushClient, events
from splusthon.sessions import StringSession
from splusthon.errors import SessionPasswordNeededError

from splusthon.tl.types import (
    ReactionEmoji, ChatAdminRights, InputMediaPoll, Poll, PollAnswer,
    InputGeoPoint, InputMediaGeoPoint, InputMediaContact,
)

from .exceptions import AuthError, PasswordRequiredError, SoroushAccountError


class AsyncClient:
    """
    Asynchronous client for interacting with Soroush Plus as a user.
    """

    def __init__(
        self,
        session_string: Optional[str] = None,
        session_file: str = "pysoroush_account",
    ) -> None:
        self.session_string = session_string
        self.session_file = session_file
        session = StringSession(session_string) if session_string else session_file
        self._client: SoroushClient = SoroushClient(session)

    # ==================================================================
    # Raw TL API
    # ==================================================================

    async def __call__(self, request: Any) -> Any:
        await self.connect()
        return await self._client(request)

    async def raw(self, request: Any) -> Any:
        return await self(request)

    # ==================================================================
    # Context manager & connection
    # ==================================================================

    async def __aenter__(self) -> "AsyncClient":
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.disconnect()

    async def connect(self) -> None:
        if not self._client.is_connected():
            await self._client.connect()

    async def disconnect(self) -> None:
        if self._client.is_connected():
            await self._client.disconnect()
        await asyncio.sleep(0.1)

    async def is_connected(self) -> bool:
        return self._client.is_connected()

    async def run_until_disconnected(self) -> None:
        await self.connect()
        try:
            await self._client.run_until_disconnected()
        except asyncio.CancelledError:
            await self.disconnect()

    async def catch_up(self) -> None:
        await self.connect()
        try:
            return await self._client.catch_up()
        except Exception as e:
            raise SoroushAccountError(f"Failed to catch up: {e}")

    # ==================================================================
    # Auth
    # ==================================================================

    async def start(self, phone: str, code_callback=None, password: Optional[str] = None) -> None:
        try:
            await self._client.start(phone=phone, code_callback=code_callback, password=password)
        except SessionPasswordNeededError:
            raise PasswordRequiredError("Two-step verification is enabled. Please provide a password.")
        except Exception as e:
            raise AuthError(f"Login failed: {e}")

    async def is_authorized(self) -> bool:
        await self.connect()
        return await self._client.is_user_authorized()

    async def log_out(self) -> None:
        try:
            await self._client.log_out()
        except Exception as e:
            raise SoroushAccountError(f"Failed to log out: {e}")

    # ==================================================================
    # User & Entity Info
    # ==================================================================

    async def get_me(self) -> Any:
        await self.connect()
        return await self._client.get_me()

    async def get_entity(self, entity: Union[str, int, Any]) -> Any:
        await self.connect()
        try:
            return await self._client.get_entity(entity)
        except Exception as e:
            raise SoroushAccountError(f"Failed to resolve entity: {e}")

    async def get_input_entity(self, entity: Union[str, int, Any]) -> Any:
        await self.connect()
        return await self._client.get_input_entity(entity)

    async def get_peer_id(self, entity: Union[str, int, Any]) -> int:
        """Get numeric peer ID (async in SPlusthon)."""
        await self.connect()
        return await self._client.get_peer_id(entity)

    async def get_full_user(self, entity: Union[str, int, Any]) -> Any:
        await self.connect()
        try:
            from splusthon.tl.functions.users import GetFullUserRequest
            user = await self._client.get_input_entity(entity)
            return await self._client(GetFullUserRequest(id=user))
        except Exception as e:
            raise SoroushAccountError(f"Failed to get full user: {e}")

    async def get_full_channel(self, entity: Union[str, int, Any]) -> Any:
        await self.connect()
        try:
            from splusthon.tl.functions.channels import GetFullChannelRequest
            peer = await self._client.get_input_entity(entity)
            return await self._client(GetFullChannelRequest(channel=peer))
        except Exception as e:
            raise SoroushAccountError(f"Failed to get full channel: {e}")

    async def get_profile_photos(self, entity: Union[str, int, Any], limit: int = 100) -> Any:
        await self.connect()
        try:
            return await self._client.get_profile_photos(entity, limit=limit)
        except Exception as e:
            raise SoroushAccountError(f"Failed to get profile photos: {e}")

    async def get_dialogs(self, limit: int = 100) -> List[Any]:
        await self.connect()
        return await self._client.get_dialogs(limit=limit)

    async def iter_dialogs(self, limit: Optional[int] = None) -> AsyncIterator[Any]:
        await self.connect()
        async for dialog in self._client.iter_dialogs(limit=limit):
            yield dialog

    async def get_participants(self, entity: Any, limit: int = 100) -> Any:
        await self.connect()
        try:
            return await self._client.get_participants(entity, limit=limit)
        except Exception as e:
            raise SoroushAccountError(f"Failed to get participants: {e}")

    async def iter_participants(self, entity: Any, limit: Optional[int] = None, **kwargs) -> AsyncIterator[Any]:
        await self.connect()
        async for p in self._client.iter_participants(entity, limit=limit, **kwargs):
            yield p

    # ==================================================================
    # Sending Messages
    # ==================================================================

    async def send_message(self, entity: Any, text: str, **kwargs) -> Any:
        await self.connect()
        try:
            return await self._client.send_message(entity, text, **kwargs)
        except Exception as e:
            raise SoroushAccountError(f"Failed to send message: {e}")

    async def send_scheduled_message(self, entity: Any, text: str, schedule_date: datetime) -> Any:
        return await self.send_message(entity, text, schedule=schedule_date)

    async def send_file(self, entity: Any, file: Union[str, bytes, BinaryIO], **kwargs) -> Any:
        await self.connect()
        try:
            return await self._client.send_file(entity, file, **kwargs)
        except Exception as e:
            raise SoroushAccountError(f"Failed to send file: {e}")

    async def send_photo(self, entity: Any, file: Union[str, BinaryIO], caption: Optional[str] = None) -> Any:
        return await self.send_file(entity, file, force_document=False, caption=caption)

    async def send_document(self, entity: Any, file: Union[str, BinaryIO], caption: Optional[str] = None) -> Any:
        return await self.send_file(entity, file, force_document=True, caption=caption)

    async def send_sticker(self, entity: Any, file: Union[str, BinaryIO]) -> Any:
        return await self.send_file(entity, file, force_document=False)

    async def send_location(self, entity: Any, latitude: float, longitude: float) -> Any:
        await self.connect()
        try:
            return await self._client.send_file(
                entity, InputMediaGeoPoint(geo_point=InputGeoPoint(lat=latitude, long=longitude))
            )
        except Exception as e:
            raise SoroushAccountError(f"Failed to send location: {e}")

    async def send_contact(self, entity: Any, phone_number: str, first_name: str, last_name: str = "") -> Any:
        await self.connect()
        try:
            return await self._client.send_file(
                entity, InputMediaContact(
                    phone_number=phone_number, first_name=first_name,
                    last_name=last_name, vcard=""
                )
            )
        except Exception as e:
            raise SoroushAccountError(f"Failed to send contact: {e}")

    async def send_poll(self, entity: Any, question: str, options: List[str], is_anonymous: bool = True, allows_multiple_answers: bool = False) -> Any:
        await self.connect()
        try:
            answers = [PollAnswer(text=opt, option=bytes([i])) for i, opt in enumerate(options)]
            poll = Poll(id=0, question=question, answers=answers, public_voters=not is_anonymous, multiple_choice=allows_multiple_answers)
            return await self._client.send_file(entity, InputMediaPoll(poll=poll))
        except Exception as e:
            raise SoroushAccountError(f"Failed to send poll: {e}")

    async def forward_messages(self, entity: Any, messages: Union[int, List[int]], from_entity: Any) -> Any:
        await self.connect()
        try:
            return await self._client.forward_messages(entity, messages, from_entity)
        except Exception as e:
            raise SoroushAccountError(f"Failed to forward messages: {e}")

    async def send_reaction(self, entity: Any, message_id: int, emoji: str) -> Any:
        await self.connect()
        try:
            from splusthon.tl.functions.messages import SendReactionRequest
            peer = await self._client.get_input_entity(entity)
            return await self._client(SendReactionRequest(peer=peer, msg_id=message_id, reaction=[ReactionEmoji(emoticon=emoji)]))
        except Exception as e:
            raise SoroushAccountError(f"Failed to send reaction: {e}")

    # ==================================================================
    # Reading Messages
    # ==================================================================

    async def get_messages(self, entity: Any, limit: int = 100, **kwargs) -> List[Any]:
        await self.connect()
        return await self._client.get_messages(entity, limit=limit, **kwargs)

    async def iter_messages(self, entity: Any, limit: Optional[int] = None, **kwargs) -> AsyncIterator[Any]:
        await self.connect()
        async for message in self._client.iter_messages(entity, limit=limit, **kwargs):
            yield message

    async def search_messages(self, entity: Any, query: str, limit: int = 100) -> List[Any]:
        return await self.get_messages(entity, limit=limit, search=query)

    async def get_messages_views(self, entity: Any, message_ids: List[int], increment: bool = False) -> Any:
        await self.connect()
        try:
            from splusthon.tl.functions.messages import GetMessagesViewsRequest
            peer = await self._client.get_input_entity(entity)
            return await self._client(GetMessagesViewsRequest(peer=peer, id=message_ids, increment=increment))
        except Exception as e:
            raise SoroushAccountError(f"Failed to get messages views: {e}")

    # ==================================================================
    # Managing Messages
    # ==================================================================

    async def edit_message(self, entity: Any, message: Any, text: str, **kwargs) -> Any:
        await self.connect()
        try:
            return await self._client.edit_message(entity, message, text, **kwargs)
        except Exception as e:
            raise SoroushAccountError(f"Failed to edit message: {e}")

    async def delete_messages(self, entity: Any, message_ids: Union[int, List[int]], revoke: bool = True) -> Any:
        await self.connect()
        try:
            return await self._client.delete_messages(entity, message_ids, revoke=revoke)
        except Exception as e:
            raise SoroushAccountError(f"Failed to delete messages: {e}")

    async def clear_history(self, entity: Any, max_id: int = 0, just_clear: bool = False, revoke: bool = True) -> Any:
        await self.connect()
        try:
            from splusthon.tl.functions.messages import DeleteHistoryRequest
            peer = await self._client.get_input_entity(entity)
            return await self._client(DeleteHistoryRequest(peer=peer, max_id=max_id, just_clear=just_clear, revoke=revoke))
        except Exception as e:
            raise SoroushAccountError(f"Failed to clear history: {e}")

    async def save_draft(self, entity: Any, text: str) -> Any:
        await self.connect()
        try:
            from splusthon.tl.functions.messages import SaveDraftRequest
            peer = await self._client.get_input_entity(entity)
            return await self._client(SaveDraftRequest(peer=peer, message=text))
        except Exception as e:
            raise SoroushAccountError(f"Failed to save draft: {e}")

    async def pin_message(self, entity: Any, message: Any, notify: bool = True) -> Any:
        await self.connect()
        try:
            return await self._client.pin_message(entity, message, notify=notify)
        except Exception as e:
            raise SoroushAccountError(f"Failed to pin message: {e}")

    async def unpin_message(self, entity: Any, message: Optional[Any] = None) -> Any:
        await self.connect()
        try:
            return await self._client.unpin_message(entity, message)
        except Exception as e:
            raise SoroushAccountError(f"Failed to unpin message: {e}")

    async def mark_as_read(self, entity: Any) -> bool:
        await self.connect()
        try:
            return await self._client.send_read_acknowledge(entity)
        except Exception as e:
            raise SoroushAccountError(f"Failed to mark as read: {e}")

    async def send_chat_action(self, entity: Any, action: str = "typing") -> Any:
        """Send a one-shot chat action (e.g. 'typing', 'upload_photo').
        Uses the raw SetTypingRequest to avoid context-manager semantics."""
        await self.connect()
        try:
            from splusthon.tl.functions.messages import SetTypingRequest
            from splusthon.tl.types import (
                SendMessageTypingAction,
                SendMessageUploadPhotoAction,
                SendMessageRecordVideoAction,
                SendMessageUploadVideoAction,
                SendMessageRecordAudioAction,
                SendMessageUploadAudioAction,
                SendMessageUploadDocumentAction,
                SendMessageGeoLocationAction,
                SendMessageChooseContactAction,
                SendMessageRecordRoundAction,
                SendMessageUploadRoundAction,
            )

            action_map = {
                "typing": SendMessageTypingAction,
                "upload_photo": SendMessageUploadPhotoAction,
                "record_video": SendMessageRecordVideoAction,
                "upload_video": SendMessageUploadVideoAction,
                "record_voice": SendMessageRecordAudioAction,
                "upload_voice": SendMessageUploadAudioAction,
                "upload_document": SendMessageUploadDocumentAction,
                "find_location": SendMessageGeoLocationAction,
                "choose_contact": SendMessageChooseContactAction,
                "record_video_note": SendMessageRecordRoundAction,
                "upload_video_note": SendMessageUploadRoundAction,
            }

            action_class = action_map.get(action, SendMessageTypingAction)
            peer = await self._client.get_input_entity(entity)
            return await self._client(SetTypingRequest(peer=peer, action=action_class()))
        except Exception as e:
            raise SoroushAccountError(f"Failed to send action: {e}")

    # ==================================================================
    # Chat & Channel Management
    # ==================================================================

    async def create_group(self, title: str, users: List[Any]) -> Any:
        await self.connect()
        try:
            return await self._client.create_group(title, users)
        except Exception as e:
            raise SoroushAccountError(f"Failed to create group: {e}")

    async def create_channel(self, title: str, about: str = "", megagroup: bool = False) -> Any:
        await self.connect()
        try:
            return await self._client.create_channel(title, about=about, megagroup=megagroup)
        except Exception as e:
            raise SoroushAccountError(f"Failed to create channel: {e}")

    async def join_chat(self, entity: Any) -> Any:
        await self.connect()
        try:
            from splusthon.tl.functions.channels import JoinChannelRequest
            return await self._client(JoinChannelRequest(entity))
        except Exception as e:
            raise SoroushAccountError(f"Failed to join chat: {e}")

    async def join_chat_invite(self, invite_hash: str) -> Any:
        await self.connect()
        try:
            from splusthon.tl.functions.messages import ImportChatInviteRequest
            return await self._client(ImportChatInviteRequest(hash=invite_hash))
        except Exception as e:
            raise SoroushAccountError(f"Failed to join chat by invite: {e}")

    async def leave_chat(self, entity: Any) -> Any:
        await self.connect()
        try:
            from splusthon.tl.functions.channels import LeaveChannelRequest
            return await self._client(LeaveChannelRequest(entity))
        except Exception as e:
            raise SoroushAccountError(f"Failed to leave chat: {e}")

    async def export_chat_invite_link(self, entity: Any) -> str:
        await self.connect()
        try:
            return await self._client.export_chat_invite_link(entity)
        except Exception as e:
            raise SoroushAccountError(f"Failed to export invite link: {e}")

    async def add_chat_user(self, chat: Any, user: Any, forward_limit: int = 100) -> Any:
        await self.connect()
        try:
            from splusthon.tl.functions.messages import AddChatUserRequest
            chat_peer = await self._client.get_input_entity(chat)
            user_peer = await self._client.get_input_entity(user)
            return await self._client(AddChatUserRequest(chat_id=chat_peer, user_id=user_peer, fwd_limit=forward_limit))
        except Exception as e:
            raise SoroushAccountError(f"Failed to add chat user: {e}")

    async def invite_to_channel(self, channel: Any, users: List[Any]) -> Any:
        await self.connect()
        try:
            from splusthon.tl.functions.channels import InviteToChannelRequest
            channel_peer = await self._client.get_input_entity(channel)
            user_peers = [await self._client.get_input_entity(u) for u in users]
            return await self._client(InviteToChannelRequest(channel=channel_peer, users=user_peers))
        except Exception as e:
            raise SoroushAccountError(f"Failed to invite to channel: {e}")

    async def get_stats(self, entity: Any, dark: bool = True) -> Any:
        await self.connect()
        try:
            try:
                from splusthon.tl.functions.stats import GetBroadcastStatsRequest
                channel = await self._client.get_input_entity(entity)
                return await self._client(GetBroadcastStatsRequest(channel=channel, dark=dark))
            except ImportError:
                return {"error": "GetBroadcastStatsRequest not supported"}
        except Exception as e:
            raise SoroushAccountError(f"Failed to get stats: {e}")

    # ==================================================================
    # Folders & Dialog Management
    # ==================================================================

    async def get_folders(self) -> Any:
        await self.connect()
        try:
            from splusthon.tl.functions.messages import GetDialogFiltersRequest
            return await self._client(GetDialogFiltersRequest())
        except Exception as e:
            raise SoroushAccountError(f"Failed to get folders: {e}")

    async def edit_folder(self, folder_id: int, title: str, **kwargs) -> Any:
        await self.connect()
        try:
            from splusthon.tl.functions.messages import UpdateDialogFilterRequest
            from splusthon.tl.types import DialogFilter
            pinned = kwargs.pop("pinned_peers", [])
            include = kwargs.pop("include_peers", [])
            exclude = kwargs.pop("exclude_peers", [])
            folder = DialogFilter(id=folder_id, title=title, pinned_peers=pinned, include_peers=include, exclude_peers=exclude, **kwargs)
            return await self._client(UpdateDialogFilterRequest(id=folder_id, filter=folder))
        except Exception as e:
            raise SoroushAccountError(f"Failed to edit folder: {e}")

    async def pin_dialog(self, entity: Any, pin: bool = True) -> Any:
        await self.connect()
        try:
            from splusthon.tl.functions.messages import ToggleDialogPinRequest
            from splusthon.tl.types import InputDialogPeer
            peer = await self._client.get_input_entity(entity)
            return await self._client(ToggleDialogPinRequest(peer=InputDialogPeer(peer=peer), pinned=pin))
        except Exception as e:
            raise SoroushAccountError(f"Failed to pin dialog: {e}")

    async def unpin_dialog(self, entity: Any) -> Any:
        return await self.pin_dialog(entity, pin=False)

    async def mute_chat(self, entity: Any, mute_until: Optional[datetime] = None) -> Any:
        await self.connect()
        try:
            from splusthon.tl.functions.account import UpdateNotifySettingsRequest
            from splusthon.tl.types import InputNotifyPeer, InputPeerNotifySettings
            peer = await self._client.get_input_entity(entity)
            if mute_until is None:
                mute_until = datetime(2038, 1, 1)
            settings = InputPeerNotifySettings(show_previews=False, silent=True, mute_until=mute_until)
            return await self._client(UpdateNotifySettingsRequest(peer=InputNotifyPeer(peer=peer), settings=settings))
        except Exception as e:
            raise SoroushAccountError(f"Failed to mute chat: {e}")

    async def unmute_chat(self, entity: Any) -> Any:
        await self.connect()
        try:
            from splusthon.tl.functions.account import UpdateNotifySettingsRequest
            from splusthon.tl.types import InputNotifyPeer, InputPeerNotifySettings
            peer = await self._client.get_input_entity(entity)
            settings = InputPeerNotifySettings(show_previews=True, silent=False, mute_until=0)
            return await self._client(UpdateNotifySettingsRequest(peer=InputNotifyPeer(peer=peer), settings=settings))
        except Exception as e:
            raise SoroushAccountError(f"Failed to unmute chat: {e}")

    async def archive_chat(self, entity: Any) -> Any:
        await self.connect()
        try:
            from splusthon.tl.functions.folders import EditPeerFoldersRequest
            from splusthon.tl.types import InputFolderPeer
            peer = await self._client.get_input_entity(entity)
            return await self._client(EditPeerFoldersRequest(folder_peers=[InputFolderPeer(peer=peer, folder_id=1)]))
        except Exception as e:
            raise SoroushAccountError(f"Failed to archive chat: {e}")

    async def unarchive_chat(self, entity: Any) -> Any:
        await self.connect()
        try:
            from splusthon.tl.functions.folders import EditPeerFoldersRequest
            from splusthon.tl.types import InputFolderPeer
            peer = await self._client.get_input_entity(entity)
            return await self._client(EditPeerFoldersRequest(folder_peers=[InputFolderPeer(peer=peer, folder_id=0)]))
        except Exception as e:
            raise SoroushAccountError(f"Failed to unarchive chat: {e}")

    # ==================================================================
    # Admin & Blocks
    # ==================================================================

    async def kick_participant(self, entity: Any, user: Any) -> Any:
        await self.connect()
        try:
            return await self._client.kick_participant(entity, user)
        except Exception as e:
            raise SoroushAccountError(f"Failed to kick participant: {e}")

    async def edit_admin(self, entity: Any, user: Any, **kwargs) -> Any:
        await self.connect()
        try:
            from splusthon.tl.functions.channels import EditAdminRequest
            rights = ChatAdminRights(**kwargs)
            peer = await self._client.get_input_entity(entity)
            user_peer = await self._client.get_input_entity(user)
            return await self._client(EditAdminRequest(channel=peer, user_id=user_peer, admin_rights=rights, rank=""))
        except Exception as e:
            raise SoroushAccountError(f"Failed to edit admin: {e}")

    async def block_user(self, user: Any) -> bool:
        await self.connect()
        try:
            from splusthon.tl.functions.contacts import BlockRequest
            peer = await self._client.get_input_entity(user)
            await self._client(BlockRequest(id=peer))
            return True
        except Exception as e:
            raise SoroushAccountError(f"Failed to block user: {e}")

    async def unblock_user(self, user: Any) -> bool:
        await self.connect()
        try:
            from splusthon.tl.functions.contacts import UnblockRequest
            peer = await self._client.get_input_entity(user)
            await self._client(UnblockRequest(id=peer))
            return True
        except Exception as e:
            raise SoroushAccountError(f"Failed to unblock user: {e}")

    # ==================================================================
    # Profile
    # ==================================================================

    async def update_profile(self, first_name: Optional[str] = None, last_name: Optional[str] = None, about: Optional[str] = None) -> bool:
        await self.connect()
        try:
            from splusthon.tl.functions.account import UpdateProfileRequest
            await self._client(UpdateProfileRequest(first_name=first_name, last_name=last_name, about=about))
            return True
        except Exception as e:
            raise SoroushAccountError(f"Failed to update profile: {e}")

    async def update_username(self, username: str) -> bool:
        await self.connect()
        try:
            from splusthon.tl.functions.account import UpdateUsernameRequest
            await self._client(UpdateUsernameRequest(username=username))
            return True
        except Exception as e:
            raise SoroushAccountError(f"Failed to update username: {e}")

    async def set_profile_photo(self, file: Union[str, BinaryIO]) -> Any:
        await self.connect()
        try:
            from splusthon.tl.functions.photos import UploadProfilePhotoRequest
            uploaded = await self._client.upload_file(file)
            return await self._client(UploadProfilePhotoRequest(file=uploaded))
        except Exception as e:
            raise SoroushAccountError(f"Failed to set profile photo: {e}")

    async def delete_profile_photos(self, photos: List[Any]) -> Any:
        await self.connect()
        try:
            from splusthon.tl.functions.photos import DeletePhotosRequest
            return await self._client(DeletePhotosRequest(id=photos))
        except Exception as e:
            raise SoroushAccountError(f"Failed to delete profile photos: {e}")

    # ==================================================================
    # Media Download
    # ==================================================================

    async def download_media(self, message_or_media: Any, file: Optional[str] = None, **kwargs) -> Optional[str]:
        await self.connect()
        try:
            return await self._client.download_media(message_or_media, file=file, **kwargs)
        except Exception as e:
            raise SoroushAccountError(f"Failed to download media: {e}")

    async def download_profile_photo(self, entity: Any, file: Optional[str] = None) -> Optional[str]:
        await self.connect()
        try:
            return await self._client.download_profile_photo(entity, file=file)
        except Exception as e:
            raise SoroushAccountError(f"Failed to download profile photo: {e}")

    # ==================================================================
    # Events
    # ==================================================================

    def _register_handler(self, event_filter: Any, user_func: Callable, pass_event: bool = False) -> Callable:
        async def async_wrapper(event_obj):
            arg = event_obj if pass_event else event_obj.message
            result = user_func(arg)
            if asyncio.iscoroutine(result):
                await result
        self._client.add_event_handler(async_wrapper, event_filter)
        return user_func

    def on_message(self, pattern: Optional[str] = None, chats: Any = None, from_users: Any = None) -> Callable:
        def decorator(func: Callable) -> Callable:
            return self._register_handler(events.NewMessage(pattern=pattern, chats=chats, from_users=from_users), func, False)
        return decorator

    def on_edited_message(self, chats: Any = None) -> Callable:
        def decorator(func: Callable) -> Callable:
            return self._register_handler(events.MessageEdited(chats=chats), func, False)
        return decorator

    def on_deleted_message(self, chats: Any = None) -> Callable:
        def decorator(func: Callable) -> Callable:
            return self._register_handler(events.MessageDeleted(chats=chats), func, True)
        return decorator

    def on_callback(self) -> Callable:
        def decorator(func: Callable) -> Callable:
            return self._register_handler(events.CallbackQuery(), func, True)
        return decorator

    def on_user_update(self) -> Callable:
        def decorator(func: Callable) -> Callable:
            return self._register_handler(events.UserUpdate(), func, True)
        return decorator

    def on_chat_action(self, chats: Any = None) -> Callable:
        def decorator(func: Callable) -> Callable:
            return self._register_handler(events.ChatAction(chats=chats), func, True)
        return decorator

    def on_message_read(self, chats: Any = None) -> Callable:
        def decorator(func: Callable) -> Callable:
            return self._register_handler(events.MessageRead(chats=chats), func, True)
        return decorator

    def on_album(self, chats: Any = None) -> Callable:
        def decorator(func: Callable) -> Callable:
            return self._register_handler(events.Album(chats=chats), func, True)
        return decorator

    def on_raw(self) -> Callable:
        def decorator(func: Callable) -> Callable:
            return self._register_handler(events.Raw(), func, True)
        return decorator
