from pyrogram import Client, filters
from pyrogram.types import Message
import requests
from bs4 import BeautifulSoup

@Client.on_message(filters.command("ultra") & filters.private)
async def ultra_handler(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❗ Usage:\n/ultra <UltraJhakaas Movie URL>")

    url = message.command[1].strip()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/140.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return await message.reply(f"❌ Failed to fetch page: {e}")

    soup = BeautifulSoup(response.text, "html.parser")

    # 🔎 Grab <video poster="...">
    video_tag = soup.find("video", {"id": "video"})
    poster = video_tag["poster"] if video_tag and video_tag.has_attr("poster") else None

    # 🔎 Title/year fallback from <title>
    page_title = soup.title.string if soup.title else "Unknown"
    # Example: "Twelve (2025) - UltraJhakaas"
    title = page_title.split(" - ")[0].strip()
    year = ""
    if "(" in title and ")" in title:
        year = title.split("(")[-1].replace(")", "").strip()
        title = title.split("(")[0].strip()

    if not poster:
        return await message.reply("❌ Poster not found!")

    caption = f"🎬 <b>{title}</b> {f'({year})' if year else ''}"
    await message.reply_photo(photo=poster, caption=caption)
