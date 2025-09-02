import httpx
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.types import Message


async def fetch_posters(url: str):
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            r = await client.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        posters = []

        # Try og:image
        og_image = soup.find("meta", property="og:image")
        if og_image:
            posters.append(og_image.get("content"))

        # Try JSON-LD (structured data)
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, dict) and "image" in data:
                    if isinstance(data["image"], list):
                        posters.extend(data["image"])
                    else:
                        posters.append(data["image"])
            except:
                continue

        # Extra fallback: find any BookMyShow asset images
        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src")
            if src and "assets-in.bmscdn.com" in src:
                posters.append(src)

        posters = list(set(posters))
        return posters if posters else None

    except Exception as e:
        return f"❌ Error: {e}"


@Client.on_message(filters.command("bms") & filters.private)
async def poster_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Send URL like:\n`/bms bms_url`")

    url = message.command[1]
    waiting = await message.reply_text("🔍 Fetching...")

    result = await fetch_posters(url)
    await waiting.delete()

    if not result:
        return await message.reply_text("❌ No posters found.")
    if isinstance(result, str):
        return await message.reply_text(result)

    for poster in result:
        try:
            await message.reply_photo(poster)
        except:
            await message.reply_text(poster)