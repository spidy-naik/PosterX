from pyrogram import Client, filters
import httpx
from bs4 import BeautifulSoup

@Client.on_message(filters.command("hulu"))
async def hulu_poster(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: /hulu <Hulu Series/Movie URL>", quote=True)

    url = message.command[1].strip()

    try:
        async with httpx.AsyncClient(timeout=10) as client_http:
            resp = await client_http.get(url)
            resp.raise_for_status()
            html = resp.text
    except Exception as e:
        return await message.reply(f"❌ Failed to fetch URL: {e}", quote=True)

    soup = BeautifulSoup(html, "html.parser")

    # Try to get poster from twitter:image or og:image
    poster_url = (
        soup.find("meta", property="twitter:image") or 
        soup.find("meta", property="og:image")
    )

    if poster_url and poster_url.get("content"):
        poster = poster_url["content"]
    else:
        return await message.reply("❌ Poster not found!", quote=True)

    # Get title
    title_meta = soup.find("meta", property="og:title") or soup.find("meta", attrs={"name":"title"})
    title = title_meta["content"] if title_meta and title_meta.get("content") else "Hulu Content"

    # Get description (optional)
    desc_meta = soup.find("meta", property="og:description") or soup.find("meta", attrs={"name":"description"})
    desc = desc_meta["content"] if desc_meta and desc_meta.get("content") else ""

    await message.reply_text(f"{poster}\n{title}\n{desc}", quote=True)
