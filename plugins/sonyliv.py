import json
import re
from pyrogram import Client, filters
import requests

@Client.on_message(filters.command("sonyliv"))
async def sonyliv_handler(client, message):
    if len(message.command) < 2:
        return await message.reply("❗ Usage:\n/sonyliv <SonyLIV Show URL>", quote=True)

    url = message.command[1].strip()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        html = response.text
    except Exception as e:
        return await message.reply(f"❌ Failed to fetch page:\n{e}", quote=True)

    # 🔍 Extract JSON-LD script for name and year
    jsonld_match = re.search(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
    if jsonld_match:
        try:
            data = json.loads(jsonld_match.group(1))
            full_name = data.get("name", "Unknown").strip()
            # Extract year from the name using regex (usually in format "Movie Name 2025")
            year_match = re.search(r'(\d{4})', full_name)
            year = year_match.group(1) if year_match else "Unknown"
            title = full_name.split("-")[0].strip()  # remove any suffix like "- Sony LIV"
        except Exception:
            title = "Unknown"
            year = "Unknown"
    else:
        title = "Unknown"
        year = "Unknown"

    # 🔍 Poster extraction (your existing code)
    all_images = re.findall(
        r'https?://[^\s"\']+videoasset_images/[^\s"\']+\.(?:jpg|jpeg|png|webp)',
        html, re.IGNORECASE
    )

    portrait = None
    landscape = None
    for img in all_images:
        lower = img.lower()
        if not portrait and "portrait" in lower:
            portrait = img
        elif not landscape and "landscape" in lower:
            if "images.slivcdn.com" in img:
                img = img.replace("images.slivcdn.com", "origin-staticv2.sonyliv.com")
            landscape = img
        if portrait and landscape:
            break

    # 🔹 Build reply
    result = [f"🎬 Title: {title}", f"📅 Year: {year}"]
    if portrait:
        result.append(f"🖼️ Portrait: {portrait}")
    if landscape:
        result.append(f"🖼️ Landscape: {landscape}")
    if not portrait and not landscape:
        result.append("❌ No poster found.")

    await message.reply("\n".join(result), disable_web_page_preview=True, quote=True)