import os
import re
import random
import aiofiles
import aiohttp
import requests

from bs4 import BeautifulSoup
from PIL import (
    Image,
    ImageDraw,
    ImageEnhance,
    ImageFilter,
    ImageFont,
    ImageOps,
)

from py_yt import VideosSearch
from config import YOUTUBE_IMG_URL
from VISHALMUSIC.core.dir import CACHE_DIR


# =========================
# PANEL SETTINGS
# =========================

PANEL_W, PANEL_H = 763, 545
PANEL_X = (1280 - PANEL_W) // 2
PANEL_Y = 88

TRANSPARENCY = 170
INNER_OFFSET = 36

THUMB_W, THUMB_H = 542, 273
THUMB_X = PANEL_X + (PANEL_W - THUMB_W) // 2
THUMB_Y = PANEL_Y + INNER_OFFSET

TITLE_X = 377
META_X = 377

TITLE_Y = THUMB_Y + THUMB_H + 10
META_Y = TITLE_Y + 45

BAR_X, BAR_Y = 388, META_Y + 45
BAR_RED_LEN = 280
BAR_TOTAL_LEN = 480

ICONS_W, ICONS_H = 415, 45
ICONS_X = PANEL_X + (PANEL_W - ICONS_W) // 2
ICONS_Y = BAR_Y + 48

MAX_TITLE_WIDTH = 580


# =========================
# RANDOM ACCENT COLORS
# =========================

ACCENTS = [
    (255, 102, 204),
    (102, 204, 255),
    (255, 153, 102),
    (153, 102, 255),
    (102, 255, 178),
    (255, 255, 102),
    (255, 51, 153),
    (51, 255, 255),
    (255, 102, 0),
    (102, 0, 255),
    (0, 255, 102),
    (255, 0, 102),
    (0, 204, 255),
    (204, 0, 255),
    (255, 204, 102),
]


# =========================
# TEXT TRIMMER
# =========================

def trim_to_width(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> str:
    ellipsis = "…"

    if font.getlength(text) <= max_w:
        return text

    for i in range(len(text) - 1, 0, -1):
        if font.getlength(text[:i] + ellipsis) <= max_w:
            return text[:i] + ellipsis

    return ellipsis


# =========================
# RANDOM ANIME BACKGROUND
# =========================

async def get_random_anime_bg():

    url = "https://wallpapercave.com/anime-girl-laptop-wallpapers"

    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers)

        soup = BeautifulSoup(response.text, "html.parser")

        images = []

        for img in soup.find_all("img"):

            src = img.get("src")

            if src and "wallpapers" in src:

                if src.startswith("//"):
                    src = "https:" + src

                elif src.startswith("/"):
                    src = "https://wallpapercave.com" + src

                images.append(src)

        if not images:
            return None

        return random.choice(images)

    except Exception as e:
        print(f"Anime BG Error: {e}")
        return None


# =========================
# MAIN THUMBNAIL FUNCTION
# =========================

async def get_thumb(videoid: str) -> str:

    cache_path = os.path.join(
        CACHE_DIR,
        f"{videoid}_anime_premium.png"
    )

    if os.path.exists(cache_path):
        return cache_path

    # =========================
    # GET YOUTUBE DATA
    # =========================

    results = VideosSearch(
        f"https://www.youtube.com/watch?v={videoid}",
        limit=1
    )

    try:

        results_data = await results.next()

        data = results_data.get("result", [])[0]

        title = re.sub(
            r"\W+",
            " ",
            data.get("title", "Unsupported Title")
        ).title()

        thumbnail = data.get(
            "thumbnails",
            [{}]
        )[0].get("url", YOUTUBE_IMG_URL)

        duration = data.get("duration")

        views = data.get(
            "viewCount",
            {}
        ).get("short", "Unknown Views")

    except Exception:

        title = "Unsupported Title"
        thumbnail = YOUTUBE_IMG_URL
        duration = None
        views = "Unknown Views"

    is_live = (
        not duration or
        str(duration).strip().lower() in {
            "",
            "live",
            "live now"
        }
    )

    duration_text = (
        "Live"
        if is_live
        else duration or "Unknown"
    )

    # =========================
    # DOWNLOAD YOUTUBE THUMB
    # =========================

    thumb_path = os.path.join(
        CACHE_DIR,
        f"thumb_{videoid}.png"
    )

    try:

        async with aiohttp.ClientSession() as session:

            async with session.get(thumbnail) as resp:

                if resp.status == 200:

                    async with aiofiles.open(
                        thumb_path,
                        "wb"
                    ) as f:

                        await f.write(await resp.read())

    except Exception:
        return YOUTUBE_IMG_URL

    # =========================
    # RANDOM ANIME BACKGROUND
    # =========================

    accent = random.choice(ACCENTS)

    anime_path = os.path.join(
        CACHE_DIR,
        f"anime_{videoid}.jpg"
    )

    anime_url = await get_random_anime_bg()

    try:

        if anime_url:

            async with aiohttp.ClientSession() as session:

                async with session.get(anime_url) as resp:

                    if resp.status == 200:

                        async with aiofiles.open(
                            anime_path,
                            "wb"
                        ) as f:

                            await f.write(await resp.read())

            bg = Image.open(anime_path).resize(
                (1280, 720)
            ).convert("RGBA")

        else:

            bg = Image.open(thumb_path).resize(
                (1280, 720)
            ).convert("RGBA")

    except Exception:

        bg = Image.open(thumb_path).resize(
            (1280, 720)
        ).convert("RGBA")

    # =========================
    # PREMIUM EFFECTS
    # =========================

    overlay = Image.new(
        "RGBA",
        bg.size,
        (0, 0, 0, 120)
    )

    bg = Image.alpha_composite(bg, overlay)

    bg = bg.filter(
        ImageFilter.GaussianBlur(3)
    )

    bg = ImageEnhance.Brightness(bg).enhance(0.8)

    # =========================
    # GLASS PANEL
    # =========================

    panel_area = bg.crop(
        (
            PANEL_X,
            PANEL_Y,
            PANEL_X + PANEL_W,
            PANEL_Y + PANEL_H
        )
    )

    overlay = Image.new(
        "RGBA",
        (PANEL_W, PANEL_H),
        (255, 255, 255, TRANSPARENCY)
    )

    frosted = Image.alpha_composite(
        panel_area,
        overlay
    )

    mask = Image.new(
        "L",
        (PANEL_W, PANEL_H),
        0
    )

    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, PANEL_W, PANEL_H),
        50,
        fill=255
    )

    bg.paste(
        frosted,
        (PANEL_X, PANEL_Y),
        mask
    )

    # =========================
    # FONTS
    # =========================

    draw = ImageDraw.Draw(bg)

    try:

        title_font = ImageFont.truetype(
            "VISHALMUSIC/assets/thumb/font2.ttf",
            36
        )

        regular_font = ImageFont.truetype(
            "VISHALMUSIC/assets/thumb/font.ttf",
            20
        )

    except OSError:

        title_font = ImageFont.load_default()
        regular_font = ImageFont.load_default()

    # =========================
    # THUMBNAIL IMAGE
    # =========================

    yt_thumb = Image.open(thumb_path).resize(
        (THUMB_W, THUMB_H)
    )

    tmask = Image.new(
        "L",
        yt_thumb.size,
        0
    )

    ImageDraw.Draw(tmask).rounded_rectangle(
        (0, 0, THUMB_W, THUMB_H),
        25,
        fill=255
    )

    bg.paste(
        yt_thumb,
        (THUMB_X, THUMB_Y),
        tmask
    )

    # =========================
    # TITLE
    # =========================

    title_text = trim_to_width(
        title,
        title_font,
        MAX_TITLE_WIDTH
    )

    shadow_pos = (
        TITLE_X + 2,
        TITLE_Y + 2
    )

    draw.text(
        shadow_pos,
        title_text,
        font=title_font,
        fill=(0, 0, 0, 180)
    )

    draw.text(
        (TITLE_X, TITLE_Y),
        title_text,
        font=title_font,
        fill=accent
    )

    draw.text(
        (META_X, META_Y),
        f"YouTube | {views}",
        fill=(40, 40, 40),
        font=regular_font
    )

    # =========================
    # PROGRESS BAR
    # =========================

    bar_y = BAR_Y

    draw.line(
        [
            (BAR_X, bar_y),
            (BAR_X + BAR_TOTAL_LEN, bar_y)
        ],
        fill="black",
        width=6
    )

    draw.line(
        [
            (BAR_X, bar_y),
            (BAR_X + BAR_RED_LEN, bar_y)
        ],
        fill=accent,
        width=6
    )

    # =========================
    # HEART ICON
    # =========================

    heart_symbol = "♡゙"

    try:

        heart_font = ImageFont.truetype(
            "VISHALMUSIC/assets/thumb/font2.ttf",
            26
        )

    except:
        heart_font = ImageFont.load_default()

    heart_x = BAR_X + BAR_RED_LEN - 10
    heart_y = bar_y - 30

    draw.text(
        (heart_x, heart_y),
        heart_symbol,
        fill=accent,
        font=heart_font
    )

    # =========================
    # TIME TEXT
    # =========================

    draw.text(
        (BAR_X, bar_y + 15),
        "00:00",
        fill="black",
        font=regular_font
    )

    end_text = (
        "Live"
        if is_live
        else duration_text
    )

    draw.text(
        (BAR_X + BAR_TOTAL_LEN - 90, bar_y + 15),
        end_text,
        fill=accent,
        font=regular_font
    )

    # =========================
    # ICONS
    # =========================

    icons_path = "VISHALMUSIC/assets/thumb/play_icons.png"

    if os.path.isfile(icons_path):

        ic = Image.open(icons_path).resize(
            (ICONS_W, ICONS_H)
        ).convert("RGBA")

        ic_gray = ic.convert("L")

        ic_colored = ImageOps.colorize(
            ic_gray,
            black="black",
            white=f"rgb{accent}"
        ).convert("RGBA")

        ic_colored.putalpha(
            ic.split()[-1]
        )

        bg.paste(
            ic_colored,
            (ICONS_X, ICONS_Y),
            ic_colored
        )

    # =========================
    # SAVE
    # =========================

    bg.save(cache_path)

    # =========================
    # CLEANUP
    # =========================

    try:
        os.remove(thumb_path)
    except:
        pass

    try:
        os.remove(anime_path)
    except:
        pass

    return cache_path
