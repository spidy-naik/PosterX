import httpx
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.types import Message


async def fetch_poster(url: str):
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            r = await client.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        # Extract og:image
        og_image = soup.find("meta", property="og:image")
        if og_image:
            return og_image.get("content")

        return None
    except Exception as e:
        return f"❌ Error: {e}"


@Client.on_message(filters.command("bms") & filters.private)
async def poster_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Send URL like:\n`/bms bms_url`")

    url = message.command[1]
    waiting = await message.reply_text("🔍 Fetching poster...")

    result = await fetch_poster(url)
    await waiting.delete()

    if not result:
        return await message.reply_text("❌ No poster found.")
    if isinstance(result, str):  # error case
        return await message.reply_text(result)

    # Send poster as photo
    try:
        await message.reply_photo(result)
    except:
        await message.reply_text(result)
