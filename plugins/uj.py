from pyrogram import Client, filters
import httpx
from bs4 import BeautifulSoup

@Client.on_message(filters.command("ultrajhakaas"))
async def ultrajhakaas_poster(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: /ultrajhakaas <Ultra Jhakaas URL>", quote=True)

    url = message.command[1].strip()

    try:
        async with httpx.AsyncClient(timeout=10) as http_client:
            resp = await http_client.get(url)
            resp.raise_for_status()
            html = resp.text
    except Exception as e:
        return await message.reply(f"❌ Failed to fetch URL: {e}", quote=True)

    soup = BeautifulSoup(html, "html.parser")

    try:
        # Title
        title = soup.select_one("h1.content-title")
        title = title.get_text(strip=True) if title else "Unknown"

        # Year
        year = "Unknown"
        sub_detail = soup.select_one(".content-sub-detail")
        if sub_detail:
            parts = [p.get_text(strip=True) for p in sub_detail.find_all("p")]
            for part in parts:
                if part.isdigit() and len(part) == 4:  # Likely a year
                    year = part
                    break

        # Poster (from video tag poster attribute)
        poster = None
        video = soup.select_one("video#video")
        if video and video.has_attr("poster"):
            poster = video["poster"]

        if not poster:
            return await message.reply("❌ Poster not found!", quote=True)

    except Exception as e:
        return await message.reply(f"❌ Failed to parse Ultra Jhakaas page: {e}", quote=True)

    msg = f"{poster}\n\n{title} ({year})"
    await message.reply_text(msg, quote=True)