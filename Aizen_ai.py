from groq import AsyncGroq
import logging
from collections import defaultdict, deque

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.constants import ChatAction, ChatType
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from groq import AsyncGroq


# ==========================================
# 1. CONFIGURATION
# ==========================================

BOT_TOKEN = "PASTE_NEW_TELEGRAM_TOKEN"
GROQ_API_KEY = "PASTE_NEW_GROQ_API_KEY"

MODEL = "openai/gpt-oss-120b"

if "PASTE_NEW" in BOT_TOKEN or "PASTE_NEW" in GROQ_API_KEY:
    raise ValueError("Add your new API credentials first.")

client = AsyncGroq(api_key=GROQ_API_KEY)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("AizenAI")


# ==========================================
# 2. CHARACTERS
# ==========================================

CHARACTERS = {
    "kakashi": {
        "name": "Kakashi",
        "personality": (
            "Calm, mysterious, intelligent, confident, "
            "witty and composed. Uses clever dry humour."
        )
    },

    "ren": {
        "name": "Ren",
        "personality": (
            "Quiet, intense, thoughtful, observant, "
            "reserved and confident."
        )
    },

    "aizen": {
        "name": "Aizen",
        "personality": (
            "Strategic, elegant, charismatic, intelligent, "
            "mysterious and authoritative."
        )
    },

    "yuki": {
        "name": "Yuki",
        "personality": (
            "Playful, cheerful, expressive, funny, "
            "caring and energetic."
        )
    },

    "yui": {
        "name": "Yui",
        "personality": (
            "Sweet, warm, humorous, supportive, "
            "cheerful and playful."
        )
    }
}


# ==========================================
# 3. USER DATA
# ==========================================

user_settings = {}

conversation_memory = defaultdict(
    lambda: deque(maxlen=20)
)


def get_settings(user_id):

    if user_id not in user_settings:

        user_settings[user_id] = {
            "character": "aizen",
            "language": "English with occasional Hinglish",
            "flash": False,
            "detailed": False,
            "emoji": True
        }

    return user_settings[user_id]


def memory_key(user_id, chat_id):

    return (user_id, chat_id)


# ==========================================
# 4. MAIN KEYBOARD
# ==========================================

def main_keyboard():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "🎭 Characters",
                callback_data="characters"
            ),
            InlineKeyboardButton(
                "⚙️ Settings",
                callback_data="settings"
            )
        ],

        [
            InlineKeyboardButton(
                "👤 My Profile",
                callback_data="profile"
            ),
            InlineKeyboardButton(
                "⚡ Flash Mode",
                callback_data="flash"
            )
        ],

        [
            InlineKeyboardButton(
                "🗑 Reset Chat",
                callback_data="reset"
            )
        ]

    ])


# ==========================================
# 5. CHARACTER KEYBOARD
# ==========================================

def character_keyboard():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "🥷 Kakashi",
                callback_data="char_kakashi"
            ),
            InlineKeyboardButton(
                "🌑 Ren",
                callback_data="char_ren"
            )
        ],

        [
            InlineKeyboardButton(
                "♟ Aizen",
                callback_data="char_aizen"
            )
        ],

        [
            InlineKeyboardButton(
                "🌸 Yuki",
                callback_data="char_yuki"
            ),
            InlineKeyboardButton(
                "🎀 Yui",
                callback_data="char_yui"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="home"
            )
        ]

    ])


# ==========================================
# 6. SETTINGS KEYBOARD
# ==========================================

def settings_keyboard():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "🌐 Language",
                callback_data="language"
            ),
            InlineKeyboardButton(
                "📝 Response Length",
                callback_data="length"
            )
        ],

        [
            InlineKeyboardButton(
                "😊 Emoji",
                callback_data="emoji"
            ),
            InlineKeyboardButton(
                "⚡ Flash Mode",
                callback_data="flash"
            )
        ],

        [
            InlineKeyboardButton(
                "🎭 Characters",
                callback_data="characters"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="home"
            )
        ]

    ])


# ==========================================
# 7. START COMMAND
# ==========================================

async def start(update, context):

    user = update.effective_user

    get_settings(user.id)

    await update.effective_message.reply_text(

        f"✦ Welcome to Aizen AI, {user.first_name}!\n\n"

        "Your personal AI experience starts here.\n\n"

        "Choose your character and customize "
        "your AI experience.",

        reply_markup=main_keyboard()

    )


# ==========================================
# 8. HELP COMMAND
# ==========================================

async def help_command(update, context):

    await update.effective_message.reply_text(

        """
✦ AIZEN AI COMMAND CENTER

/start - Start bot
/help - Show commands
/character - Select character
/settings - Personalization
/profile - Personal details
/flash - Toggle flash mode
/reset - Clear conversation
/ask - Ask AI in groups
/status - Bot status

GROUP BEHAVIOUR:
Mention the bot or reply to its message.
Ordinary group messages are ignored.
"""

    )


# ==========================================
# 9. CHARACTER COMMAND
# ==========================================

async def character_command(update, context):

    await update.effective_message.reply_text(

        "🎭 SELECT YOUR CHARACTER",

        reply_markup=character_keyboard()

    )


# ==========================================
# 10. SETTINGS COMMAND
# ==========================================

async def settings_command(update, context):

    await update.effective_message.reply_text(

        "⚙️ PERSONALIZATION SETTINGS",

        reply_markup=settings_keyboard()

    )


# ==========================================
# 11. PROFILE COMMAND
# ==========================================

async def profile_command(update, context):

    user = update.effective_user

    settings = get_settings(user.id)

    username = (
        f"@{user.username}"
        if user.username
        else "Not set"
    )

    await update.effective_message.reply_text(

        "👤 YOUR PROFILE\n\n"

        f"Name: {user.full_name}\n"
        f"Username: {username}\n"
        f"Telegram ID: {user.id}\n\n"

        f"Character: {CHARACTERS[settings['character']]['name']}\n"
        f"Language: {settings['language']}\n"
        f"Flash: {'ON' if settings['flash'] else 'OFF'}\n"
        f"Detailed: {'ON' if settings['detailed'] else 'OFF'}\n"
        f"Emoji: {'ON' if settings['emoji'] else 'OFF'}",

        reply_markup=main_keyboard()

    )


# ==========================================
# 12. RESET COMMAND
# ==========================================

async def reset_command(update, context):

    user = update.effective_user
    chat = update.effective_chat

    conversation_memory[
        memory_key(user.id, chat.id)
    ].clear()

    await update.effective_message.reply_text(
        "🗑 Your conversation has been reset."
    )


# ==========================================
# 13. FLASH COMMAND
# ==========================================

async def flash_command(update, context):

    settings = get_settings(update.effective_user.id)

    settings["flash"] = not settings["flash"]

    await update.effective_message.reply_text(

        "⚡ Flash Mode: "
        + ("ON" if settings["flash"] else "OFF")

    )


# ==========================================
# 14. STATUS COMMAND
# ==========================================

async def status_command(update, context):

    await update.effective_message.reply_text(

        "✦ AIZEN AI STATUS\n\n"
        "Backend: Online\n"
        "AI Engine: Groq\n"
        "Group Mode: Mention Only\n"
        "Characters: 5\n"
        "Memory: Active"

    )


# ==========================================
# 15. ASK COMMAND
# ==========================================

async def ask_command(update, context):

    if not context.args:

        await update.effective_message.reply_text(
            "Usage: /ask your question"
        )

        return

    await generate_response(
        update,
        context,
        " ".join(context.args)
    )


# ==========================================
# 16. CALLBACK HANDLER
# ==========================================

async def button_handler(update, context):

    query = update.callback_query

    await query.answer()

    user = query.from_user

    settings = get_settings(user.id)

    action = query.data

    if action == "home":

        await query.edit_message_text(
            "✦ AIZEN AI",
            reply_markup=main_keyboard()
        )

    elif action == "characters":

        await query.edit_message_text(
            "🎭 SELECT YOUR CHARACTER",
            reply_markup=character_keyboard()
        )

    elif action.startswith("char_"):

        character = action.replace("char_", "")

        if character not in CHARACTERS:
            return

        settings["character"] = character

        for key in list(conversation_memory.keys()):

            if key[0] == user.id:
                conversation_memory[key].clear()

        await query.edit_message_text(

            f"Character changed to "
            f"{CHARACTERS[character]['name']}!",

            reply_markup=main_keyboard()

        )

    elif action == "settings":

        await query.edit_message_text(
            "⚙️ PERSONALIZATION SETTINGS",
            reply_markup=settings_keyboard()
        )

    elif action == "profile":

        username = (
            f"@{user.username}"
            if user.username
            else "Not set"
        )

        await query.edit_message_text(

            "👤 YOUR PROFILE\n\n"
            f"Name: {user.full_name}\n"
            f"Username: {username}\n"
            f"Telegram ID: {user.id}\n"
            f"Character: {CHARACTERS[settings['character']]['name']}",

            reply_markup=main_keyboard()

        )

    elif action == "flash":

        settings["flash"] = not settings["flash"]

        await query.edit_message_text(

            "⚡ Flash Mode: "
            + ("ON" if settings["flash"] else "OFF"),

            reply_markup=settings_keyboard()

        )

    elif action == "length":

        settings["detailed"] = not settings["detailed"]

        await query.edit_message_text(

            "📝 Response Length: "
            + ("Detailed" if settings["detailed"] else "Short"),

            reply_markup=settings_keyboard()

        )

    elif action == "language":

        settings["language"] = (

            "English only"
            if settings["language"] != "English only"
            else "English with occasional Hinglish"

        )

        await query.edit_message_text(

            f"🌐 Language: {settings['language']}",

            reply_markup=settings_keyboard()

        )

    elif action == "emoji":

        settings["emoji"] = not settings["emoji"]

        await query.edit_message_text(

            "😊 Emoji: "
            + ("ON" if settings["emoji"] else "OFF"),

            reply_markup=settings_keyboard()

        )

    elif action == "reset":

        conversation_memory[
            memory_key(user.id, query.message.chat_id)
        ].clear()

        await query.edit_message_text(

            "🗑 Conversation memory cleared.",

            reply_markup=main_keyboard()

        )


# ==========================================
# 17. AI RESPONSE ENGINE
# ==========================================

async def generate_response(update, context, user_message):

    user = update.effective_user

    chat = update.effective_chat

    settings = get_settings(user.id)

    character = CHARACTERS[settings["character"]]

    key = memory_key(user.id, chat.id)

    if settings["flash"]:

        response_style = "Reply in one or two concise sentences."

    elif settings["detailed"]:

        response_style = "Give a detailed and organized response."

    else:

        response_style = "Keep replies short and natural."

    emoji_style = (
        "Use emojis naturally."
        if settings["emoji"]
        else "Do not use emojis."
    )

    system_prompt = f"""
You are {character['name']}, an AI character inside Aizen AI.

Personality:
{character['personality']}

Rules:
- Use {settings['language']}.
- {response_style}
- {emoji_style}
- Be expressive and conversational.
- Use playful teasing and harmless dramatic humour.
- Keep interactions age-appropriate and non-romantic.
- Never claim to be a human.
- Never expose API credentials or private data.
- Answer questions about your AI provider truthfully.
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    messages.extend(list(conversation_memory[key]))

    messages.append({
        "role": "user",
        "content": user_message
    })

    try:

        await context.bot.send_chat_action(
            chat_id=chat.id,
            action=ChatAction.TYPING
        )

        completion = await client.chat.completions.create(

            model=MODEL,

            messages=messages,

            temperature=0.8,

            max_tokens=1200 if settings["detailed"] else 350

        )

        answer = completion.choices[0].message.content

        if not answer:
            answer = "I couldn't generate a response. Try again."

        conversation_memory[key].append({
            "role": "user",
            "content": user_message
        })

        conversation_memory[key].append({
            "role": "assistant",
            "content": answer
        })

        await update.effective_message.reply_text(answer)

    except Exception:

        logger.exception("AI response failed")

        await update.effective_message.reply_text(
            "⚠️ AI service is temporarily unavailable."
        )


# ==========================================
# 18. GROUP AND PRIVATE CHAT HANDLER
# ==========================================

async def chat_handler(update, context):

    message = update.effective_message

    user = update.effective_user

    chat = update.effective_chat

    if not message or not message.text or not user:
        return

    if user.is_bot:
        return

    user_message = message.text

    if chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):

        bot_info = await context.bot.get_me()

        bot_mention = f"@{bot_info.username}".lower()

        mentioned = any(

            entity.type == "mention"

            and user_message[
                entity.offset:entity.offset + entity.length
            ].lower() == bot_mention

            for entity in (message.entities or [])

        )

        replied_to_bot = (

            message.reply_to_message is not None

            and message.reply_to_message.from_user is not None

            and message.reply_to_message.from_user.id == bot_info.id

        )

        if not mentioned and not replied_to_bot:
            return

        user_message = user_message.replace(
            f"@{bot_info.username}",
            ""
        ).strip()

        if not user_message:

            await message.reply_text(
                "Yes? What can I help you with?"
            )

            return

    await generate_response(
        update,
        context,
        user_message
    )


# ==========================================
# 19. ERROR HANDLER
# ==========================================

async def error_handler(update, context):

    logger.error(
        "Update processing error",
        exc_info=context.error
    )


# ==========================================
# 20. START APPLICATION
# ==========================================

def main():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("character", character_command))
    app.add_handler(CommandHandler("settings", settings_command))
    app.add_handler(CommandHandler("profile", profile_command))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CommandHandler("flash", flash_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("ask", ask_command))

    app.add_handler(CallbackQueryHandler(button_handler))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            chat_handler
        )
    )

    app.add_error_handler(error_handler)

    print("====================================")
    print("          AIZEN AI 2.0")
    print("          STATUS: ONLINE")
    print("          GROUP MODE: MENTION")
    print("====================================")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
