import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime
import re

@Client.on_message(filters.command("appletv") & filters.private)
async def appletv_poster(client: Client, message: Message):
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
        if r.status_code != 200:
            return await message.reply_text(f"❌ Failed to fetch page, status code: {r.status_code}")

        soup = BeautifulSoup(r.text, "html.parser")

        # Poster image
        og_image = soup.find("meta", property="og:image")
        poster_url = og_image.get("content") if og_image else None
        if not poster_url:
            return await message.reply_text("❌ Poster not found.")

        # Title
        og_title = soup.find("meta", property="og:title")
        title_text = og_title.get("content") if og_title else "Unknown Title"
        title_clean = re.split(r"\s*-\s*Apple TV", title_text)[0].strip()

        # Year from release date
        release_date_tag = soup.find("meta", property="og:video:release_date")
        if release_date_tag:
            try:
                release_date = release_date_tag.get("content")
                year = datetime.fromisoformat(release_date.replace("Z", "")).year
            except:
                year = "Unknown"
        else:
            year = "Unknown"

        final_title = f"{title_clean} ({year})"

        # Reply with poster + title
        await message.reply_text(f"{poster_url}\n\n{final_title}")

    except Exception as e:
        await message.reply_text(f"❌ Error occurred:\n`{str(e)}`")
