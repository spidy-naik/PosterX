import requests
from bs4 import BeautifulSoup
import re
from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command("airtel") & filters.private)
async def airtel_poster(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "❌ Please send a valid Airtel Xstream movie URL.\nExample:\n`/airtel https://www.airtelxstream.in/movies/jodi/...`"
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

        # Extract title
        og_title = soup.find("meta", property="og:title")
        title_text = og_title.get("content") if og_title else "Unknown Title"

        # Extract year
        year_match = re.search(r"(\d{4})", title_text)
        year = year_match.group(1) if year_match else "Unknown Year"

        # Clean title (remove "Full Movie Online" or "HD Movies" text)
        title_clean = re.sub(r"\s*-\s*Full Movie Online.*", "", title_text).strip()

        # Extract poster
        og_image = soup.find("meta", property="og:image")
        poster_url = og_image.get("content") if og_image else None
        if not poster_url:
            return await message.reply_text(f"❌ Poster not found for {title_clean}")

        # Output
        await message.reply_text(f"{poster_url}\n\n{title_clean} ({year})")

    except Exception as e:
        await message.reply_text(f"❌ Error occurred:\n`{str(e)}`")