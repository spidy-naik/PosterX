import json
import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from datetime import datetime

@Client.on_message(filters.command("appletv") & filters.private)
async def appletv_poster(client, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "❌ Please send a valid Apple TV movie URL.\nExample:\n`/appletv https://tv.apple.com/us/movie/manje-bistre/...`"
        )

    url = message.command[1]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/139.0.0.0 Safari/537.36"
    }

    try:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")

        # Extract JSON from script tag
        script_tag = soup.find("script", {"id": "schema:movie", "type": "application/ld+json"})
        movie_json = json.loads(script_tag.string)

        # Poster URL
        poster_url = movie_json.get("image")

        # Title
        title = movie_json.get("name", "Unknown Title")

        # Year
        date_published = movie_json.get("datePublished", "")
        try:
            year = datetime.fromisoformat(date_published.replace("Z", "")).year
        except:
            year = "Unknown"

        final_title = f"{title} ({year})"

        await message.reply_text(f"{poster_url}\n\n{final_title}")

    except Exception as e:
        await message.reply_text(f"❌ Error occurred:\n`{str(e)}`")
