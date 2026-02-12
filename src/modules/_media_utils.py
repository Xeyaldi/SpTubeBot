import re
from typing import Optional, Union, TYPE_CHECKING

from pytdbot import types, Client
from pytdbot.types import Error, InputFileLocal, InputFileRemote, FormattedText

from src.utils import ApiData, Download, db

if TYPE_CHECKING:
    from src.utils._dataclass import TrackResponse


async def process_track_media(c: Client, track: 'TrackResponse', chat_id: Optional[int] = None,
                              message_id: Optional[int] = None, inline_message_id: Optional[str] = None) -> Error | \
                                                                                                            tuple[
                                                                                                                InputFileRemote, str | None, FormattedText] | \
                                                                                                            tuple[
                                                                                                                InputFileRemote, str | None, None] | \
                                                                                                            tuple[
                                                                                                                InputFileRemote | InputFileLocal, str | None]:
    # Tərcümə: Musiqiniz emal olunur, zəhmət olmasa gözləyin...
    parsed_status = await c.parseTextEntities("<b>Musiqiniz emal olunur, zəhmət olmasa gözləyin...</b>", types.TextParseModeHTML())
    text = types.InputMessageText(parsed_status)
    
    # Update status message
    if inline_message_id:
        await c.editInlineMessageText(inline_message_id=inline_message_id, input_message_content=text)
    elif chat_id and message_id:
        await c.editMessageText(chat_id=chat_id, message_id=message_id, input_message_content=text)

    api = ApiData(track.url)
    if track.platform.lower() == "spotify":
        _track = await api.spotify()
        if isinstance(_track, types.Error):
            # Tərcümə: Yükləmə uğursuz oldu.
            error_msg = f"Yükləmə uğursuz oldu.\n<b>{_track.message}</b>"
            return types.Error(message=error_msg)

        dl = Download(_track)
        result = await dl.process()
        if isinstance(result, types.Error):
            # Tərcümə: ❌ Yükləmə baş tutmadı.
            error_msg = f"❌ Yükləmə baş tutmadı.\n<b>{result.message}</b>"
            return types.Error(message=error_msg)

        audio_file, cover = result
        if not audio_file:
            # Tərcümə: Mahnını yükləmək mümkün olmadı. Zəhmət olmasa, bu barədə @FallenProjects ünvanına məlumat verin.
            return types.Error(message="Mahnını yükləmək mümkün olmadı.\nZəhmət olmasa, bu barədə @FallenProjects ünvanına məlumat verin.")

        file_id = await db.upload_song_and_get_file_id(audio_file, cover, _track)
        if isinstance(file_id, types.Error):
            # Tərcümə: ❌ Mahnını bazaya göndərmək mümkün olmadı.
            return types.Error(message=file_id.message or "❌ Mahnını bazaya göndərmək mümkün olmadı.")

        if isinstance(file_id, tuple):
            file_id, caption = file_id
            audio = types.InputFileRemote(file_id)
            return audio, cover, caption

        audio = types.InputFileRemote(file_id[0])
        return audio, cover, None

    dl = Download(track)
    result = await dl.process()
    if isinstance(result, types.Error):
        # Tərcümə: ❌ Yükləmə baş tutmadı.
        error_msg = f"❌ Yükləmə baş tutmadı.\n<b>{result.message}</b>"
        return types.Error(message=error_msg)

    audio_file, cover = result
    if not audio_file:
        # Tərcümə: ❌ Mahnını yükləmək mümkün olmadı.
        error_msg = "❌ Mahnını yükləmək mümkün olmadı.\nZəhmət olmasa, bu barədə @FallenProjects ünvanına məlumat verin."
        return types.Error(message=error_msg)

    if re.match(r"https?://t\.me/([^/]+)/(\d+)", audio_file):
        info = await c.getMessageLinkInfo(audio_file)
        if isinstance(info, types.Error) or not info.message:
            # Tərcümə: ❌ Link həll edilə bilmədi:
            return types.Error(message=f"❌ Link həll edilə bilmədi: {audio_file}")

        public_msg = await c.getMessage(info.chat_id, info.message.id)
        if isinstance(public_msg, types.Error):
            # Tərcümə: ❌ Mesajı əldə etmək mümkün olmadı:
            return types.Error(message=f"❌ Mesajı əldə etmək mümkün olmadı: {public_msg.message}")

        if isinstance(public_msg.content, types.MessageAudio):
            audio = types.InputFileRemote(public_msg.content.audio.audio.remote.id)
        elif isinstance(public_msg.content, types.MessageDocument):
            audio = types.InputFileRemote(public_msg.content.document.document.remote.id)
        elif isinstance(public_msg.content, types.MessageVideo):
            audio = types.InputFileRemote(public_msg.content.video.video.remote.id)
        else:
            # Tərcümə: Linkdə səs faylı tapılmadı:
            return types.Error(message=f"Linkdə səs faylı tapılmadı: {audio_file}")
    else:
        audio = types.InputFileLocal(audio_file)

    return audio, cover, None


def get_reply_markup(track_name: str, artist: str) -> types.ReplyMarkupInlineKeyboard:
    """Generate a reply markup with the track name and update button."""
    return types.ReplyMarkupInlineKeyboard(
        [
            [
                types.InlineKeyboardButton(
                    text=track_name,
                    type=types.InlineKeyboardButtonTypeSwitchInline(
                        query=artist,
                        target_chat=types.TargetChatCurrent()
                    )
                )
            ],
            [
                types.InlineKeyboardButton(
                    # Tərcümə: Yeniləmələr
                    text="Yeniləmələr",
                    type=types.InlineKeyboardButtonTypeUrl("https://t.me/ht_bots"),
                )
            ]
        ]
    )
