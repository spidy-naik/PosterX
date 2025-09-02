from pyrogram import Client, filters
import httpx
import json
from bs4 import BeautifulSoup

@Client.on_message(filters.command("aaonxt"))
async def aaonxt_poster(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: /aaonxt <AAONXT URL>", quote=True)

    url = message.command[1].strip()

    try:
        async with httpx.AsyncClient(timeout=10) as client_http:
            resp = await client_http.get(url)
            resp.raise_for_status()
            html = resp.text
    except Exception as e:
        return await message.reply(f"❌ Failed to fetch URL: {e}", quote=True)

    soup = BeautifulSoup(html, "html.parser")

    # Extract the __NEXT_DATA__ JSON
    script_tag = soup.find("script", id="__NEXT_DATA__", type="application/json")
    if not script_tag:
        return await message.reply("❌ AAONXT metadata not found!", quote=True)

    try:
        data = json.loads(script_tag.string)
        movie_data = data["props"]["pageProps"]["MovieData"]

        title = movie_data.get("title", "AAONXT Content")
        year = movie_data.get("year", "Unknown")
        poster = movie_data.get("cardImage", "")

    except Exception as e:
        return await message.reply(f"❌ Failed to parse AAONXT metadata: {e}", quote=True)

    # Final output
    msg = f"{poster}\n\n{title} ({year})"
    await message.reply_text(msg, quote=True)
