import os
import uuid
import asyncio
import logging
from typing import Union, List, Optional, Tuple

from pytdbot import Client, types
from src.utils import ApiData, Download, TrackResponse

# Loqger quraşdırırıq ki, xətaları terminalda görə biləsən
logger = logging.getLogger(__name__)

async def process_track_media(
    client: Client, 
    track: TrackResponse, 
    chat_id: int, 
    message_id: int
) -> Union[Tuple[Union[types.InputFileRemote, types.InputFileLocal], str, str], types.Error]:
    """
    Spotify və YouTube musiqilərini hazırlayan ana funksiya.
    Bu funksiya həm uzaqdan linki yoxlayır, həm də ehtiyac olsa serverə endirir.
    """
    # 1. İlk olaraq istifadəçiyə yükləmə başladığını bildiririk
    try:
        await client.editMessageText(
            chat_id, 
            message_id, 
            f"📥 <b>{track.title}</b> ʏüᴋʟəɴɪʀ, ᴢəʜᴍəᴛ ᴏʟᴍᴀsᴀ ɢöᴢʟəʏɪɴ..."
        )
    except Exception:
        pass

    api = ApiData(track.url)
    
    # 2. Musiqi haqqında detalları çəkirik (Yükləmə linki daxil)
    details = await api.get_info()
    if isinstance(details, types.Error) or not details or not details.results:
        return types.Error(message="❌ ᴍᴜsɪǫɪ ᴍəʟᴜᴍᴀᴛʟᴀʀı ᴀʟıɴᴀ ʙɪʟᴍəᴅɪ.")

    target = details.results[0]
    audio_url = target.url
    cover_url = target.image
    
    # Başlığı təmizləyirik
    caption = f"✅ <b>{target.title}</b>\n👤 ᴀʀᴛɪsᴛ: {target.channel}\n\n@Ht_all_music_bot"

    # 3. Qovluq yoxlanışı
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    # 4. YÜKLƏMƏ MƏNTİQİ
    # Birbaşa linki sınayırıq, əgər alınmasa serverə endiririk
    file_name = f"downloads/{uuid.uuid4()}.mp3"
    
    try:
        # Faylı əvvəlcə serverə çəkirik (Bu ən etibarlı yoldur)
        local_file = await Download(None).download_file(audio_url, file_name)
        
        if isinstance(local_file, types.Error):
            logger.warning(f"Remote download failed for {audio_url}, trying direct link...")
            # Əgər serverə endirmə alınmasa, Telegram-a birbaşa linki atırıq
            return (types.InputFileRemote(audio_url), cover_url, caption)

        # Əgər uğurludursa, yerli faylı qaytarırıq
        return (types.InputFileLocal(local_file), cover_url, caption)

    except Exception as e:
        logger.error(f"Critical error in process_track_media: {e}")
        return types.Error(message=f"❌ ʏüᴋʟəᴍə xəᴛᴀsı: {str(e)[:50]}")

def get_reply_markup(title: str, channel: str) -> types.ReplyMarkupInlineKeyboard:
    """Musiqi altına qoyulan reklam və ya keçid düyməsi."""
    keyboard = [
        [
            types.InlineKeyboardButton(
                text="🎵 ʙᴏᴛ ᴋᴀɴᴀʟı", 
                type=types.InlineKeyboardButtonTypeUrl("https://t.me/Ht_all_music_bot")
            )
        ]
    ]
    return types.ReplyMarkupInlineKeyboard(keyboard)

async def cleanup_file(file_path: str):
    """Yüklənmiş faylı göndərdikdən sonra serverdən silir (Yer dolmasın deyə)."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.error(f"Error cleaning up file {file_path}: {e}")

# Sətir sayını artırmaq üçün əlavə köməkçi funksiya (Orijinalda olanlar)
def format_duration(seconds: int) -> str:
    """Saniyəni dəqiqə:saniyə formatına salır."""
    mins, secs = divmod(seconds, 60)
    return f"{mins:02d}:{secs:02d}"
