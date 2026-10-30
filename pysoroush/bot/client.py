"""
Synchronous client for the Soroush Plus Bot API.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional, Union, List

import requests

from .base_client import BaseClient
from .exceptions import (
    RateLimitError, SoroushAPIError, SoroushNetworkError,
    SoroushServerError, raise_for_error,
)
from .types import (
    User, Message, MessageEntity, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply,
    Update, WebhookInfo, InputFile, File, UserProfilePhotos,
    BotCommand, BotCommandScopeDefault, BotCommandScopeAllPrivateChats, BotCommandScopeChat
)


class Client(BaseClient):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.session = requests.Session()

    def request(
        self, method: str, data: Optional[Dict[str, Any]] = None, files: Optional[Dict[str, Any]] = None
    ) -> Any:
        url = self._get_method_url(method)
        attempt = 0

        while attempt <= self.retries:
            try:
                self._debug_log(f"POST {url} (attempt {attempt + 1})")
                response = self.session.post(url, data=data, files=files, timeout=self.timeout)

                if response.status_code >= 500:
                    raise SoroushServerError(response.status_code, response.text[:200])

                try:
                    json_data = response.json()
                except ValueError:
                    raise SoroushAPIError(f"Invalid JSON: {response.text[:100]}", response.status_code)

                self._debug_log(f"Response: {json_data}")
                raise_for_error(json_data)
                return json_data.get("result")

            except SoroushServerError as e:
                if attempt >= self.retries: raise
                time.sleep(self._get_retry_delay(attempt))
            except RateLimitError as e:
                if attempt >= self.retries: raise
                time.sleep(e.retry_after)
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                if attempt >= self.retries: raise SoroushNetworkError(f"Network error: {e}")
                time.sleep(self._get_retry_delay(attempt))

            attempt += 1
        raise SoroushNetworkError("Maximum retries exceeded.")

    def get_me(self) -> User:
        return User.from_dict(self.request("getMe"))

    def send_message(
        self, chat_id: Union[int, str], text: str, parse_mode: Optional[str] = None,
        entities: Optional[List[MessageEntity]] = None, disable_web_page_preview: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None, allow_sending_without_reply: Optional[bool] = None,
        reply_markup: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]] = None,
    ) -> Message:
        payload = self._build_payload(
            chat_id=chat_id, text=text, parse_mode=parse_mode, entities=entities,
            disable_web_page_preview=disable_web_page_preview,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply, reply_markup=reply_markup,
        )
        return Message.from_dict(self.request("sendMessage", data=payload))

    def send_photo(
        self, chat_id: Union[int, str], photo: Union[str, InputFile], caption: Optional[str] = None,
        parse_mode: Optional[str] = None, caption_entities: Optional[List[MessageEntity]] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Message:
        payload, files, opened = self._prepare_media_and_files(
            chat_id=chat_id, photo=photo, caption=caption, parse_mode=parse_mode,
            caption_entities=caption_entities, reply_markup=reply_markup,
        )
        try:
            return Message.from_dict(self.request("sendPhoto", data=payload, files=files))
        finally:
            for f in opened: f.close()

    def send_document(
        self, chat_id: Union[int, str], document: Union[str, InputFile], thumb: Optional[Union[str, InputFile]] = None,
        caption: Optional[str] = None, parse_mode: Optional[str] = None, caption_entities: Optional[List[MessageEntity]] = None,
        disable_content_type_detection: Optional[bool] = None, reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Message:
        payload, files, opened = self._prepare_media_and_files(
            chat_id=chat_id, document=document, thumb=thumb, caption=caption, parse_mode=parse_mode,
            caption_entities=caption_entities, disable_content_type_detection=disable_content_type_detection,
            reply_markup=reply_markup,
        )
        try:
            return Message.from_dict(self.request("sendDocument", data=payload, files=files))
        finally:
            for f in opened: f.close()

    def send_audio(
        self, chat_id: Union[int, str], audio: Union[str, InputFile], caption: Optional[str] = None,
        parse_mode: Optional[str] = None, caption_entities: Optional[List[MessageEntity]] = None,
        duration: Optional[int] = None, performer: Optional[str] = None, title: Optional[str] = None,
        thumb: Optional[Union[str, InputFile]] = None, reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Message:
        payload, files, opened = self._prepare_media_and_files(
            chat_id=chat_id, audio=audio, caption=caption, parse_mode=parse_mode, caption_entities=caption_entities,
            duration=duration, performer=performer, title=title, thumb=thumb, reply_markup=reply_markup,
        )
        try:
            return Message.from_dict(self.request("sendAudio", data=payload, files=files))
        finally:
            for f in opened: f.close()

    def send_video(
        self, chat_id: Union[int, str], video: Union[str, InputFile], duration: Optional[int] = None,
        width: Optional[int] = None, height: Optional[int] = None, thumb: Optional[Union[str, InputFile]] = None,
        caption: Optional[str] = None, parse_mode: Optional[str] = None, caption_entities: Optional[List[MessageEntity]] = None,
        supports_streaming: Optional[bool] = None, reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Message:
        payload, files, opened = self._prepare_media_and_files(
            chat_id=chat_id, video=video, duration=duration, width=width, height=height, thumb=thumb,
            caption=caption, parse_mode=parse_mode, caption_entities=caption_entities,
            supports_streaming=supports_streaming, reply_markup=reply_markup,
        )
        try:
            return Message.from_dict(self.request("sendVideo", data=payload, files=files))
        finally:
            for f in opened: f.close()

    def send_animation(
        self, chat_id: Union[int, str], animation: Union[str, InputFile], duration: Optional[int] = None,
        width: Optional[int] = None, height: Optional[int] = None, thumb: Optional[Union[str, InputFile]] = None,
        caption: Optional[str] = None, parse_mode: Optional[str] = None, caption_entities: Optional[List[MessageEntity]] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Message:
        payload, files, opened = self._prepare_media_and_files(
            chat_id=chat_id, animation=animation, duration=duration, width=width, height=height, thumb=thumb,
            caption=caption, parse_mode=parse_mode, caption_entities=caption_entities, reply_markup=reply_markup,
        )
        try:
            return Message.from_dict(self.request("sendAnimation", data=payload, files=files))
        finally:
            for f in opened: f.close()

    def send_voice(
        self, chat_id: Union[int, str], voice: Union[str, InputFile], caption: Optional[str] = None,
        parse_mode: Optional[str] = None, caption_entities: Optional[List[MessageEntity]] = None,
        duration: Optional[int] = None, reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Message:
        payload, files, opened = self._prepare_media_and_files(
            chat_id=chat_id, voice=voice, caption=caption, parse_mode=parse_mode,
            caption_entities=caption_entities, duration=duration, reply_markup=reply_markup,
        )
        try:
            return Message.from_dict(self.request("sendVoice", data=payload, files=files))
        finally:
            for f in opened: f.close()

    def send_video_note(
        self, chat_id: Union[int, str], video_note: Union[str, InputFile], duration: Optional[int] = None,
        length: Optional[int] = None, thumb: Optional[Union[str, InputFile]] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Message:
        payload, files, opened = self._prepare_media_and_files(
            chat_id=chat_id, video_note=video_note, duration=duration, length=length,
            thumb=thumb, reply_markup=reply_markup,
        )
        try:
            return Message.from_dict(self.request("sendVideoNote", data=payload, files=files))
        finally:
            for f in opened: f.close()

    def send_sticker(
        self, chat_id: Union[int, str], sticker: Union[str, InputFile],
        reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Message:
        payload, files, opened = self._prepare_media_and_files(
            chat_id=chat_id, sticker=sticker, reply_markup=reply_markup,
        )
        try:
            return Message.from_dict(self.request("sendSticker", data=payload, files=files))
        finally:
            for f in opened: f.close()

    def send_location(
        self, chat_id: Union[int, str], latitude: float, longitude: float,
        horizontal_accuracy: Optional[float] = None, reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Message:
        payload = self._build_payload(
            chat_id=chat_id, latitude=latitude, longitude=longitude,
            horizontal_accuracy=horizontal_accuracy, reply_markup=reply_markup,
        )
        return Message.from_dict(self.request("sendLocation", data=payload))

    def send_contact(
        self, chat_id: Union[int, str], phone_number: str, first_name: str,
        last_name: Optional[str] = None, vcard: Optional[str] = None, reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Message:
        payload = self._build_payload(
            chat_id=chat_id, phone_number=phone_number, first_name=first_name,
            last_name=last_name, vcard=vcard, reply_markup=reply_markup,
        )
        return Message.from_dict(self.request("sendContact", data=payload))

    def edit_message_text(
        self, text: str, chat_id: Optional[Union[int, str]] = None, message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None, parse_mode: Optional[str] = None,
        entities: Optional[List[MessageEntity]] = None, disable_web_page_preview: Optional[bool] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Union[Message, bool]:
        payload = self._build_payload(
            text=text, chat_id=chat_id, message_id=message_id, inline_message_id=inline_message_id,
            parse_mode=parse_mode, entities=entities, disable_web_page_preview=disable_web_page_preview,
            reply_markup=reply_markup,
        )
        result = self.request("editMessageText", data=payload)
        return Message.from_dict(result) if isinstance(result, dict) else bool(result)

    def edit_message_caption(
        self, chat_id: Optional[Union[int, str]] = None, message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None, caption: Optional[str] = None,
        parse_mode: Optional[str] = None, caption_entities: Optional[List[MessageEntity]] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Union[Message, bool]:
        payload = self._build_payload(
            chat_id=chat_id, message_id=message_id, inline_message_id=inline_message_id,
            caption=caption, parse_mode=parse_mode, caption_entities=caption_entities, reply_markup=reply_markup,
        )
        result = self.request("editMessageCaption", data=payload)
        return Message.from_dict(result) if isinstance(result, dict) else bool(result)

    def edit_message_reply_markup(
        self, chat_id: Optional[Union[int, str]] = None, message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None, reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Union[Message, bool]:
        payload = self._build_payload(
            chat_id=chat_id, message_id=message_id, inline_message_id=inline_message_id, reply_markup=reply_markup,
        )
        result = self.request("editMessageReplyMarkup", data=payload)
        return Message.from_dict(result) if isinstance(result, dict) else bool(result)

    def delete_message(self, chat_id: Union[int, str], message_id: int) -> bool:
        payload = self._build_payload(chat_id=chat_id, message_id=message_id)
        return bool(self.request("deleteMessage", data=payload))

    def answer_callback_query(
        self, callback_query_id: str, text: Optional[str] = None, show_alert: Optional[bool] = None,
        url: Optional[str] = None, cache_time: Optional[int] = None,
    ) -> bool:
        payload = self._build_payload(
            callback_query_id=callback_query_id, text=text, show_alert=show_alert, url=url, cache_time=cache_time,
        )
        return bool(self.request("answerCallbackQuery", data=payload))

    def set_my_commands(
        self, commands: List[BotCommand],
        scope: Optional[Union[BotCommandScopeDefault, BotCommandScopeAllPrivateChats, BotCommandScopeChat]] = None,
        language_code: Optional[str] = None,
    ) -> bool:
        payload = self._build_payload(commands=commands, scope=scope, language_code=language_code)
        return bool(self.request("setMyCommands", data=payload))

    def delete_my_commands(
        self, scope: Optional[Union[BotCommandScopeDefault, BotCommandScopeAllPrivateChats, BotCommandScopeChat]] = None,
        language_code: Optional[str] = None,
    ) -> bool:
        payload = self._build_payload(scope=scope, language_code=language_code)
        return bool(self.request("deleteMyCommands", data=payload))

    def get_my_commands(
        self, scope: Optional[Union[BotCommandScopeDefault, BotCommandScopeAllPrivateChats, BotCommandScopeChat]] = None,
        language_code: Optional[str] = None,
    ) -> List[BotCommand]:
        payload = self._build_payload(scope=scope, language_code=language_code)
        result = self.request("getMyCommands", data=payload)
        return [BotCommand.from_dict(c) for c in result]

    def get_file(self, file_id: str) -> File:
        return File.from_dict(self.request("getFile", data=self._build_payload(file_id=file_id)))

    def get_user_profile_photos(self, user_id: int, offset: Optional[int] = None, limit: Optional[int] = None) -> UserProfilePhotos:
        payload = self._build_payload(user_id=user_id, offset=offset, limit=limit)
        return UserProfilePhotos.from_dict(self.request("getUserProfilePhotos", data=payload))

    def get_updates(
        self, offset: Optional[int] = None, limit: Optional[int] = None,
        timeout: Optional[int] = None, allowed_updates: Optional[List[str]] = None,
    ) -> List[Update]:
        payload = self._build_payload(offset=offset, limit=limit, timeout=timeout, allowed_updates=allowed_updates)
        return [Update.from_dict(u) for u in self.request("getUpdates", data=payload)]

    def set_webhook(
        self, url: str, certificate: Optional[Any] = None, ip_address: Optional[str] = None,
        max_connections: Optional[int] = None, allowed_updates: Optional[List[str]] = None, drop_pending_updates: Optional[bool] = None,
    ) -> bool:
        payload = self._build_payload(
            url=url, ip_address=ip_address, max_connections=max_connections,
            allowed_updates=allowed_updates, drop_pending_updates=drop_pending_updates,
        )
        files = {"certificate": certificate} if certificate else None
        return bool(self.request("setWebhook", data=payload, files=files))

    def delete_webhook(self, drop_pending_updates: Optional[bool] = None) -> bool:
        payload = self._build_payload(drop_pending_updates=drop_pending_updates)
        return bool(self.request("deleteWebhook", data=payload))

    def get_webhook_info(self) -> WebhookInfo:
        return WebhookInfo.from_dict(self.request("getWebhookInfo"))

    def send_media_group(self, chat_id: Union[int, str], media: List[Any]) -> List[Message]:
        """Use this method to send a group of photos, videos, documents or audios as an album."""
        media_dicts, files, opened = self._prepare_media_group(media)
        payload = self._build_payload(chat_id=chat_id, media=media_dicts)
        try:
            result = self.request("sendMediaGroup", data=payload, files=files)
            return [Message.from_dict(m) for m in result]
        finally:
            for f in opened: f.close()
