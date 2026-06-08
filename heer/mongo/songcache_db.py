from heer.core.mongo import mongodb

songcache_db = mongodb["songcache"]


async def get_cached_song(videoid: str, media_type: str):
    """Return cached song doc for videoid + type (audio/video), or None."""
    return await songcache_db.find_one({"videoid": videoid, "type": media_type})


async def save_cached_song(
    videoid: str,
    media_type: str,
    file_id: str,
    message_id: int,
    title: str = "",
):
    await songcache_db.update_one(
        {"videoid": videoid, "type": media_type},
        {
            "$set": {
                "videoid": videoid,
                "type": media_type,
                "file_id": file_id,
                "message_id": message_id,
                "title": title,
            }
        },
        upsert=True,
    )
