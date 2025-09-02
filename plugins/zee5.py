import requests
from bs4 import BeautifulSoup
import json
from pyrogram import Client, filters
from pyrogram.types import Message
import re
from datetime import datetime

@Client.on_message(filters.command("zee") & filters.private)
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
        release_date = data.get("uploadDate", "Unknown")
        try:
            year = datetime.strptime(release_date, "%Y-%m-%d").year
        except:
            year = "Unknown"

        # Extract poster and clean URL
        poster_url = data.get("thumbnailUrl", [None])[0]
        if not poster_url:
            return await message.reply_text("❌ Poster not found.")

        # Clean poster URL to remove size/format parameters
        match = re.search(r"(\/resources\/.*)", poster_url)
        if match:
            clean_poster = f"https://akamaividz2.zee5.com/image/upload{match.group(1)}"
        else:
            clean_poster = poster_url  # fallback

        # Reply
        await message.reply_text(f"{clean_poster}\n\n{title} ({year})")

    except Exception as e:
        await message.reply_text(f"❌ Error occurred:\n`{str(e)}`")