import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from datetime import datetime
import re

@Client.on_message(filters.command("appletv") & filters.private)
async def appletv_poster(client: Client, message):
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

        # Poster image
        poster_url = soup.find("meta", property="og:image").get("content")

        # Title
        title_text = soup.find("meta", property="og:title").get("content")
        # Remove "- Apple TV" and any weird characters
        title_clean = re.split(r"\s*-\s*Apple TV", title_text, flags=re.I)[0].replace("\xa0", " ").strip()

        # Year
        release_date_tag = soup.find("meta", property="og:video:release_date")
        if release_date_tag:
            try:
                year = datetime.fromisoformat(release_date_tag.get("content").replace("Z", "")).year
            except:
                year = "Unknown"
        else:
            year = "Unknown"

        final_title = f"{title_clean} ({year})"

        await message.reply_text(f"{poster_url}\n\n{final_title}")

    except Exception as e:
        await message.reply_text(f"❌ Error occurred:\n`{str(e)}`")
