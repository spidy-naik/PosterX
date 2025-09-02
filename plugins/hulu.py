from pyrogram import Client, filters
import httpx
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

@Client.on_message(filters.command("hulu"))
async def hulu_poster(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: /hulu <Hulu URL>", quote=True)

    url = message.command[1].strip()

    try:
        async with httpx.AsyncClient(timeout=10) as client_http:
            resp = await client_http.get(url)
            resp.raise_for_status()
            html = resp.text
    except Exception as e:
        return await message.reply(f"❌ Failed to fetch URL: {e}", quote=True)

    soup = BeautifulSoup(html, "html.parser")

    # Extract JSON-LD script
    json_ld = soup.find("script", type="application/ld+json")
    if not json_ld:
        return await message.reply("❌ Hulu metadata not found!", quote=True)

    try:
        data = json.loads(json_ld.string)
        title = data.get("name", "Hulu Content")
        year = None
        if "releasedEvent" in data and data["releasedEvent"].get("startDate"):
            year = data["releasedEvent"]["startDate"].split("-")[0]

        poster = data.get("image", "")
        if poster:
            # Parse the URL and query
            parsed_url = urlparse(poster)
            query = parse_qs(parsed_url.query)

            # Keep only the essential keys
            query = {
                k: v[0] for k, v in query.items() 
                if k in ["base_image_bucket_name", "base_image"]
            }

            # Add high-res parameters
            query.update({"format": "jpeg", "size": "3840x2160"})

            # Rebuild URL
            poster = urlunparse(
                (parsed_url.scheme, parsed_url.netloc, parsed_url.path, "", urlencode(query), "")
            )

    except Exception as e:
        return await message.reply(f"❌ Failed to parse Hulu metadata: {e}", quote=True)

    # Final output
    msg = f"{poster}\n\n{title} -"
    if year:
        msg += f" ({year})"

    await message.reply_text(msg, quote=True)
