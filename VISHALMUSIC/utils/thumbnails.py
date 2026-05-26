import os
import aiofiles
import aiohttp
from PIL import Image
from py_yt import VideosSearch
from config import YOUTUBE_IMG_URL
from VISHALMUSIC.core.dir import CACHE_DIR


async def get_thumb(videoid: str) -> str:
    cache_path = os.path.join(CACHE_DIR, f"{videoid}_fullscreen.png")
    if os.path.exists(cache_path):
        return cache_path

    # Fetch YouTube video data
    results = VideosSearch(f"https://www.youtube.com/watch?v={videoid}", limit=1)
    try:
        results_data = await results.next()
        data = results_data.get("result", [])[0]
        thumbnail = data.get("thumbnails", [{}])[0].get("url", YOUTUBE_IMG_URL)
    except Exception:
        thumbnail = YOUTUBE_IMG_URL

    # Download thumbnail
    thumb_path = os.path.join(CACHE_DIR, f"thumb{videoid}.png")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    async with aiofiles.open(thumb_path, "wb") as f:
                        await f.write(await resp.read())
    except Exception:
        return YOUTUBE_IMG_URL

    # Just the thumbnail - full screen, no overlays
    img = Image.open(thumb_path).resize((1280, 720)).convert("RGBA")

    # Cleanup
    try:
        os.remove(thumb_path)
    except OSError:
        pass

    img.save(cache_path)
    return cache_path
