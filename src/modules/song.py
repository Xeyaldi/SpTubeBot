from pytdbot import Client, types
from pytdbot.exception import StopHandlers
from src.utils import ApiData, Filter, shortener
from ._fsub import fsub
from ._media_utils import process_track_media, get_reply_markup

async def process_spotify_query(client: Client, message: types.Message, query: str):
    # Mesajın qəbul edildiyini göstərən ilkin status
    status = await message.reply_text("⏳ ᴍəʟᴜᴍᴀᴛʟᴀʀ ᴇᴍᴀʟ ᴏʟᴜɴᴜʀ...")
    
    api = ApiData(query)
    
    # 1. Əgər birbaşa linkdirsə (Spotify və ya YouTube)
    if api.is_valid():
        track_info = await api.get_info()
        if track_info and track_info.results:
            # Birbaşa yükləməyə göndəririk
            res = await process_track_media(client, track_info.results[0], message.chat_id, status.id)
            if not isinstance(res, types.Error):
                audio, cover, caption = res
                await message.reply_audio(
                    audio,
                    caption=caption,
                    thumbnail=types.InputFileRemote(cover) if cover else None,
                    reply_markup=get_reply_markup(track_info.results[0].title, track_info.results[0].channel)
                )
                await status.delete()
                return
        await status.edit_text("❌ ᴍᴇᴅɪᴀ ʏüᴋʟəɴə ʙɪʟᴍəᴅɪ.")
        return

    # 2. Əgər axtarış sözüdürsə
    search_results = await api.search(limit="5")
    if not search_results or not search_results.results:
        await status.edit_text("❌ ɴəᴛɪᴄə ᴛᴀᴘıʟᴍᴀᴅı.")
        return

    keyboard = []
    for track in search_results.results:
        # Linki qısaldırıq ki, düyməyə sığsın
        callback_data = f"spot_{shortener.encode_url(track.url)}_0"
        keyboard.append([types.InlineKeyboardButton(
            text=f"{track.title} - {track.channel}",
            type=types.InlineKeyboardButtonTypeCallback(callback_data.encode())
        )])

    await status.edit_text(
        f"🔎 ᴀxᴛᴀʀış ɴəᴛɪᴄəsɪ: <b>{query}</b>",
        parse_mode="html",
        reply_markup=types.ReplyMarkupInlineKeyboard(keyboard)
    )

@Client.on_message(filters=Filter.command(["song", "spotify", "spot"]))
@fsub
async def song_cmd(client: Client, message: types.Message):
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        await message.reply_text("🔎 ᴢəʜᴍəᴛ ᴏʟᴍᴀsᴀ, ᴍᴀʜɴı ᴀdı ᴠə ʏᴀ ʟɪɴᴋ ɢöɴᴅəʀɪɴ.")
        return
    await process_spotify_query(client, message, parts[1])
    raise StopHandlers

@Client.on_message(filters=Filter.sp_tube())
@fsub
async def song_autodetect(client: Client, message: types.Message):
    # Bu filtr həm linkləri, həm də düz yazıları tutur
    await process_spotify_query(client, message, message.text)
    raise StopHandlers
