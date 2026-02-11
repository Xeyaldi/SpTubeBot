import asyncio
import os
from typing import Optional

from pymongo import AsyncMongoClient
from pytdbot import types


from src.config import MONGO_URI, LOGGER_ID
from ._dataclass import Spotify


async def convert_to_m4a(input_file: str, cover_file: str, track: Spotify) -> str | None:
    """Audio faylı üz qabığı və metadata ilə M4A formatına çevirir."""
    abs_input = os.path.abspath(input_file)
    abs_cover = os.path.abspath(cover_file)
    output_file = f"{os.path.splitext(abs_input)[0]}.m4a"

    cmd = [
        "ffmpeg", "-y",
        "-i", abs_input, "-i", abs_cover,
        "-map", "0:a", "-map", "1:v",
        "-c:a", "aac", "-b:a", "192k",
        "-c:v", "png",
        "-metadata:s:v", "title=Album cover",
        "-metadata:s:v", "comment=Cover (front)",
        "-metadata", f"lyrics={track.lyrics}",
        "-metadata", f"title={track.name}",
        "-metadata", f"artist={track.artist}",
        "-metadata", f"album={track.album}",
        "-metadata", f"year={track.year}",
        "-metadata", "genre=Spotify",
        "-metadata", "comment=Via SpTube Bot",
        "-f", "mp4",
        output_file,
    ]

    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        print(f"ғғᴍᴘᴇɢ xəᴛᴀsı:\n{stderr.decode(errors='ignore')}")
        return None

    return output_file



class MongoDB:
    def __init__(self):
        self.mongo_client = AsyncMongoClient(MONGO_URI)
        self._db = self.mongo_client["SpTube"]
        self.songs = self._db["songs"]
        self.logger_chat_id = LOGGER_ID
        self._cache: dict[str, str] = {}

    async def connect(self) -> None:
        """ᴍᴏɴɢᴏᴅʙ ʙᴀğʟᴀɴᴛısı ǫᴜʀᴜʟᴜʀ ᴠə ᴋᴇş ʏüᴋʟəɴɪʀ."""
        await self.mongo_client.aconnect()
        try:
            await self.mongo_client.admin.command("ping")
        except Exception as e:
            raise e
        await self._load_cache()

    async def _load_cache(self) -> None:
        """Bazada olan bütün mahnıları operativ yaddaşa (cache) yükləyir."""
        async for song in self.songs.find():
            self._cache[song["_id"]] = song["link"]

    async def store_song_link(self, track_id: str, link: str) -> None:
        """Mahnı linkini bazada saxlayır və keşləyir."""
        await self.songs.update_one({"_id": track_id}, {"$set": {"link": link}}, upsert=True)
        self._cache[track_id] = link

    async def get_song_link(self, track_id: str) -> Optional[str]:
        """Mahnı linkini keşdən və ya bazadan götürür."""
        if track_id in self._cache:
            return self._cache[track_id]

        song = await self.songs.find_one({"_id": track_id})
        if song:
            self._cache[track_id] = song["link"]
            return song["link"]
        return None

    async def get_song_file_id(self, track_id: str) -> tuple[Optional[str], Optional[types.FormattedText]]:
        """Saxlanılan link üçün Telegram fayl ID-sini əldə edir."""
        from src import client

        link = await self.get_song_link(track_id)
        if not link:
            return None, None

        info = await client.getMessageLinkInfo(url=link)
        if isinstance(info, types.Error) or not info.message:
            client.logger.warning(f"❌ ᴍᴇsᴀᴊ ʟɪɴᴋɪ ᴍəʟᴜᴍᴀᴛı ᴀʟıɴᴍᴀᴅı: {getattr(info, 'message', info)}")
            return None, None

        msg = await client.getMessage(info.chat_id, info.message.id)
        if isinstance(msg, types.Error):
            client.logger.warning(f"❌ ᴍᴇsᴀᴊ ᴛᴀᴘıʟᴍᴀᴅı: {msg.message}")
            return None, None

        content = msg.content
        text = content.caption
        if isinstance(content, types.MessageAudio):
            return content.audio.audio.remote.id, text
        elif isinstance(content, types.MessageDocument):
            return content.document.document.remote.id, text
        elif isinstance(content, types.MessageVideo):
            return content.video.video.remote.id, text

        client.logger.warning(f"❌ ᴅəsᴛəᴋʟəɴᴍəʏəɴ ᴍᴇᴅɪᴀ ɴöᴠü: {content}")
        await self.remove_song(track_id)
        return None, text

    async def upload_song_and_get_file_id(
            self, file_path: str, cover: Optional[str], track: Spotify
    ) -> tuple[Optional[str], types.FormattedText] | types.Error:
        """Mahnını arxiv kanalına yükləyir və ID qaytarır."""
        from src import client

        thumb = types.InputThumbnail(thumbnail=types.InputFileLocal(cover) if cover else types.InputFileRemote(track.cover), width=640, height=640)
        async def _send(path: str):
            return await client.sendAudio(
                chat_id=self.logger_chat_id,
                audio=types.InputFileLocal(path),
                album_cover_thumbnail=thumb,
                title=track.name,
                performer=track.artist,
                caption=f"<b>{track.name}</b>\n<i>{track.artist}</i>",
            )

        upload = await _send(file_path)

        # Səs qeydi kimi yüklənmə xətası (FFmpeg ilə düzəliş)
        if not isinstance(upload, types.Error) and isinstance(upload.content, types.MessageVoiceNote):
            fixed_path = await convert_to_m4a(file_path, cover, track)
            if not fixed_path:
                public_link = await client.getMessageLink(upload.chat_id, upload.id)
                return types.Error(
                    message=f"ᴍᴀʜɴı ʏüᴋʟəɴᴍəᴅɪ - ʟɪɴᴋ: {public_link.link or 'ʟɪɴᴋ ᴛᴀᴘıʟᴍᴀᴅı'}"
                )

            await upload.delete()
            upload = await _send(fixed_path)

            try:
                os.remove(fixed_path)
            except Exception as e:
                client.logger.warning(f"❌ ᴄᴏɴᴠᴇʀᴛ ᴏʟᴜɴᴍᴜş ғᴀʏʟ sɪʟɪɴᴍəᴅɪ: {e}")

        if isinstance(upload, types.Error):
            client.logger.warning(f"❌ ᴀᴜᴅɪᴏ ʏüᴋʟəɴᴍəᴅɪ: {upload.message}")
            return upload

        public_link = await client.getMessageLink(upload.chat_id, upload.id)
        if isinstance(public_link, types.Error):
            client.logger.warning(f"❌ ᴘᴜʙʟɪᴄ ʟɪɴᴋ ᴀʟıɴᴍᴀᴅı: {public_link.message}")
            return public_link

        try:
            os.remove(file_path)
        except Exception as e:
            client.logger.warning(f"❌ ᴏʀɪᴊɪɴᴀʟ ғᴀʏʟ sɪʟɪɴᴍəᴅɪ: {e}")

        if isinstance(upload.content, types.MessageAudio):
            await self.store_song_link(track.tc, public_link.link)
            return upload.content.audio.audio.remote.id, upload.content.caption

        return types.Error(
            message=f"ᴍᴀʜɴı ʏüᴋʟəɴᴍəᴅɪ - ʟɪɴᴋ: {public_link.link}"
        )

    async def remove_song(self, track_id: str) -> None:
        """Mahnını bazadan və keşdən silir."""
        await self.songs.delete_one({"_id": track_id})
        if track_id in self._cache:
            del self._cache[track_id]

    async def close(self) -> None:
        """Bağlantını kəsir."""
        await self.mongo_client.aclose()
        self._cache.clear()


# Global DB instance
db: MongoDB = MongoDB()
