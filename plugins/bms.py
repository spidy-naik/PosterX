import httpx
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.types import Message


async def fetch_poster(url: str):
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            r = await client.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        posters = []

        # Look for meta og:image (property or name)
        for tag in soup.find_all("meta", attrs={"property": "og:image"}):
            posters.append(tag.get("content"))
        for tag in soup.find_all("meta", attrs={"name": "og:image"}):
            posters.append(tag.get("content"))

        # Extra fallback: BookMyShow asset images
        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src")
            if src and "assets-in.bmscdn.com" in src:
                posters.append(src)

        posters = list(set([p for p in posters if p]))

        return posters if posters else None

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

    # Send all posters (deduplicated)
    for poster in result:
        try:
            await message.reply_photo(poster)
        except:
            await message.reply_text(poster)
