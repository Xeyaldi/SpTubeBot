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
    # "Processing your track..." -> "ᴍᴀʜɴı ʜᴀᴢıʀʟᴀɴıʀ, ᴢəʜᴍəᴛ ᴏʟᴍᴀsᴀ ɢöᴢʟəʏɪɴ..."
    parsed_status = await c.parseTextEntities("<b>⏳ ᴍᴀʜɴı ʜᴀᴢıʀʟᴀɴıʀ, ᴢəʜᴍəᴛ ᴏʟᴍᴀsᴀ ɢöᴢʟəʏɪɴ...</b>", types.TextParseModeHTML())
    text = types.InputMessageText(parsed_status)
    
    if inline_message_id:
        await c.editInlineMessageText(inline_message_id=inline_message_id, input_message_content=text)
    elif chat_id and message_id:
        await c.editMessageText(chat_id=chat_id, message_id=message_id, input_message_content=text)

    api = ApiData(track.url)
    if track.platform.lower() == "spotify":
        _track = await api.spotify()
        if isinstance(_track, types.Error):
            error_msg = f"📥 ʏüᴋʟəᴍə ʙᴀş ᴛᴜᴛᴍᴀᴅı.\n<b>{_track.message}</b>"
            return types.Error(message=error_msg)

        dl = Download(_track)
        result = await dl.process()
        if isinstance(result, types.Error):
            error_msg = f"❌ ʏüᴋʟəᴍə xəᴛᴀsı.\n<b>{result.message}</b>"
            return types.Error(message=error_msg)

        audio_file, cover = result
        if not audio_file:
            return types.Error(message="⚠️ ᴍᴀʜɴı ʏüᴋʟəɴə ʙɪʟᴍəᴅɪ.\nᴢəʜᴍəᴛ ᴏʟᴍᴀsᴀ, ʀəsᴍɪ ᴋᴀɴᴀʟᴀ ʙɪʟᴅɪʀɪɴ.")

        file_id = await db.upload_song_and_get_file_id(audio_file, cover, _track)
        if isinstance(file_id, types.Error):
            return types.Error(message=file_id.message or "❌ ᴍᴀʟᴜᴍᴀᴛ ʙᴀᴢᴀsı ɪʟə əʟᴀǫə ᴋəsɪʟᴅɪ.")

        if isinstance(file_id, tuple):
            file_id, caption = file_id
            audio = types.InputFileRemote(file_id)
            return audio, cover, caption

        audio = types.InputFileRemote(file_id[0])
        return audio, cover, None

    dl = Download(track)
    result = await dl.process()
    if isinstance(result, types.Error):
        error_msg = f"❌ ʏüᴋʟəᴍə xəᴛᴀsı.\n<b>{result.message}</b>"
        return types.Error(message=error_msg)

    audio_file, cover = result
    if not audio_file:
        error_msg = "❌ ᴍᴀʜɴı ʏüᴋʟəɴə ʙɪʟᴍəᴅɪ.\nᴢəʜᴍəᴛ ᴏʟᴍᴀsᴀ, ʀəsᴍɪ ᴋᴀɴᴀʟᴀ ʙɪʟᴅɪʀɪɴ."
        return types.Error(message=error_msg)

    if re.match(r"https?://t\.me/([^/]+)/(\d+)", audio_file):
        info = await c.getMessageLinkInfo(audio_file)
        if isinstance(info, types.Error) or not info.message:
            return types.Error(message=f"❌ ʟɪɴᴋ ᴀçıʟᴍᴀᴅı: {audio_file}")

        public_msg = await c.getMessage(info.chat_id, info.message.id)
        if isinstance(public_msg, types.Error):
            return types.Error(message=f"❌ ᴍᴇsᴀᴊ ᴀʟıɴᴍᴀᴅı: {public_msg.message}")

        if isinstance(public_msg.content, types.MessageAudio):
            audio = types.InputFileRemote(public_msg.content.audio.audio.remote.id)
        elif isinstance(public_msg.content, types.MessageDocument):
            audio = types.InputFileRemote(public_msg.content.document.document.remote.id)
        elif isinstance(public_msg.content, types.MessageVideo):
            audio = types.InputFileRemote(public_msg.content.video.video.remote.id)
        else:
            return types.Error(message=f"ʟɪɴᴋdə səs ғᴀʏʟı ʏᴏxᴅᴜʀ: {audio_file}")
    else:
        audio = types.InputFileLocal(audio_file)

    return audio, cover, None


def get_reply_markup(track_name: str, artist: str) -> types.ReplyMarkupInlineKeyboard:
    """Mahnı göndəriləndə altındakı düymələr"""
    return types.ReplyMarkupInlineKeyboard(
        [
            [
                types.InlineKeyboardButton(
                    text=f"🎧 {track_name}",
                    type=types.InlineKeyboardButtonTypeSwitchInline(
                        query=artist,
                        target_chat=types.TargetChatCurrent()
                    )
                )
            ],
            [
                # "Update" düyməsini "Məlumat Kanalı" düyməsi ilə əvəz etdim
                types.InlineKeyboardButton(
                    text="📢 ᴍəʟᴜᴍᴀᴛ ᴋᴀɴᴀʟı",
                    type=types.InlineKeyboardButtonTypeUrl("https://t.me/SƏNİN_KANAL_LİNKİN"),
                )
            ]
        ]
    )
    
