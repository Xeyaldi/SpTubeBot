from pytdbot import Client, types
from pytdbot.exception import StopHandlers

from src.utils import ApiData, shortener, Filter
from ._fsub import fsub


async def process_spotify_query(message: types.Message, query: str):
    # Botun reaksiya verdiyini görmək üçün ilk mesaj
    response = await message.reply_text("⏳ ᴍəʟᴜᴍᴀᴛʟᴀʀ ᴇᴍᴀʟ ᴏʟᴜɴᴜʀ...")
    if isinstance(response, types.Error):
        return

    api = ApiData(query)

    try:
        # 1. Yoxlayırıq: Bu hər hansı bir sosial media linkidirmi? 
        # (TikTok, Instagram, FB, Pinterest, Twitter, Reddit və s.)
        if api.is_save_snap_url():
            snap_data = await api.get_snap()
            
            if snap_data and not isinstance(snap_data, types.Error):
                # Video tapılarsa
                if snap_data.videos:
                    await message.reply_video(snap_data.videos[0].url, caption="✅ ᴜğᴜʀʟᴀ ʏüᴋʟəɴᴅɪ.")
                    await response.delete()
                    return
                # Şəkil tapılarsa (Pinterest/Insta post)
                elif snap_data.images:
                    await message.reply_photo(snap_data.images[0], caption="✅ ᴜğᴜʀʟᴀ ʏüᴋʟəɴᴅɪ.")
                    await response.delete()
                    return
            
            await response.edit_text("❌ ʙᴜ ʟɪɴᴋ üzʀə ᴍᴇᴅɪᴀ ᴛᴀᴘıʟᴍᴀᴅı.")
            return

        # 2. Əgər sosial media deyilsə, Musiqi/Spotify axtarışına keç
        song_data = await api.get_info() if api.is_valid() else await api.search(limit="5")
        
        if isinstance(song_data, types.Error) or not song_data or not song_data.results:
            await response.edit_text("❌ ɴəᴛɪᴄə ᴛᴀᴘıʟᴍᴀᴅı.")
            return

        keyboard = [
            [types.InlineKeyboardButton(
                text=f"{track.title} - {track.channel}",
                type=types.InlineKeyboardButtonTypeCallback(
                    f"spot_{shortener.encode_url(track.url)}_0".encode()
                )
            )]
            for track in song_data.results
        ]

        await response.edit_text(
            f"🔎 ᴀxᴛᴀʀış ɴəᴛɪᴄəsɪ: <b>{query}</b>\n\nᴢəʜᴍəᴛ ᴏʟᴍᴀsᴀ, ʏüᴋʟəᴍəᴋ ɪsᴛəᴅɪʏɪɴɪᴢ ᴍᴀʜɴıɴıɴ üzəʀɪɴə ᴛᴏxᴜɴᴜɴ.",
            parse_mode="html",
            disable_web_page_preview=True,
            reply_markup=types.ReplyMarkupInlineKeyboard(keyboard),
        )

    except Exception as e:
        # Hər hansı texniki xəta olsa bot susmasın
        await response.edit_text(f"❌ xəᴛᴀ: ᴍᴇᴅɪᴀ ᴇᴍᴀʟ ᴏʟᴜɴᴀ ʙɪʟᴍəᴅɪ.")


@Client.on_message(filters=Filter.command(["spot", "spotify", "song"]))
@fsub
async def spotify_cmd(_: Client, message: types.Message):
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        await message.reply_text("🔎 ᴢəʜᴍəᴛ ᴏʟᴍᴀsᴀ, ᴀxᴛᴀʀış sᴏʀğᴜsᴜ ɢöɴᴅəʀɪɴ.")
        return
    await process_spotify_query(message, parts[1])
    raise StopHandlers


@Client.on_message(filters=Filter.sp_tube())
@fsub
async def spotify_autodetect(_: Client, message: types.Message):
    await process_spotify_query(message, message.text)
    raise StopHandlers
