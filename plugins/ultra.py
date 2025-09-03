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

    try:
        # ✅ Title
        title = soup.select_one("h1.content-title")
        title = title.get_text(strip=True) if title else "Unknown Title"

        # ✅ Year (numeric <p>)
        year = "Unknown"
        for p in soup.select(".content-sub-detail p"):
            text = p.get_text(strip=True)
            if text.isdigit():
                year = text
                break

        # ✅ Description
        desc_tag = soup.select_one(".content-description p")
        description = desc_tag.get_text(strip=True) if desc_tag else "No description"

        # ✅ Cast & Crew
        cast_tags = soup.select(".cast-an-crew-value")
        cast = cast_tags[0].get_text(strip=True) if len(cast_tags) > 0 else "N/A"
        crew = cast_tags[1].get_text(strip=True) if len(cast_tags) > 1 else "N/A"

        # ✅ Poster
        poster = soup.select_one(".content-image img")
        poster_url = poster["src"] if poster else ""

    except Exception as e:
        return await message.reply(f"❌ Failed to parse Ultraplay metadata: {e}", quote=True)

    # Final output message
    msg = f"🎬 **{title} ({year})**\n\n"
    msg += f"📝 {description}\n\n"
    msg += f"👥 **Cast:** {cast}\n"
    msg += f"🎥 **Crew:** {crew}\n\n"
    if poster_url:
        msg = f"{poster_url}\n\n" + msg
    else:
        msg += "❌ Poster not found"

    await message.reply_text(msg, quote=True)