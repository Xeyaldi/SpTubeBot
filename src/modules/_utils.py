import asyncio

from pytdbot import types, Client


async def has_audio_stream(url: str) -> bool:
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'a',
        '-show_entries', 'stream=index',
        '-of', 'csv=p=0',
        '-user_agent', 'Mozilla/5.0',
        url
    ]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=10)

        return bool(stdout.strip())
    except Exception as e:
        print(f"Error checking audio stream: {e}")
        return False


# Start mesajının tərcüməsi
StartMessage = (
        "<b>🎧 {bot_name}-ə xᴏş ɢəʟᴅɪɴɪᴢ!</b>\n"
        "əɴ ᴍəşʜᴜʀ ᴘʟᴀᴛғᴏʀᴍᴀʟᴀʀᴅᴀɴ ᴍᴜsɪǫɪ ᴠə ᴍᴇᴅɪᴀ ʏüᴋʟəᴍəᴋ üçüɴ süʀəᴛʟɪ ᴠə ᴀsᴀɴ ᴠᴀsɪᴛəɴɪᴢ.\n\n"
        "📩 sᴀᴅəᴄə ᴍᴀʜɴı ᴀᴅı, ʟɪɴᴋ ᴠə ʏᴀ ᴍᴇᴅɪᴀ ᴜʀʟ-ɪ ɢöɴᴅəʀɪɴ.\n"
        "🔎 ʏᴀᴢı ʏᴇʀɪɴᴅə ᴀxᴛᴀʀış: <code>@{bot_username} ᴍᴀʜɴı ᴀᴅı</code>\n\n"
        "🔐 ᴍəxғɪʟɪᴋ sɪʏᴀsəᴛɪ: /privacy\n"
    )

async def handle_help_callback(_: Client, message: types.UpdateNewCallbackQuery):
    data = message.payload.data.decode()
    platform = data.replace("help_", "")

    examples = {
        "spotify": (
            "💡 <b>sᴘᴏᴛɪғʏ ʏüᴋʟəʏɪᴄɪ</b>\n\n"
            "🔹 ᴍᴀʜɴıʟᴀʀı, ᴀʟʙᴏᴍʟᴀʀı ᴠə ᴘʟᴇʏʟɪsᴛʟəʀɪ ʏüᴋʟəʏɪɴ\n"
            "🔹 ʜəᴍ ᴀçıǫ, ʜəᴍ də ɢɪᴢʟɪ ʟɪɴᴋʟəʀɪ dəsᴛəᴋʟəʏɪʀ\n\n"
            "ɴüᴍᴜɴə ғᴏʀᴍᴀᴛʟᴀʀ:\n"
            "👉 <code>https://open.spotify.com/track/*</code>\n"
            "👉 <code>https://open.spotify.com/album/*</code>"
        ),
        "youtube": (
            "💡 <b>ʏᴏᴜᴛᴜʙᴇ ʏüᴋʟəʏɪᴄɪ</b>\n\n"
            "🔹 ᴠɪᴅᴇᴏʟᴀʀı ʏüᴋʟəʏɪɴ ᴠə ʏᴀ səsɪ çıxᴀʀıɴ\n"
            "🔹 ʏᴏᴜᴛᴜʙᴇ ᴍᴜsɪᴄ ʟɪɴᴋʟəʀɪɴɪ dəsᴛəᴋʟəʏɪʀ\n\n"
            "ɴüᴍᴜɴə ғᴏʀᴍᴀᴛʟᴀʀ:\n"
            "👉 <code>https://youtu.be/*</code>\n"
            "👉 <code>https://www.youtube.com/watch?v=*</code>"
        ),
        "soundcloud": (
            "💡 <b>sᴏᴜɴᴅᴄʟᴏᴜᴅ ʏüᴋʟəʏɪᴄɪ</b>\n\n"
            "🔹 ᴛʀᴇᴋʟəʀɪ ʏüᴋsəᴋ ᴋᴇʏғɪʏʏəᴛᴅə ʏüᴋʟəʏɪɴ\n\n"
            "ɴüᴍᴜɴə ғᴏʀᴍᴀᴛ:\n"
            "👉 <code>https://soundcloud.com/user/track-name</code>"
        ),
        "apple": (
            "💡 <b>ᴀᴘᴘʟᴇ ᴍᴜsɪᴄ ʏüᴋʟəʏɪᴄɪ</b>\n\n"
            "🔹 ᴍᴀʜɴıʟᴀʀı ᴠə ᴀʟʙᴏᴍʟᴀʀı dəsᴛəᴋʟəʏɪʀ\n\n"
            "ɴüᴍᴜɴə ғᴏʀᴍᴀᴛ:\n"
            "👉 <code>https://music.apple.com/*</code>"
        ),
        "instagram": (
            "💡 <b>ɪɴsᴛᴀɢʀᴀᴍ ᴍᴇᴅɪᴀ ʏüᴋʟəʏɪᴄɪ</b>\n\n"
            "🔹 ᴘᴏsᴛʟᴀʀı, ʀᴇᴇʟs ᴠə ʜᴇᴋᴀʏəʟəʀɪ ʏüᴋʟəʏɪɴ\n\n"
            "ɴüᴍᴜɴə ғᴏʀᴍᴀᴛ:\n"
            "👉 <code>https://www.instagram.com/reel/Cxyz123/</code>"
        ),
        "pinterest": (
            "💡 <b>ᴘɪɴᴛᴇʀᴇsᴛ ʏüᴋʟəʏɪᴄɪ</b>\n\n"
            "şəᴋɪʟ ᴠə ᴠɪᴅᴇᴏʟᴀʀı ʏüᴋʟəᴍəᴋ ᴍüᴍᴋüɴᴅüʀ:\n\n"
            "👉 <code>https://www.pinterest.com/pin/*</code>"
        ),
        "facebook": (
            "💡 <b>ғᴀᴄᴇʙᴏᴏᴋ ʏüᴋʟəʏɪᴄɪ</b>\n\n"
            "ᴠɪᴅᴇᴏʟᴀʀı ʏüᴋʟəᴍəᴋ ᴍüᴍᴋüɴᴅüʀ:\n\n"
            "👉 <code>https://www.facebook.com/watch/?v=*</code>"
        ),
        "twitter": (
            "💡 <b>ᴛᴡɪᴛᴛᴇʀ ʏüᴋʟəʏɪᴄɪ</b>\n\n"
            "ᴠɪᴅᴇᴏ ᴠə ʏᴀ şəᴋɪʟʟəʀɪ ʏüᴋʟəʏɪɴ:\n\n"
            "👉 <code>https://x.com/i/status/*</code>"
        ),
        "tiktok": (
            "💡 <b>ᴛɪᴋᴛᴏᴋ ʏüᴋʟəʏɪᴄɪ</b>\n\n"
            "ʟᴏɢᴏsᴜᴢ ʏüᴋʟəᴍəɴɪ dəsᴛəᴋʟəʏɪʀ:\n\n"
            "👉 <code>https://vt.tiktok.com/*</code>"
        ),
        "threads": (
            "💡 <b>ᴛʜʀᴇᴀᴅs ʏüᴋʟəʏɪᴄɪ</b>\n\n"
            "ᴛʜʀᴇᴀᴅs-ᴅəɴ ᴍᴇᴅɪᴀ ʏüᴋʟəʏɪɴ:\n\n"
            "👉 <code>https://www.threads.net/@post/*</code>"
        ),
        "reddit": (
            "💡 <b>ʀᴇᴅᴅɪᴛ ʏüᴋʟəʏɪᴄɪ</b>\n\n"
            "ʀᴇᴅᴅɪᴛ-ᴅəɴ ᴍᴇᴅɪᴀ ʏüᴋʟəʏɪɴ:\n\n"
            "👉 <code>https://www.reddit.com/r/*</code>"
        ),
        "twitch": (
            "💡 <b>ᴛᴡɪᴛᴄʜ ᴋʟɪᴘ ʏüᴋʟəʏɪᴄɪ</b>\n\n"
            "ᴛᴡɪᴛᴄʜ-ᴅəɴ ᴍᴇᴅɪᴀ ʏüᴋʟəʏɪɴ:\n\n"
            "👉 <code>https://www.twitch.tv/*/clip/*</code>"
        ),
    }

    reply_text = examples.get(platform, "<b>ʙᴜ ᴘʟᴀᴛғᴏʀᴍᴀ üçüɴ ᴋöᴍəᴋçɪ ᴍəʟᴜᴍᴀᴛ ᴛᴀᴘıʟᴍᴀᴅı.</b>")
    await message.answer(text=f"{platform.upper()} ᴋöᴍəᴋ ᴍᴇɴʏᴜsᴜ")
    await message.edit_message_text(
        text=reply_text,
        parse_mode="html",
        disable_web_page_preview=True,
        reply_markup=types.ReplyMarkupInlineKeyboard([
            [
                types.InlineKeyboardButton(
                    text="⬅️ ɢᴇʀɪ",
                    type=types.InlineKeyboardButtonTypeCallback("back_menu".encode())
                )
            ]
        ])
    )
