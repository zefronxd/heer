import os
import io
import re
import random
import asyncio
import datetime
import html

from zoneinfo import ZoneInfo

from pyrogram import filters, enums
from pyrogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from PIL import (
    Image,
    ImageDraw,
    ImageFont,
    ImageFilter
)

from VISHALMUSIC import app

# =========================================================
# CONFIG
# =========================================================

TIMEZONE = os.environ.get(
    "TIMEZONE",
    "Asia/Kolkata"
)

FONT_PATH = os.environ.get(
    "FONT_PATH",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
)

ALLOW_OUT_OF_TIME_REPLY = bool(
    os.environ.get(
        "ALLOW_OUT_OF_TIME_REPLY",
        ""
    ).strip()
)

# =========================================================
# SMART TEXTS
# =========================================================

SMART_MORNING_LINES = [

    "☀️ ʀɪsᴇ ᴀɴᴅ sʜɪɴᴇ",
    "🌸 ɴᴇᴡ ᴍᴏʀɴɪɴɢ ɴᴇᴡ ᴠɪʙᴇ",
    "✨ ᴇɴᴊᴏʏ ʏᴏᴜʀ ᴅᴀʏ",
    "☕ sᴛᴀʏ ᴘᴏsɪᴛɪᴠᴇ",
    "🌤️ ᴋᴇᴇᴘ sᴍɪʟɪɴɢ",
    "💛 ʙᴇᴀᴜᴛɪғᴜʟ ᴍᴏʀɴɪɴɢ",
    "🌿 ɢᴏᴏᴅ ᴠɪʙᴇs ᴏɴʟʏ",
    "🌞 ᴍᴏʀɴɪɴɢ ᴠɪʙᴇs ᴏɴʟʏ",
    "🦋 ʜᴀᴘᴘʏ ᴍᴏʀɴɪɴɢ sᴏᴜʟ",
    "🌈 sᴛᴀʀᴛ ᴛᴏᴅᴀʏ ᴡɪᴛʜ ʜᴏᴘᴇ",
    "🌼 ᴇɴᴊᴏʏ ᴛʜᴇ ʙᴇᴀᴜᴛɪғᴜʟ ᴍᴏʀɴɪɴɢ",
    "💫 ᴍᴏʀɴɪɴɢ ᴍᴀɢɪᴄ ɪs ʜᴇʀᴇ",
]

SMART_NIGHT_LINES = [

    "🌙 sʟᴇᴇᴘ ᴘᴇᴀᴄᴇғᴜʟʟʏ",
    "✨ sᴡᴇᴇᴛ ᴅʀᴇᴀᴍs",
    "💫 ᴛɪᴍᴇ ᴛᴏ ʀᴇʟᴀx",
    "🌌 ʜᴀᴠᴇ ᴀ ᴄᴀʟᴍ ɴɪɢʜᴛ",
    "😴 ʀᴇsᴛ ᴡᴇʟʟ",
    "🌃 ɢᴏᴏᴅ ɴɪɢʜᴛ ᴠɪʙᴇs",
    "🖤 ᴘᴇᴀᴄᴇғᴜʟ sᴏᴜʟ",
    "🌠 ᴅʀᴇᴀᴍs ᴀʀᴇ ᴄᴀʟʟɪɴɢ",
    "🌌 ɴɪɢʜᴛ sᴋʏ ʟᴏᴏᴋs ʙᴇᴀᴜᴛɪғᴜʟ",
    "🌙 ᴛᴏᴍᴏʀʀᴏᴡ ɪs ᴀ ɴᴇᴡ sᴛᴀʀᴛ",
    "💤 ᴄʟᴏsᴇ ʏᴏᴜʀ ᴇʏᴇs ᴀɴᴅ ʀᴇsᴛ",
    "🦋 ᴘᴇᴀᴄᴇғᴜʟ ɴɪɢʜᴛ ᴛᴏ ʏᴏᴜ",
]

MORNING_SUBTEXTS = [

    "ʜᴀᴠᴇ ᴀ ɢʀᴇᴀᴛ ᴅᴀʏ",
    "sᴍɪʟᴇ ᴀɴᴅ sʜɪɴᴇ",
    "ᴋᴇᴇᴘ ᴇɴᴊᴏʏɪɴɢ",
    "sᴛᴀʏ ʜᴀᴘᴘʏ",
    "ᴘᴏsɪᴛɪᴠᴇ ᴠɪʙᴇs",
    "ᴍᴀᴋᴇ ᴛᴏᴅᴀʏ sᴘᴇᴄɪᴀʟ",
    "ᴠɪʙᴇ ᴡɪᴛʜ ᴘᴇᴀᴄᴇ",
]

NIGHT_SUBTEXTS = [

    "sᴡᴇᴇᴛ ᴅʀᴇᴀᴍs",
    "ᴛᴀᴋᴇ ᴄᴀʀᴇ",
    "ʀᴇsᴛ ᴡᴇʟʟ",
    "sʟᴇᴇᴘ ᴘᴇᴀᴄᴇғᴜʟʟʏ",
    "ᴄᴀʟᴍ ɴɪɢʜᴛ",
    "ᴅʀᴇᴀᴍ ʙɪɢ",
    "ʀᴇʟᴀx ʏᴏᴜʀ ᴍɪɴᴅ",
]

WRONG_TIME_MORNING_REPLIES = [

    "🌚 ʙʜᴀɪ ᴀʙʜɪ ᴍᴏʀɴɪɴɢ ɴᴀʜɪ ʜᴜɪ",
    "😂 ᴀʟᴀʀᴍ ᴀʙʜɪ ʙᴀᴊᴀ ᴋʏᴀ",
    "☀️ ᴛɪᴍᴇ ᴄʜᴇᴄᴋ ᴋᴀʀ ʟᴏ",
    "🤣 ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ.ᴇxᴇ ᴄʀᴀsʜᴇᴅ",
    "📢 ᴍᴏʀɴɪɴɢ sᴇʀᴠᴇʀ ᴏғғʟɪɴᴇ ʜᴀɪ",
    "🌙 ᴄʜᴀɴᴅ ᴅᴇᴋʜᴏ sᴜʀᴀᴊ ɴᴀʜɪ",
]

WRONG_TIME_NIGHT_REPLIES = [

    "☀️ ᴀʙʜɪ ɢᴏᴏᴅ ɴɪɢʜᴛ ɴᴀʜɪ ʜᴜᴀ",
    "😂 ᴅɪɴ ᴍᴇ sᴏ ᴊᴀᴏɢᴇ ᴋʏᴀ",
    "🌞 ɴɪɢʜᴛ ᴍᴏᴅᴇ ᴏғғ ʜᴀɪ",
    "🤣 ᴀʙʜɪ ᴘᴀʀᴛʏ ᴛɪᴍᴇ ʜᴀɪ",
    "📢 ɢᴏᴏᴅ ɴɪɢʜᴛ ᴘᴏsᴛᴘᴏɴᴇᴅ",
    "🌤️ ᴅɪɴ ᴍᴇ ᴋᴀᴜɴ sᴏᴛᴀ ʜᴀɪ",
]

AESTHETIC_EMOJIS = [
    "✨", "🌸", "☁️", "💫",
    "🌙", "☀️", "🦋", "🌿"
]

# =========================================================
# REGEX
# =========================================================

GOODNIGHT_RE = re.compile(
    r"\b(good\s*night|goodnight|gn|nighty|nite)\b",
    re.IGNORECASE
)

GOODMORNING_RE = re.compile(
    r"\b(good\s*morning|goodmorning|gm|morning|subah)\b",
    re.IGNORECASE
)

# =========================================================
# TIME CHECK
# =========================================================

def is_good_morning(dt_local):
    return 4 <= dt_local.hour < 12


def is_good_night(dt_local):
    return dt_local.hour >= 20 or dt_local.hour < 4

# =========================================================
# FONT
# =========================================================

def load_font(size):

    try:

        if FONT_PATH and os.path.exists(FONT_PATH):

            return ImageFont.truetype(
                FONT_PATH,
                size
            )

    except Exception:
        pass

    return ImageFont.load_default()

# =========================================================
# SMART TEXT
# =========================================================

def generate_smart_text(
    is_morning=True
):

    emoji = random.choice(
        AESTHETIC_EMOJIS
    )

    if is_morning:

        main = random.choice(
            SMART_MORNING_LINES
        )

        sub = random.choice(
            MORNING_SUBTEXTS
        )

    else:

        main = random.choice(
            SMART_NIGHT_LINES
        )

        sub = random.choice(
            NIGHT_SUBTEXTS
        )

    title = f"{emoji} {main} {emoji}"

    return [title, sub]

# =========================================================
# BACKGROUND
# =========================================================

def create_random_nature_background(
    width,
    height
):

    styles = [

        ((255, 153, 102), (255, 94, 98)),
        ((36, 198, 220), (81, 74, 157)),
        ((67, 67, 151), (191, 64, 191)),
        ((17, 153, 142), (56, 239, 125)),
        ((20, 20, 20), (70, 70, 70)),
        ((255, 126, 179), (255, 195, 113)),
    ]

    top, bottom = random.choice(styles)

    img = Image.new(
        "RGB",
        (width, height)
    )

    draw = ImageDraw.Draw(img)

    for y in range(height):

        ratio = y / height

        r = int(
            top[0] * (1 - ratio)
            + bottom[0] * ratio
        )

        g = int(
            top[1] * (1 - ratio)
            + bottom[1] * ratio
        )

        b = int(
            top[2] * (1 - ratio)
            + bottom[2] * ratio
        )

        draw.line(
            [(0, y), (width, y)],
            fill=(r, g, b)
        )

    for _ in range(60):

        x = random.randint(0, width)
        y = random.randint(0, height)

        radius = random.randint(40, 180)

        color = (

            random.randint(150, 255),
            random.randint(150, 255),
            random.randint(150, 255)
        )

        draw.ellipse(
            (
                x - radius,
                y - radius,
                x + radius,
                y + radius
            ),
            fill=color
        )

    img = img.filter(
        ImageFilter.GaussianBlur(12)
    )

    return img

# =========================================================
# IMAGE GENERATOR
# =========================================================

def generate_thumbnail(
    lines
):

    width = 1280
    height = 720

    img = create_random_nature_background(
        width,
        height
    )

    overlay = Image.new(
        "RGBA",
        (width, height),
        (0, 0, 0, 70)
    )

    img = Image.alpha_composite(
        img.convert("RGBA"),
        overlay
    )

    draw = ImageDraw.Draw(img)

    title_font = load_font(70)
    sub_font = load_font(42)
    small_font = load_font(30)

    fonts = [

        title_font if i == 0
        else sub_font

        for i in range(len(lines))
    ]

    total_height = 0
    sizes = []

    for i, line in enumerate(lines):

        bbox = draw.textbbox(
            (0, 0),
            line,
            font=fonts[i]
        )

        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        sizes.append((w, h))

        total_height += h + 25

    y = (height - total_height) // 2

    for i, line in enumerate(lines):

        w, h = sizes[i]

        x = (width - w) // 2

        draw.text(
            (x + 4, y + 4),
            line,
            font=fonts[i],
            fill=(0, 0, 0)
        )

        draw.text(
            (x, y),
            line,
            font=fonts[i],
            fill=(255, 255, 255)
        )

        y += h + 25

    footer = "ᴍᴜꜱɪᴄ"

    bbox = draw.textbbox(
        (0, 0),
        footer,
        font=small_font
    )

    fw = bbox[2] - bbox[0]
    fh = bbox[3] - bbox[1]

    draw.text(
        (
            width - fw - 40,
            height - fh - 30
        ),
        footer,
        font=small_font,
        fill=(255, 255, 255)
    )

    out = io.BytesIO()

    img.convert("RGB").save(
        out,
        format="JPEG",
        quality=95
    )

    out.seek(0)

    return out.read()

# =========================================================
# SEND IMAGE
# =========================================================

async def make_and_send_thumbnail(
    message,
    lines,
    caption
):

    try:

        img_bytes = await asyncio.to_thread(
            generate_thumbnail,
            lines
        )

        photo = io.BytesIO(img_bytes)

        photo.name = "greeting.jpg"

        kb = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "✨ ᴍᴜꜱɪᴄ ✨",
                        url=f"https://t.me/{app.username or ''}"
                    )
                ]
            ]
        )

        await message.reply_photo(
            photo=photo,
            caption=caption,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=kb
        )

    except Exception as e:

        await message.reply_text(
            f"⚠️ Error:\n{e}"
        )

# =========================================================
# FUNNY REPLY
# =========================================================

async def send_funny_reply(
    message,
    text
):

    funny_lines = [

        "😂 ᴛɪᴍɪɴɢ ᴡʀᴏɴɢ",
        text
    ]

    caption = (

        f"{funny_lines[0]}\n\n"
        f"{funny_lines[1]}"
    )

    await make_and_send_thumbnail(
        message,
        funny_lines,
        caption
    )

# =========================================================
# MAIN HANDLER
# =========================================================

@app.on_message(

    filters.text
    & ~filters.command([
        "goodmorning",
        "goodnight"
    ])
    & ~filters.edited,

    group=10
)
async def greet_detector_handler(
    client,
    message: Message
):

    if not message.text:
        return

    text = message.text.strip()

    if text.startswith("/"):
        return

    if (
        message.from_user
        and message.from_user.is_bot
    ):
        return

    try:

        msg_dt = message.date

        if msg_dt.tzinfo is None:

            msg_dt = msg_dt.replace(
                tzinfo=datetime.timezone.utc
            )

        local_dt = msg_dt.astimezone(
            ZoneInfo(TIMEZONE)
        )

    except Exception:

        local_dt = datetime.datetime.now(
            ZoneInfo(TIMEZONE)
        )

    is_gm = bool(
        GOODMORNING_RE.search(text)
    )

    is_gn = bool(
        GOODNIGHT_RE.search(text)
    )

    if not is_gm and not is_gn:
        return

    uname = "User"
    uid = None

    if message.from_user:

        uid = message.from_user.id

        uname = (
            message.from_user.first_name
            or "User"
        )

    if uid:

        display_html = (
            f"<a href='tg://user?id={uid}'>"
            f"{html.escape(uname)}</a>"
        )

    else:

        display_html = html.escape(uname)

    # =====================================================
    # GOOD MORNING
    # =====================================================

    if is_gm:

        if (
            is_good_morning(local_dt)
            or ALLOW_OUT_OF_TIME_REPLY
        ):

            lines = generate_smart_text(
                is_morning=True
            )

            caption = (

                f"{lines[0]}\n\n"
                f"❍ 𐙚 {display_html} ☕\n\n"
                f"{lines[1]}"
            )

            await make_and_send_thumbnail(
                message,
                lines,
                caption
            )

        else:

            funny = random.choice(
                WRONG_TIME_MORNING_REPLIES
            )

            await send_funny_reply(
                message,
                funny
            )

    # =====================================================
    # GOOD NIGHT
    # =====================================================

    elif is_gn:

        if (
            is_good_night(local_dt)
            or ALLOW_OUT_OF_TIME_REPLY
        ):

            lines = generate_smart_text(
                is_morning=False
            )

            caption = (

                f"{lines[0]}\n\n"
                f"❍ 𐙚 {display_html} 🌙\n\n"
                f"{lines[1]}"
            )

            await make_and_send_thumbnail(
                message,
                lines,
                caption
            )

        else:

            funny = random.choice(
                WRONG_TIME_NIGHT_REPLIES
            )

            await send_funny_reply(
                message,
                funny
            )

# =========================================================
# COMMANDS
# =========================================================

@app.on_message(
    filters.command("goodmorning")
)
async def cmd_gm(
    client,
    message: Message
):

    lines = generate_smart_text(
        is_morning=True
    )

    await make_and_send_thumbnail(
        message,
        lines,
        f"{lines[0]}\n\n{lines[1]}"
    )


@app.on_message(
    filters.command("goodnight")
)
async def cmd_gn(
    client,
    message: Message
):

    lines = generate_smart_text(
        is_morning=False
    )

    await make_and_send_thumbnail(
        message,
        lines,
        f"{lines[0]}\n\n{lines[1]}"
    )
