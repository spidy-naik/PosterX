from pyrogram import Client, filters
import httpx
import json
from bs4 import BeautifulSoup

@Client.on_message(filters.command("hulu"))
async def hulu_poster(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: /hulu <Hulu URL>", quote=True)

    url = message.command[1].strip()

    try:
        async with httpx.AsyncClient(timeout=10) as client_http:
            resp = await client_http.get(url)
            resp.raise_for_status()
            html = resp.text
    except Exception as e:
        return await message.reply(f"❌ Failed to fetch URL: {e}", quote=True)

    soup = BeautifulSoup(html, "html.parser")

    # Extract the JSON-LD script
    json_ld = soup.find("script", type="application/ld+json")
    if not json_ld:
        return await message.reply("❌ Hulu metadata not found!", quote=True)

    try:
        data = json.loads(json_ld.string)
        title = data.get("name", "Hulu Content")
        description = data.get("description", "")
        poster = data.get("image", "")
        # Year from releasedEvent.startDate
        year = None
        if "releasedEvent" in data and data["releasedEvent"].get("startDate"):
            year = data["releasedEvent"]["startDate"].split("-")[0]
    except Exception as e:
        return await message.reply(f"❌ Failed to parse Hulu metadata: {e}", quote=True)

    msg = f"**Title:** {title}\n"
    if year:
        msg += f"**Year:** {year}\n"
    msg += f"**Poster:** {poster}\n"
    if description:
        msg += f"**Description:** {description}"

    await message.reply_text(msg, quote=True)
