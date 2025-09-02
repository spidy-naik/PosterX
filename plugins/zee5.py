import re
import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime

@Client.on_message(filters.command("zee5") & filters.private)
async def zee5_poster(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "❌ Please send a valid ZEE5 URL.\nExample:\n`/zee5 https://www.zee5.com/movies/details/tehran/...`"
        )

    url = message.command[1]

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/139.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return await message.reply_text(f"❌ Failed to fetch page. Status code: {response.status_code}")

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract title from twitter:title
        title_tag = soup.find("meta", attrs={"name": "twitter:title"})
        title_text = title_tag.get("content") if title_tag else "Unknown Title"

        # Extract release year from title
        year_match = re.search(r"\((\d{4})\)", title_text)
        year = year_match.group(1) if year_match else "Unknown Year"

        # Extract landscape poster from twitter:image
        poster_tag = soup.find("meta", attrs={"name": "twitter:image"})
        landscape = poster_tag.get("content") if poster_tag else None

        # Optionally, portrait poster (some ZEE5 pages may have it in img src containing "portrait")
        portrait_img = soup.find("img", src=re.compile(r"portrait"))
        portrait = portrait_img.get("src") if portrait_img else None

        if not landscape and not portrait:
            return await message.reply_text("❌ No posters found.")

        caption = f"🎬 **{title_text}** ({year})\n\n"
        if landscape:
            caption += f"**Landscape Poster:**\n{landscape}\n\n"
        if portrait:
            caption += f"**Portrait Poster:**\n{portrait}\n\n"
        caption += "cc: @SpeXmen"

        await message.reply_text(caption)

    except Exception as e:
        await message.reply_text(f"❌ Error occurred:\n`{str(e)}`")
