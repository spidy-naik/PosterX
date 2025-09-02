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

    # 🔍 Extract JSON-LD script
    jsonld_match = re.search(
        r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>',
        html, re.DOTALL | re.IGNORECASE
    )

    if jsonld_match:
        try:
            data = json.loads(jsonld_match.group(1))
            full_name = data.get("name", "Unknown")

            # Clean the title
            title = re.sub(r'Watch\s+', '', full_name, flags=re.IGNORECASE)
            title = re.sub(r'\s*-\s*Sony LIV', '', title, flags=re.IGNORECASE)
            title = re.sub(r'\s*Online$', '', title, flags=re.IGNORECASE)
            title = title.strip()

            # Extract year from uploadDate
            upload_date = data.get("uploadDate", "")
            year = upload_date[:4] if upload_date else "Unknown"
        except Exception:
            title = "Unknown"
            year = "Unknown"
    else:
        title = "Unknown"
        year = "Unknown"

    # 🔍 Poster extraction
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

    # 🔹 Build reply in desired format
    result = []
    if landscape:
        result.append(f"{landscape}")  # Landscape first, no label
    if portrait:
        result.append(f"🖼️ Portrait: {portrait}")
    result.append(f"{title} ({year})")  # Title + year at the bottom

    await message.reply("\n".join(result), disable_web_page_preview=True, quote=True)
