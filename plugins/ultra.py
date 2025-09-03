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
            resp = await client_http.get(url)
            resp.raise_for_status()
            html = resp.text
    except Exception as e:
        return await message.reply(f"❌ Failed to fetch URL: {e}", quote=True)

    soup = BeautifulSoup(html, "html.parser")

    # Extract data
    title = soup.find("h1", class_="content-title")
    title = title.text.strip() if title else "Unknown Title"

    # Year is usually inside <div class="content-sub-detail"><p>…</p>
    year = "Unknown"
    sub_detail = soup.find("div", class_="content-sub-detail")
    if sub_detail:
        for p in sub_detail.find_all("p"):
            if p.text.strip().isdigit() and len(p.text.strip()) == 4:  # numeric year
                year = p.text.strip()
                break

    description = soup.find("div", class_="content-description")
    description = description.text.strip() if description else "No description"

    cast = soup.find("div", class_="cast-an-crew-value")
    cast_text = cast.text.strip() if cast else "N/A"

    # For crew, it’s the *next* div with same class
    crew = None
    if cast:
        crew = cast.find_next("div", class_="cast-an-crew-value")
    crew_text = crew.text.strip() if crew else "N/A"

    poster = soup.find("div", class_="content-image")
    poster_url = poster.img["src"] if poster and poster.img else None

    # Format output
    msg = f"🎬 {title} ({year})\n\n"
    msg += f"📝 {description}\n\n"
    msg += f"👥 Cast: {cast_text}\n"
    msg += f"🎥 Crew: {crew_text}\n\n"

    if poster_url:
        msg += poster_url
    else:
        msg += "❌ Poster not found"

    await message.reply_text(msg, quote=True)
