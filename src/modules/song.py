from pytdbot import Client, types
from pytdbot.exception import StopHandlers

from src.utils import ApiData, shortener, Filter
# fsub-u hələlik bura əlavə etmirik ki, mane olmasın

async def process_spotify_query(message: types.Message, query: str):
    # Botun cavab verib-vermədiyini yoxlamaq üçün ilk mesaj
    try:
        response = await message.reply_text("⏳ ᴍᴀʜɴıʟᴀʀ ᴀxᴛᴀʀıʟıʀ...")
    except Exception as e:
        print(f"Mesaj göndərmə xətası: {e}")
        return

    api = ApiData(query)
    song_data = await api.get_info() if api.is_valid() else await api.search(limit="5")
    
    if isinstance(song_data, types.Error):
        await response.edit_text(f"❌ xəᴛᴀ: {song_data.message}")
        return

    if not song_data or not song_data.results:
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

# Komanda ilə yoxlama
@Client.on_message(filters=Filter.command(["spot", "spotify", "song"]))
async def spotify_cmd(_: Client, message: types.Message):
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        await message.reply_text("🔎 ᴢəʜᴍəᴛ ᴏʟᴍᴀsᴀ, ᴀxᴛᴀʀış sᴏʀğᴜsᴜ ɢöɴᴅəʀɪɴ.")
        return
    await process_spotify_query(message, parts[1])
    raise StopHandlers

# Link ilə avtomatik tanıma
@Client.on_message(filters=Filter.sp_tube())
async def spotify_autodetect(_: Client, message: types.Message):
    await process_spotify_query(message, message.text)
    raise StopHandlers
