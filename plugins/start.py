from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
    user = message.from_user
    bot = await client.get_me()
    
    welcome_text = f"""
👋 Hello {user.mention}!

🤖 I am <b>{bot.first_name}</b>, your personal Poster Bot!

🔍 Send me a movie or series name and I’ll find posters, info, and more.

💡 You can also add me to your group for auto poster search.

Use the buttons below to get started!
"""

    await message.reply(welcome_text)