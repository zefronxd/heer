import os
import io
import re
import time
import asyncio
import datetime
import html
import warnings
from zoneinfo import ZoneInfo
from typing import List

# Suppress warnings
warnings.filterwarnings('ignore', category=SyntaxWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from PIL import Image, ImageDraw, ImageFont

from VISHALMUSIC import app

# Configuration
TIMEZONE = os.environ.get("TIMEZONE", "Asia/Kolkata")
FONT_PATH = os.environ.get("FONT_PATH", "")
ALLOW_OUT_OF_TIME_REPLY = os.environ.get("ALLOW_OUT_OF_TIME_REPLY", "").strip().lower() == "true"

# Greeting patterns
GOODNIGHT_RE = re.compile(r"\b(good\s*night|goodnight|gn|nighty|nite)\b", re.IGNORECASE)
GOODMORNING_RE = re.compile(r"\b(good\s*morning|goodmorning|gm|morning|subah)\b", re.IGNORECASE)

def is_good_morning(dt_local: datetime.datetime) -> bool:
    return 4 <= dt_local.hour < 12

def is_good_night(dt_local: datetime.datetime) -> bool:
    return dt_local.hour >= 20 or dt_local.hour < 4

def generate_thumbnail(lines: List[str], username: str = "", width: int = 1280, height: int = 720) -> bytes:
    bg_top = (20, 20, 60)
    bg_bottom = (80, 10, 50)

    img = Image.new("RGBA", (width, height), bg_top)
    draw = ImageDraw.Draw(img)

    # Gradient background
    for y in range(height):
        ratio = y / (height - 1)
        r = int(bg_top[0] * (1 - ratio) + bg_bottom[0] * ratio)
        g = int(bg_top[1] * (1 - ratio) + bg_bottom[1] * ratio)
        b = int(bg_top[2] * (1 - ratio) + bg_bottom[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Dark box overlay
    box_margin = 60
    box = (box_margin, box_margin, width - box_margin, height - box_margin)
    overlay = Image.new("RGBA", (width, height))
    od = ImageDraw.Draw(overlay)
    od.rectangle(box, fill=(0, 0, 0, 110))
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    def load_font(size: int):
        try:
            if FONT_PATH and os.path.exists(FONT_PATH):
                return ImageFont.truetype(FONT_PATH, size)
            for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                      "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                      "/System/Library/Fonts/Helvetica.ttc",
                      "C:\\Windows\\Fonts\\Arial.ttf"]:
                if os.path.exists(p):
                    return ImageFont.truetype(p, size)
        except:
            pass
        return ImageFont.load_default()

    title_font = load_font(72)
    sub_font = load_font(40)
    small_font = load_font(28)

    def get_text_size(text, font):
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    center_x = width // 2
    total_text_height = 0
    line_heights = []
    fonts = [title_font if i == 0 else sub_font for i in range(len(lines))]
    
    for i, ln in enumerate(lines):
        w, h = get_text_size(ln, fonts[i])
        line_heights.append((w, h))
        total_text_height += h + 18
    
    start_y = (height - total_text_height) // 2
    y = start_y
    
    for i, ln in enumerate(lines):
        f = fonts[i]
        w, h = line_heights[i]
        x = center_x - w // 2
        draw.text((x + 3, y + 3), ln, font=f, fill=(0, 0, 0, 200))
        draw.text((x, y), ln, font=f, fill=(255, 240, 160, 255))
        y += h + 18

    if username:
        user_text = f"— {username}"
        w, h = get_text_size(user_text, font=small_font)
        draw.text((width - w - 40, height - h - 30), user_text, font=small_font, fill=(220, 220, 220, 200))

    out = io.BytesIO()
    img.convert("RGB").save(out, format="JPEG", quality=88)
    out.seek(0)
    return out.read()

async def make_and_send_thumbnail(message: Message, lines: List[str], caption_text: str):
    try:
        uname = ""
        uid = None
        if message.from_user:
            uid = message.from_user.id
            uname = message.from_user.first_name or ""
            if message.from_user.last_name:
                uname += " " + message.from_user.last_name
        uname = (uname or "VISHAL").strip()

        img_bytes = await asyncio.to_thread(generate_thumbnail, lines, uname)
        
        bot_username = app.username or "VISHALMUSIC_BOT"
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("✦ ᴅᴏᴡɴʟᴏᴀᴅ ɪᴍᴀɢᴇ", url=f"https://t.me/{bot_username}")
        ]])

        await message.reply_photo(photo=img_bytes, caption=caption_text, reply_markup=kb, disable_notification=True, parse_mode="html")
    except Exception as e:
        uname_safe = html.escape(uname if uname else "VISHAL")
        await message.reply_text(f"{html.escape(caption_text)}\n\n— {uname_safe}\n\n(⚠️ Error: {e})")

def build_caption_and_lines(kind: str, display_name_html: str):
    if kind == "goodnight":
        lines = ["❖ ɢᴏᴏᴅ ɴɪɢʜᴛ ❖", "sᴡᴇᴇᴛ ᴅʀᴇᴀᴍs"]
        caption = f"❖ ɢᴏᴏᴅ ɴɪɢʜᴛ ❖ sᴡᴇᴇᴛ ᴅʀᴇᴀᴍs\n\n❍   𐙚 ꒷꒦ ๋{display_name_html} ࣭ ꒷꒦ 🎟️ 💤\n\n❖ ɢᴏ ᴛᴏ ➥ sʟᴇᴇᴘ ᴇᴀʀʟʏ"
    else:
        lines = ["☀️ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ ☀️", "ʜᴀᴠᴇ ᴀ ʙʀɪɢʜᴛ ᴅᴀʏ"]
        caption = f"☀️ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ ☀️\n\n❍   𐙚 ꒷꒦ ๋{display_name_html} ࣭ ꒷꒦ 🎟️ ☕\n\n❖ ᴘʀᴀʏ ғᴏʀ ᴀ ɢᴏᴏᴅ ᴅᴀʏ"
    return lines, caption

# ========== MAIN HANDLER WITH PROPER GROUP AND PRIORITY ==========
# Using group=1 (lower number = higher priority)
# But we add filters to avoid blocking other handlers

@app.on_message(filters.text & ~filters.command(["goodnight", "goodmorning"]), group=1)
async def greet_detector_handler(client, message: Message):
    # Skip if message is from bot or has no text
    if not message.text or message.from_user and message.from_user.is_bot:
        return
    
    # IMPORTANT: Check if message is a command or has command prefix
    text = message.text.strip()
    if text.startswith('/'):
        return  # Don't process commands, let other handlers handle them
    
    # Check for media groups or other types
    if message.media_group_id:
        return  # Skip media groups
    
    try:
        msg_dt = message.date
        if msg_dt.tzinfo is None:
            msg_dt = msg_dt.replace(tzinfo=datetime.timezone.utc)
        local_dt = msg_dt.astimezone(ZoneInfo(TIMEZONE))
    except:
        local_dt = datetime.datetime.now(ZoneInfo(TIMEZONE))

    # Detect greetings
    is_gn = bool(GOODNIGHT_RE.search(text))
    is_gm = bool(GOODMORNING_RE.search(text))

    if not is_gn and not is_gm:
        return  # Not a greeting, exit early

    # Handle both matches
    if is_gn and is_gm:
        if is_good_night(local_dt):
            is_gm = False
        else:
            is_gn = False

    # Get user info
    uname = ""
    uid = None
    if message.from_user:
        uid = message.from_user.id
        uname = message.from_user.first_name or ""
        if message.from_user.last_name:
            uname += " " + message.from_user.last_name
    uname = uname.strip() or "VISHAL"

    # Build HTML mention
    if uid:
        display_html = f"<a href='tg://user?id={uid}'>{html.escape(uname)}</a>"
    else:
        display_html = html.escape(uname)

    # Send response
    if is_gn:
        if is_good_night(local_dt) or ALLOW_OUT_OF_TIME_REPLY:
            lines, caption = build_caption_and_lines("goodnight", display_html)
            await make_and_send_thumbnail(message, lines, caption)
        else:
            await message.reply_text(f"✨ {html.escape(uname)}, ye time thoda jaldi/der ho sakta hai, par phir bhi — ɢᴏᴏᴅ ɴɪɢʜᴛ! 🌙")
    elif is_gm:
        if is_good_morning(local_dt) or ALLOW_OUT_OF_TIME_REPLY:
            lines, caption = build_caption_and_lines("goodmorning", display_html)
            await make_and_send_thumbnail(message, lines, caption)
        else:
            await message.reply_text(f"🌤️ {html.escape(uname)}, abhi 'morning' ka exact time nahi hai, phir bhi — ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ!")

# ========== COMMAND HANDLERS WITH PROPER GROUPS ==========
# Using lower group number (1) for commands too, but they will be caught by command filter
# Important: These command handlers should run AFTER other bot handlers
# So we use group=2 (higher number = lower priority compared to group=1 if same filter)

@app.on_message(filters.command("goodnight"), group=2)
async def cmd_goodnight(client, message: Message):
    # Skip if from bot
    if message.from_user and message.from_user.is_bot:
        return
        
    try:
        msg_dt = message.date
        if msg_dt.tzinfo is None:
            msg_dt = msg_dt.replace(tzinfo=datetime.timezone.utc)
        local_dt = msg_dt.astimezone(ZoneInfo(TIMEZONE))
    except:
        local_dt = datetime.datetime.now(ZoneInfo(TIMEZONE))

    uname = ""
    uid = None
    if message.from_user:
        uid = message.from_user.id
        uname = message.from_user.first_name or ""
        if message.from_user.last_name:
            uname += " " + message.from_user.last_name
    uname = uname.strip() or "VISHAL"

    if uid:
        display_html = f"<a href='tg://user?id={uid}'>{html.escape(uname)}</a>"
    else:
        display_html = html.escape(uname)

    if is_good_night(local_dt) or ALLOW_OUT_OF_TIME_REPLY:
        lines, caption = build_caption_and_lines("goodnight", display_html)
        await make_and_send_thumbnail(message, lines, caption)
    else:
        await message.reply_text(f"{html.escape(uname)}, abhi night time nahi hai, par aap chaho toh main fir bhi bhej doon.\nUse /goodnight again anytime!")

@app.on_message(filters.command("goodmorning"), group=2)
async def cmd_goodmorning(client, message: Message):
    # Skip if from bot
    if message.from_user and message.from_user.is_bot:
        return
        
    try:
        msg_dt = message.date
        if msg_dt.tzinfo is None:
            msg_dt = msg_dt.replace(tzinfo=datetime.timezone.utc)
        local_dt = msg_dt.astimezone(ZoneInfo(TIMEZONE))
    except:
        local_dt = datetime.datetime.now(ZoneInfo(TIMEZONE))

    uname = ""
    uid = None
    if message.from_user:
        uid = message.from_user.id
        uname = message.from_user.first_name or ""
        if message.from_user.last_name:
            uname += " " + message.from_user.last_name
    uname = uname.strip() or "VISHAL"

    if uid:
        display_html = f"<a href='tg://user?id={uid}'>{html.escape(uname)}</a>"
    else:
        display_html = html.escape(uname)

    if is_good_morning(local_dt) or ALLOW_OUT_OF_TIME_REPLY:
        lines, caption = build_caption_and_lines("goodmorning", display_html)
        await make_and_send_thumbnail(message, lines, caption)
    else:
        await message.reply_text(f"{html.escape(uname)}, abhi morning ka time nahi hai — lekin /goodmorning se aap kabhi bhi bhej sakte ho!")
