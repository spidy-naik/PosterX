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

    # Extract JSON-LD script
    json_ld = soup.find("script", type="application/ld+json")
    if not json_ld:
        return await message.reply("❌ Hulu metadata not found!", quote=True)

    try:
        data = json.loads(json_ld.string)
        title = data.get("name", "Hulu Content")
        year = None
        if "releasedEvent" in data and data["releasedEvent"].get("startDate"):
            year = data["releasedEvent"]["startDate"].split("-")[0]

        # Get poster and convert to high-res JPEG
        poster = data.get("image", "")
        if poster:
            # Remove old format and size params
            poster = poster.split("&format=")[0].split("&size=")[0]
            poster = poster.replace("®ion=", "&region=")  # Fix the misinterpreted region
            poster += "&format=jpeg&size=3840x2160&region=US"
    except Exception as e:
        return await message.reply(f"❌ Failed to parse Hulu metadata: {e}", quote=True)

    # Final output
    msg = f"{poster}\n\n{title}"
    if year:
        msg += f" ({year})"

    await message.reply_text(msg, quote=True)
