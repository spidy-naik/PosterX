from pyrogram import Client, filters
from pyrogram.types import Message
import requests
from bs4 import BeautifulSoup
import re
import json

@Client.on_message(filters.command("prime") & filters.private)
async def prime_poster_scraper(client, message: Message):
    if len(message.command) < 2:
        return await message.reply(
            "❌ Please provide a Prime Video link.\n\nExample:\n<code>/prime https://www.primevideo.com/detail/XYZ</code>"
        )

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

        # 🖼 Posters (improved: parse "images": {...})
        posters = {}
        seen_urls = set()

        for script in soup.find_all("script"):
            content = script.string or (script.contents[0] if script.contents else "")
            if not content:
                continue

            if '"images":' in content:
                match = re.search(r'"images"\s*:\s*({.*?})', content)
                if match:
                    try:
                        images_json = match.group(1)
                        images_json = re.sub(r',\s*}', '}', images_json)  # fix trailing commas
                        images = json.loads(images_json)

                        for key, img_url in images.items():
                            if img_url not in seen_urls:
                                posters[key.lower()] = img_url
                                seen_urls.add(img_url)
                    except Exception:
                        pass

        # fallback: old regex titleshot/covershot
        if not posters:
            for script in soup.find_all("script"):
                content = script.string or (script.contents[0] if script.contents else "")
                if content and "shot" in content:
                    pattern = r'"(?P<type>\w+shot)":\s*"(?P<url>https://m\.media-amazon\.com/images/[^"]+)"'
                    matches = re.findall(pattern, content)
                    for category, img_url in matches:
                        if img_url not in seen_urls:
                            posters[category.lower()] = img_url
                            seen_urls.add(img_url)

        # 🖨 Output (custom format)
        reply_text = ""

        # Main poster (covershot)
        if "covershot" in posters:
            reply_text += f"{posters['covershot']}\n\n"

        # Portrait (packshot)
        if "packshot" in posters:
            reply_text += f"Portrait: {posters['packshot']}\n\n"

        # Title + Season + Year
        reply_text += f"{clean_title}"
        if season:
            reply_text += f" - {season}"
        if release_year:
            reply_text += f" - ({release_year})"

        await message.reply(reply_text, disable_web_page_preview=False)

    except Exception as e:
        await message.reply(
            f"❌ Failed to fetch data.\n<b>Error:</b> <code>{str(e)}</code>"
        )
