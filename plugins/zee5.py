import requests
from bs4 import BeautifulSoup
import json
from pyrogram import Client, filters
from pyrogram.types import Message
import re
from datetime import datetime

@Client.on_message(filters.command("zee5") & filters.private)
async def zee5_poster(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "❌ Please send a valid ZEE5 URL.\nExample:\n`/zee5 https://www.zee5.com/movies/details/tehran/...`"
        )

    url = message.command[1]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/139.0.0.0 Safari/537.36"
    }

    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            return await message.reply_text(f"❌ Failed to fetch page, status code: {r.status_code}")

        soup = BeautifulSoup(r.text, "html.parser")

        # Extract JSON from <script id="videoObject">
        script_tag = soup.find("script", id="videoObject")
        if not script_tag:
            return await message.reply_text("❌ Could not find movie JSON data.")

        data = json.loads(script_tag.string)
        
        title = data.get("name", [{}])[0].get("@value", "Unknown Title")
        description = data.get("description", [{}])[0].get("@value", "")
        landscape = data.get("thumbnailUrl", [None])[0]
        page_url = data.get("contentUrl")
        embed_url = data.get("embedUrl")
        actors = ", ".join(data.get("actors", []))
        director = ", ".join(data.get("director", []))
        duration = data.get("duration", "Unknown")
        release_date = data.get("uploadDate", "Unknown")
        try:
            year = datetime.strptime(release_date, "%Y-%m-%d").year
        except:
            year = "Unknown"

        caption = f"🎬 **{title} ({year})**\n\n"
        caption += f"**Description:** {description}\n"
        caption += f"**Director:** {director}\n**Actors:** {actors}\n"
        caption += f"**Duration:** {duration}\n\n"
        caption += f"**Page URL:** {page_url}\n**Embed URL:** {embed_url}\n\n"
        caption += f"**Landscape Poster:** {landscape}"

        await message.reply_text(caption)

    except Exception as e:
        await message.reply_text(f"❌ Error occurred:\n`{str(e)}`")
