from pyrogram import Client, filters
from pyrogram.types import Message
import requests
from bs4 import BeautifulSoup
import re

@Client.on_message(filters.command("prime") & filters.private)
async def prime_poster_scraper(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Please provide a Prime Video link.\n\nExample:\n<code>/prime https://www.primevideo.com/detail/XYZ</code>")

    url = message.command[1]
    if "primevideo.com/detail/" not in url:
        return await message.reply("❌ Invalid URL. Make sure it’s a Prime Video detail link.")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive"
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        # 🎬 Title
        raw_title = soup.title.string if soup.title else "Unknown Title"
        clean_title = raw_title.replace("Prime Video:", "").strip()

        # 📅 Release Year
        release_year = None
        for tag in soup.find_all(["span", "li", "div"]):
            if tag.string and re.search(r'\b(19|20)\d{2}\b', tag.string):
                match = re.search(r'\b(19|20)\d{2}\b', tag.string)
                if match:
                    release_year = match.group()
                    break

        # 📀 Season Info
        season = None
        for tag in soup.find_all(["span", "div"]):
            if tag.string and re.search(r"Season\s*\d+", tag.string, re.IGNORECASE):
                season = re.search(r"(Season\s*\d+)", tag.string, re.IGNORECASE).group(1)
                break

        # 🖼 Posters
        target_script = None
        for script in soup.find_all("script"):
            if script.string and "titleshot" in script.string:
                target_script = script.string
                break

        posters = {}
        seen_urls = set()
        if target_script:
            pattern = r'"(?P<type>\w+shot)":\s*"(?P<url>https://m\.media-amazon\.com/images/[^"]+)"'
            matches = re.findall(pattern, target_script)
            for category, img_url in matches:
                if img_url not in seen_urls:
                    posters[category] = img_url
                    seen_urls.add(img_url)

        # 🖨 Output
        reply_text = f"<b>🎬 Title:</b> <code>{clean_title}</code>\n"
        if release_year:
            reply_text += f"<b>📅 Year:</b> <code>{release_year}</code>\n"
        if season:
            reply_text += f"<b>📀 Season:</b> <code>{season}</code>\n"
        
        if posters:
            reply_text += "\n<b>🖼 Posters:</b>\n"
            for category, img in posters.items():
                reply_text += f"• <b>{category.capitalize()}</b>: <a href=\"{img}\">Link</a>\n"
        else:
            reply_text += "\n❌ No poster found."

        await message.reply(reply_text, disable_web_page_preview=False)

    except Exception as e:
        await message.reply(f"❌ Failed to fetch data.\n<b>Error:</b> <code>{str(e)}</code>")