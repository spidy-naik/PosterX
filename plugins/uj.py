from pyrogram import Client, filters
from pyrogram.types import Message
import requests
from bs4 import BeautifulSoup
import re

def get_ultrajhakass_details(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    # Title
    title_tag = soup.find("h1", class_="content-title")
    title = title_tag.get_text(strip=True) if title_tag else None

    # Year
    sub_detail = soup.find("div", class_="content-sub-detail")
    year = None
    if sub_detail:
        year_match = re.search(r"\b(19|20)\d{2}\b", sub_detail.get_text())
        if year_match:
            year = year_match.group(0)

    # Poster
    video_tag = soup.find("video")
    poster = video_tag.get("poster") if video_tag else None

    return {"title": title, "year": year, "poster": poster}

@Client.on_message(filters.command("ultra") & filters.private)
async def ultra_handler(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage:\n`/ultra <UltraJhakass Movie URL>`", quote=True)

    url = message.command[1].strip()
    details = get_ultrajhakass_details(url)

    if not details["poster"]:
        return await message.reply("❌ Poster not found!", quote=True)

    caption = f"🎬 **{details['title']}** ({details['year']})"
    try:
        await message.reply_photo(details["poster"], caption=caption)
    except Exception as e:
        await message.reply(f"⚠️ Error sending poster: {e}", quote=True)
