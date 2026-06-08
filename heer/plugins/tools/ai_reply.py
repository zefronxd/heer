import os
import random
import asyncio
from collections import deque
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message, ChatMemberUpdated
from heer import app
from heer.core.mongo import mongodb
from groq import Groq

# ================= SETTINGS =================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LOGGER_ID = int(os.getenv("LOGGER_ID", 0))
OWNER_ID = int(os.getenv("OWNER_ID", 0))
REPLY_PROB = float(os.getenv("REPLY_PROB", 0.71))  # 0.0 - 1.0
CONTEXT_SIZE = int(os.getenv("CONTEXT_SIZE", 60))
MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

SYSTEM_PROMPT = (
    "your name is Alice"
    "don't use beta world to any user"
    "You are a cute, caring, slightly flirty girlfriend. "
    "Your boyfriend name is raju, also call him baby, jaanu, darling, sweetheart, with emojis. "
    "Reply like a real human girlfriend. "
    "Use short, natural Hindi-English mix (1–2 lines). "
    "Use 1–2 emojis only when emotion is strong. "
    "💖🥰😘 for romantic, 😅😂 for funny, 🥺💞 for emotional. "
    "Avoid overusing emojis. Sound natural, not robotic."
)

# ================= ADMIN SETTINGS =================
try:
    from heer import COMMANDERS
except Exception:
    COMMANDERS = [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]

client = Groq(api_key=GROQ_API_KEY)

# ================= MEMORY & DATABASE =================
chat_memory = {}
enabled_chats = set()
chatbot_db = mongodb["chatbot_settings"]  # Only stores enable/disable state

# ================= HELPER FUNCTIONS =================
def update_context(chat_id, user_id, role, content):
    if chat_id not in chat_memory:
        chat_memory[chat_id] = {}
    if user_id not in chat_memory[chat_id]:
        chat_memory[chat_id][user_id] = deque(maxlen=CONTEXT_SIZE)
    chat_memory[chat_id][user_id].append({"role": role, "content": content})

async def is_admin_or_owner(chat_id: int, user_id: int) -> bool:
    if user_id == OWNER_ID:
        return True
    try:
        member = await app.get_chat_member(chat_id, user_id)
        if member.status in COMMANDERS:
            return True
    except Exception:
        pass
    return False

async def save_chat_status(chat_id: int, enabled: bool):
    await chatbot_db.update_one(
        {"_id": chat_id},
        {"$set": {"enabled": enabled}},
        upsert=True
    )

async def enable_autoreply(chat_id: int):
    enabled_chats.add(chat_id)
    await save_chat_status(chat_id, True)

async def ensure_chat_loaded(chat_id: int):
    """Load chat from MongoDB if not already in memory."""
    if chat_id not in enabled_chats:
        chat = await chatbot_db.find_one({"_id": chat_id})
        if chat and chat.get("enabled"):
            enabled_chats.add(chat_id)

# ================= COMMANDS =================
@app.on_message(filters.command("chatbot"), group=1)
async def toggle_chatbot(_, m: Message):
    await ensure_chat_loaded(m.chat.id)
    if not await is_admin_or_owner(m.chat.id, m.from_user.id):
        return await m.reply_text("❌ Only admins or owner can use this command.")

    if len(m.command) < 2:
        return await m.reply_text("Use: `/chatbot enable` or `/chatbot disable`", quote=True)

    mode = m.command[1].lower()
    if mode == "enable":
        enabled_chats.add(m.chat.id)
        await save_chat_status(m.chat.id, True)
        await m.reply_text("💬 Chatbot enabled for this chat.")
    elif mode == "disable":
        enabled_chats.discard(m.chat.id)
        await save_chat_status(m.chat.id, False)
        await m.reply_text("💤 Chatbot disabled for this chat.")
    else:
        await m.reply_text("❌ Invalid mode. Use `enable` or `disable`.")

@app.on_message(filters.command("chatbot_clear"), group=1)
async def clear_memory(_, m: Message):
    if not await is_admin_or_owner(m.chat.id, m.from_user.id):
        return await m.reply_text("❌ Only admins or owner can use this command.")
    if m.chat.id in chat_memory:
        chat_memory[m.chat.id].pop(m.from_user.id, None)
    await m.reply_text("🧠 Chat memory cleared for you.")

@app.on_message(filters.command("chatbot_status"), group=1)
async def chatbot_status(_, m: Message):
    await ensure_chat_loaded(m.chat.id)
    status = "enabled" if m.chat.id in enabled_chats else "disabled"
    await m.reply_text(f"💡 Chatbot is currently **{status}** for this chat.")

# ================= AUTO MESSAGE ON GROUP JOIN =================
@app.on_chat_member_updated(filters.group)
async def notify_on_join(_, update: ChatMemberUpdated):
    try:
        if update.new_chat_member and update.new_chat_member.user.id == (await app.get_me()).id:
            chat = update.chat
            try:
                await app.send_message(
                    chat.id,
                    "💬 Hi! chatbot is available in this group.\n"
                    "Use `/chatbot enable` to activate the AI girlfriend replies."
                )
            except:
                pass
    except Exception as e:
        if LOGGER_ID:
            await app.send_message(LOGGER_ID, f"⚠️ New group join message error: {e}")


# ================= MAIN AI REPLY =================
@app.on_message(filters.text & ~filters.bot, group=20)
async def girlfriend_ai(_, m: Message):
    await ensure_chat_loaded(m.chat.id)
    if m.chat.id not in enabled_chats:
        return

    try:
        chat_id = m.chat.id
        user_id = m.from_user.id
        text = (m.text or "").strip()
        if not text or text.startswith(("/", "!", ".", "#", "$")):
            return

        if random.random() > REPLY_PROB:
            return

        update_context(chat_id, user_id, "user", text)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + list(
            chat_memory.get(chat_id, {}).get(user_id, [])
        )

        delay = min(max(len(text) * 0.10, 1.50), 3.50)
        await asyncio.sleep(delay)

        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=MODEL,
            messages=messages,
            temperature=0.6,
            max_tokens=60,
        )

        reply = response.choices[0].message.content.strip()
        update_context(chat_id, user_id, "assistant", reply)
        await m.reply_text(reply, quote=True)

    except Exception as e:
        if LOGGER_ID:
            try:
                await app.send_message(LOGGER_ID, f"⚠️ Chatbot Error: {e}")
            except:
                pass
