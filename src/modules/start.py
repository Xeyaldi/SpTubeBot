import time
from datetime import datetime

from pytdbot import Client, types

from src import StartTime
from src.utils import Filter, ApiData

# fsub (məcburi abunəlik) silindi
from ._utils import StartMessage


def get_main_menu_keyboard(bot_username: str) -> types.ReplyMarkupInlineKeyboard:
    return types.ReplyMarkupInlineKeyboard([
        [
            types.InlineKeyboardButton(
                text="📢 ᴍəʟᴜᴍᴀᴛ ᴋᴀɴᴀʟı",
                type=types.InlineKeyboardButtonTypeUrl(url="https://t.me/ht_bots")
            ),
            types.InlineKeyboardButton(
                text="💬 ᴋöᴍəᴋ ǫʀᴜᴘᴜ",
                type=types.InlineKeyboardButtonTypeUrl(url="https://t.me/ht_bots_chat")
            )
        ],
        [
            types.InlineKeyboardButton(
                text="➕ ǫʀᴜᴘᴀ əʟᴀᴠə ᴇᴛ",
                type=types.InlineKeyboardButtonTypeUrl(
                    url=f"https://t.me/{bot_username}?startgroup=true"
                )
            ),
            types.InlineKeyboardButton(
                text="⚡ᴅᴇᴠᴇʟᴏᴘᴇʀ⚡",
                type=types.InlineKeyboardButtonTypeUrl(
                    url="https://t.me/kullaniciadidi"
                )
            )
        ],
        [
            types.InlineKeyboardButton(
                text="🎧 sᴘᴏᴛɪғʏ",
                type=types.InlineKeyboardButtonTypeCallback("help_spotify".encode())
            ),
            types.InlineKeyboardButton(
                text="🎥 ʏᴏᴜᴛᴜʙᴇ",
                type=types.InlineKeyboardButtonTypeCallback("help_youtube".encode())
            )
        ],
        [
            types.InlineKeyboardButton(
                text="☁️ sᴏᴜɴᴅᴄʟᴏᴜᴅ",
                type=types.InlineKeyboardButtonTypeCallback("help_soundcloud".encode())
            ),
            types.InlineKeyboardButton(
                text="🍎 ᴀᴘᴘʟᴇ ᴍᴜsɪᴄ",
                type=types.InlineKeyboardButtonTypeCallback("help_apple".encode())
            )
        ],
        [
            types.InlineKeyboardButton(
                text="📸 ɪɴsᴛᴀɢʀᴀᴍ",
                type=types.InlineKeyboardButtonTypeCallback("help_instagram".encode())
            ),
            types.InlineKeyboardButton(
                text="📌 ᴘɪɴᴛᴇʀᴇsᴛ",
                type=types.InlineKeyboardButtonTypeCallback("help_pinterest".encode())
            )
        ],
        [
            types.InlineKeyboardButton(
                text="👥 ғᴀᴄᴇʙᴏᴏᴋ",
                type=types.InlineKeyboardButtonTypeCallback("help_facebook".encode())
            ),
            types.InlineKeyboardButton(
                text="🐦 ᴛᴡɪᴛᴛᴇʀ (x)",
                type=types.InlineKeyboardButtonTypeCallback("help_twitter".encode())
            )
        ],
        [
            types.InlineKeyboardButton(
                text="🎵 ᴛɪᴋᴛᴏᴋ",
                type=types.InlineKeyboardButtonTypeCallback("help_tiktok".encode())
            ),
            types.InlineKeyboardButton(
                text="🧵 ᴛʜʀᴇᴀᴅs",
                type=types.InlineKeyboardButtonTypeCallback("help_threads".encode())
            )
        ],
        [
            types.InlineKeyboardButton(
                text="🧡 ʀᴇᴅᴅɪᴛ",
                type=types.InlineKeyboardButtonTypeCallback("help_reddit".encode())
            ),
            types.InlineKeyboardButton(
                text="🎮 ᴛᴡɪᴛᴄʜ",
                type=types.InlineKeyboardButtonTypeCallback("help_twitch".encode())
            )
        ]
    ])


@Client.on_message(filters=Filter.command(["start", "help"]))
async def welcome(c: Client, message: types.Message):
    bot_username = c.me.usernames.editable_username
    bot_name = c.me.first_name

    await message.reply_text(
        StartMessage.format(bot_name=bot_name, bot_username=bot_username),
        parse_mode="html",
        disable_web_page_preview=True,
        reply_markup=get_main_menu_keyboard(bot_username)
    )

@Client.on_message(filters=Filter.command("privacy"))
async def privacy_handler(_: Client, message: types.Message):
    await message.reply_text(
        "🔒 <b>ᴍəxғɪʟɪᴋ sɪʏᴀsəᴛɪ</b>\n\n"
        "ʙᴜ ʙᴏᴛ ʜᴇç ʙɪʀ şəxssɪ ᴍəʟᴜᴍᴀᴛı ʏᴀᴅᴅᴀ sᴀxʟᴀᴍıʀ.\n"
        "ʙüᴛüɴ sᴏʀğᴜʟᴀʀ ʀᴇᴀʟ ᴠᴀxᴛ ʀᴇᴊɪᴍɪɴᴅə ᴇᴍᴀʟ ᴏʟᴜɴᴜʀ.",
        parse_mode="html",
        disable_web_page_preview=True
    )
    
