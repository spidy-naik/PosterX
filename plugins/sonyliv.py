from pyrogram import Client, filters
import requests
import re

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
        html = response.text
    except Exception as e:
        return await message.reply(f"❌ Failed to fetch page:\n{e}", quote=True)

    # 🔍 Title from <title> tag using regex
    title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    full_title = title_match.group(1).strip() if title_match else "Unknown"
    title = full_title.split(" - ")[0].strip()

    # 🔍 All image URLs containing "videoasset_images"
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

    result = [f"🎬 Title: {title}"]
    if portrait:
        result.append(f"🖼️ Portrait: {portrait}")
    if landscape:
        result.append(f"🖼️ Landscape: {landscape}")
    if not portrait and not landscape:
        result.append("❌ No poster found.")

    await message.reply("\n".join(result), disable_web_page_preview=True, quote=True)