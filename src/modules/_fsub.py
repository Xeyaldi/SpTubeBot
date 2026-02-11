from typing import TypeAlias, Union, Callable, Awaitable
from functools import wraps
from pytdbot import Client, types
from src.config import FSUB_ID

ChatMemberStatus: TypeAlias = Union[
    types.ChatMemberStatusCreator,
    types.ChatMemberStatusAdministrator,
    types.ChatMemberStatusMember,
    types.ChatMemberStatusRestricted,
    types.ChatMemberStatusLeft,
    types.ChatMemberStatusBanned,
]

BLOCKED_STATUSES = {
    types.ChatMemberStatusLeft().getType(),
    types.ChatMemberStatusBanned().getType(),
    types.ChatMemberStatusRestricted().getType(),
}

# Caches
member_status_cache = {}
invite_link_cache: dict[int, str] = {}

def fsub(func: Callable[..., Awaitable]):
    @wraps(func)
    async def wrapper(client: Client, message: types.Message, *args, **kwargs):
        # Məcburi abunəliyi tamamilə ləğv etmək üçün aşağıdakı sətiri əlavə etdik:
        return await func(client, message, *args, **kwargs)

        # Bundan aşağıdakı kodlar artıq icra olunmayacaq (yəni yoxlama aparılmayacaq)
        chat_id = message.chat_id
        if chat_id < 0:
            return await func(client, message, *args, **kwargs)

        if not FSUB_ID or FSUB_ID == 0:
            return await func(client, message, *args, **kwargs)

        user_id = message.from_id
        cached_status = member_status_cache.get(user_id)

        if cached_status and cached_status not in BLOCKED_STATUSES:
            return await func(client, message, *args, **kwargs)

        member = await client.getChatMember(
            chat_id=FSUB_ID,
            member_id=types.MessageSenderUser(user_id)
        )
        
        if isinstance(member, types.Error) or member.status is None:
            status_type = types.ChatMemberStatusLeft().getType()
        else:
            status_type = member.status.getType()

        if status_type not in BLOCKED_STATUSES:
            member_status_cache[user_id] = status_type
            return await func(client, message, *args, **kwargs)

        # Əgər abunəlik aktiv olsaydı, bu mesaj görünəcəkdi:
        text = (
            "🔒 <b>ᴋᴀɴᴀʟᴀ ᴀʙᴜɴəʟɪᴋ ᴛəʟəʙ ᴏʟᴜɴᴜʀ</b>\n\n"
            "ʙᴏᴛᴅᴀɴ ɪsᴛɪғᴀᴅə ᴇᴛᴍəᴋ üçüɴ ᴋᴀɴᴀʟıᴍıᴢᴀ ǫᴏşᴜʟᴍᴀʟısıɴıᴢ.\n"
            "✅ ǫᴏşᴜʟᴅᴜǫᴅᴀɴ sᴏɴʀᴀ ʙᴏᴛᴜ ᴀᴋᴛɪᴠʟəşᴅɪʀᴍəᴋ üçüɴ /start ʏᴀᴢıɴ.\n\n"
            "💬 ǫʀᴜᴘʟᴀʀᴅᴀ ᴀʙᴜɴəʟɪᴋ ᴛəʟəʙ ᴏʟᴜɴᴍᴜʀ."
        )
        button = types.ReplyMarkupInlineKeyboard(
            [[types.InlineKeyboardButton(text="📢 ᴋᴀɴᴀʟᴀ ǫᴏşᴜʟ",
                                         type=types.InlineKeyboardButtonTypeUrl(url="https://t.me/ht_bots"))]]
        )

        return await message.reply_text(
            text=text,
            parse_mode="html",
            disable_web_page_preview=True,
            reply_markup=button,
        )

    return wrapper

# Digər funksiyalar (status dəyişikliyi və s.) olduğu kimi qalır...
