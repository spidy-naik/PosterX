from pyrogram import Client, filters
import httpx
from bs4 import BeautifulSoup

@Client.on_message(filters.command("ultraplay"))
async def ultraplay_poster(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: /ultraplay <Ultraplay URL>", quote=True)

    url = message.command[1].strip()

    try:
        async with httpx.AsyncClient(timeout=10) as client_http:
            resp = await client_http.get(url, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            html = resp.text
    except Exception as e:
        return await message.reply(f"❌ Failed to fetch URL: {e}", quote=True)

    soup = BeautifulSoup(html, "html.parser")

    # ✅ Fallback to OpenGraph meta tags
    title = soup.find("meta", property="og:title")
    title = title["content"].strip() if title else "Unknown Title"

    description = soup.find("meta", property="og:description")
    description = description["content"].strip() if description else "No description"

    poster = soup.find("meta", property="og:image")
    poster_url = poster["content"].strip() if poster else None

    # No reliable year / cast / crew in static HTML
    year = "Unknown"

    # Build message
    msg = f"🎬 {title} ({year})\n\n"
    msg += f"📝 {description}\n\n"

    if poster_url:
        msg = f"{poster_url}\n\n" + msg
    else:
        msg += "❌ Poster not found"

    await message.reply_text(msg, quote=True)
