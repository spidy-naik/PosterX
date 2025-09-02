from pyrogram import Client, filters
import re
import httpx

@Client.on_message(filters.command("nf"))
async def netflix_handler(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: /nf <Netflix URL>", quote=True)

    url = message.command[1].strip()

    # Extract Netflix ID
    match = re.search(r'/title/(\d+)', url)
    if not match:
        return await message.reply("❌ Invalid Netflix URL!", quote=True)

    movie_id = match.group(1)

    api_url = f"https://netflix-en.gregory24thom-ps-on23-96.workers.dev/?movieid={movie_id}"
    
    try:
        async with httpx.AsyncClient(timeout=10) as client_http:
            resp = await client_http.get(api_url)
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        return await message.reply(f"❌ Failed to fetch data: {e}", quote=True)

    if data.get("status") != "success":
        return await message.reply("❌ Movie/Series not found!", quote=True)

    video = data.get("metadata", {}).get("video", {})
    title = video.get("title", "N/A")
    type_ = video.get("type", "movie")

    # Always take the first artwork from the main video
    poster_url = video.get("artwork", [{}])[0].get("url", "No poster found")

    if type_ == "show" and video.get("seasons"):
        # Only the first season
        first_season = video["seasons"][0]
        season_name = first_season.get("longName") or first_season.get("shortName") or f"Season {first_season.get('seq', 1)}"
        season_year = first_season.get("year") or ""
        await message.reply_text(f"{poster_url}\n\n{title} - {season_name} - ({season_year})", quote=True)
    else:
        year = video.get("year", "N/A")
        await message.reply_text(f"{poster_url}\n\n{title} - ({year})", quote=True)
