import asyncio
import os
from typing import Optional

import config
from heer import LOGGER
from heer.mongo.songcache_db import get_cached_song, save_cached_song

logger = LOGGER("heer.utils.song_cache")

_MIN_FILE_BYTES = 10240


async def fetch_cached_download(videoid: str, is_video: bool) -> Optional[str]:
    """Fetch a previously cached song from the log group via MongoDB file_id."""
    if not config.LOGGER_ID:
        return None

    media_type = "video" if is_video else "audio"
    doc = await get_cached_song(videoid, media_type)
    if not doc or not doc.get("file_id"):
        return None

    from heer import app

    ext = ".mp4" if is_video else ".mp3"
    dest = os.path.join("downloads", f"{videoid}{ext}")
    os.makedirs("downloads", exist_ok=True)

    try:
        path = await app.download_media(doc["file_id"], file_name=dest)
        if path and os.path.exists(path) and os.path.getsize(path) > _MIN_FILE_BYTES:
            logger.info("Loaded %s for %s from log group cache", media_type, videoid)
            return path
    except Exception as exc:
        logger.warning("Log group cache fetch failed for %s: %s", videoid, exc)
    return None


async def save_to_cache(
    videoid: str,
    file_path: str,
    is_video: bool,
    title: str = "",
) -> None:
    """Upload downloaded media to log group and store file_id in MongoDB."""
    if not config.LOGGER_ID or not file_path or not os.path.exists(file_path):
        return
    if os.path.getsize(file_path) <= _MIN_FILE_BYTES:
        return

    media_type = "video" if is_video else "audio"
    existing = await get_cached_song(videoid, media_type)
    if existing and existing.get("file_id"):
        return

    from heer import app

    label = title or videoid
    caption = (
        f"{'🎬' if is_video else '🎵'} <b>{label[:64]}</b>\n"
        f"🆔 <code>{videoid}</code>"
    )

    try:
        if is_video:
            msg = await app.send_video(
                config.LOGGER_ID, video=file_path, caption=caption
            )
            file_id = msg.video.file_id
        else:
            try:
                msg = await app.send_audio(
                    config.LOGGER_ID, audio=file_path, caption=caption
                )
                file_id = msg.audio.file_id
            except Exception:
                msg = await app.send_document(
                    config.LOGGER_ID, document=file_path, caption=caption
                )
                file_id = msg.document.file_id

        await save_cached_song(videoid, media_type, file_id, msg.id, title)
        logger.info("Cached %s for %s in log group", media_type, videoid)
    except Exception as exc:
        logger.warning("Failed to cache %s (%s): %s", videoid, media_type, exc)


def schedule_cache_save(
    videoid: str,
    file_path: str,
    is_video: bool,
    title: str = "",
) -> None:
    """Upload to log group in background so playback is not delayed."""
    asyncio.create_task(save_to_cache(videoid, file_path, is_video, title))
