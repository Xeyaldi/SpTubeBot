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


StartMessage = (
        "<b>🎧 {bot_name}-ə xoş gəldiniz!</b>\n"
        "Ən məşhur platformalardan musiqi və media yükləmək üçün sürətli və asan vasitəniz.\n\n"
        "📩 Sadəcə mahnı adı, link və ya media URL-i göndərin.\n"
        "🔎 Yazı yerində axtarış: <code>@{bot_username} mahnı adı</code>\n\n"
        "🔐 Məxfilik siyasəti: /privacy\n"
    )

async def handle_help_callback(_: Client, message: types.UpdateNewCallbackQuery):
    data = message.payload.data.decode()
    platform = data.replace("help_", "")

    examples = {
        "spotify": (
            "💡<b>Spotify Yükləyici</b>\n\n"
            "🔹 Mahnıları, albomları və pleylistləri 320kbps keyfiyyətində yükləyin\n"
            "🔹 Həm açıq, həm də gizli linkləri dəstəkləyir\n\n"
            "Nümunə formatlar:\n"
            "👉 <code>https://open.spotify.com/track/*</code> (Tək mahnı)\n"
            "👉 <code>https://open.spotify.com/album/*</code> (Tam albom)\n"
            "👉 <code>https://open.spotify.com/playlist/*</code> (Pleylist)\n"
            "👉 <code>https://open.spotify.com/artist/*</code> (Sənətçinin ən çox dinlənilənləri)"
        ),
        "youtube": (
            "💡<b>YouTube Yükləyici</b>\n\n"
            "🔹 Videoları yükləyin və ya səsi çıxarın\n"
            "🔹 Həm YouTube, həm də YouTube Music linklərini dəstəkləyir\n\n"
            "Nümunə formatlar:\n"
            "👉 <code>https://youtu.be/*</code> (Qısa URL)\n"
            "👉 <code>https://www.youtube.com/watch?v=*</code> (Tam URL)\n"
            "👉 <code>https://music.youtube.com/watch?v=*</code> (YouTube Music)"
        ),
        "soundcloud": (
            "💡<b>SoundCloud Yükləyici</b>\n\n"
            "🔹 Trekləri yüksək keyfiyyətdə yükləyin\n"
            "🔹 Həm açıq, həm də gizli trekləri dəstəkləyir\n\n"
            "Nümunə formatlar:\n"
            "👉 <code>https://soundcloud.com/user/track-name</code>\n"
            "👉 <code>https://soundcloud.com/user/track-name?utm_source=*</code> (İzləmə parametrləri ilə)"
        ),
        "apple": (
            "💡<b>Apple Music Yükləyici</b>\n\n"
            "🔹 İtkisiz (Lossless) musiqi yükləmələri\n"
            "🔹 Mahnıları, albomları və sənətçiləri dəstəkləyir\n\n"
            "Nümunə formatlar:\n"
            "👉 <code>https://music.apple.com/*</code>\n"
            "👉 <code>https://music.apple.com/us/song/*</code>\n"
            "👉 <code>https://music.apple.com/us/album/*</code>\n"
            "👉 <code>https://music.apple.com/us/artist/*</code>"
        ),
        "instagram": (
            "💡<b>Instagram Media Yükləyici</b>\n\n"
            "🔹 Instagram postlarını, reels və hekayələrini yükləyin\n"
            "🔹 Həm açıq, həm də gizli hesabları dəstəkləyir\n\n"
            "Nümunə formatlar:\n"
            "👉 <code>https://www.instagram.com/p/*</code> (Postlar)\n"
            "👉 <code>https://www.instagram.com/reel/*</code> (Reels)\n"
            "👉 <code>https://www.instagram.com/stories/*</code> (Hekayələr)\n"
           "Reels, Hekayə və Postları yükləyin:\n\n"
            "👉 <code>https://www.instagram.com/reel/Cxyz123/</code>"
        ),
        "pinterest": (
            "💡<b>Pinterest Yükləyici</b>\n\n"
            "Şəkil və videoları yükləmək mümkündür:\n\n"
            "👉 <code>https://www.pinterest.com/pin/1085649053904273177/</code>"
        ),
        "facebook": (
            "💡<b>Facebook Yükləyici</b>\n\n"
            "Açıq səhifələrdəki videolarla işləyir:\n\n"
            "👉 <code>https://www.facebook.com/watch/?v=123456789</code>"
        ),
        "twitter": (
            "💡<b>Twitter Yükləyici</b>\n\n"
            "Postlardakı video və ya şəkilləri yükləyin:\n\n"
            "👉 <code>https://x.com/i/status/1951310276814578086</code>\n"
            "👉 <code>https://twitter.com/i/status/1951310276814578086</code>\n"
            "👉 <code>https://x.com/luismbat/status/1951307858764607604/photo/1</code>"
        ),
        "tiktok": (
            "💡<b>TikTok Yükləyici</b>\n\n"
            "Logosuz (watermark-free) yükləməni dəstəkləyir:\n\n"
            "👉 <code>https://vt.tiktok.com/ZSB3BovQp/</code>\n"
            "👉 <code>https://vt.tiktok.com/ZSSe7NprD/</code>"
        ),
        "threads": (
            "💡<b>Threads Yükləyici</b>\n\n"
            "Threads-dən media yükləyin:\n\n"
            "👉 <code>https://www.threads.com/@camycavero/post/DM0FquaM2At?xmt=AQF0u_6ebeMHEjWCw0cm0Li4i8fI3INIU7YeSMffM9DmDw</code>\n"
        ),
        "reddit": (
            "💡<b>Reddit Yükləyici</b>\n\n"
            "Reddit-dən media yükləyin:\n\n"
            "👉 <code>https://www.reddit.com/r/tollywood/comments/1mld609/what_is_your_honest_unfiltered_opinion_on_mahesh/</code>\n"
            "👉 <code>https://www.reddit.com/r/Damnthatsinteresting/comments/1mlfgzv/when_cat_meets_cat/</code>\n"
            "👉 <code>https://www.reddit.com/r/Indian_flex/comments/1mlez7j/tough_life/</code>\n"
        ),
        "twitch": (
            "💡<b>Twitch Klip Yükləyici</b>\n\n"
            "Twitch-dən media yükləyin:\n\n"
            "👉 <code>https://www.twitch.tv/tarik/clip/CheerfulHonorableBibimbapHumbleLife-cdCV_zL45i1p2Kh6</code>\n"
        ),
    }

    reply_text = examples.get(platform, "<b>Bu platforma üçün köməkçi məlumat tapılmadı.</b>")
    await message.answer(text=f"{platform} Kömək Menyu")
    await message.edit_message_text(
        text=reply_text,
        parse_mode="html",
        disable_web_page_preview=True,
        reply_markup=types.ReplyMarkupInlineKeyboard([
            [
                types.InlineKeyboardButton(
                    text="⬅️ Geri",
                    type=types.InlineKeyboardButtonTypeCallback("back_menu".encode())
                )
            ]
        ])
    )
    
