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

    # Get largest poster from a list
    def get_largest_artwork(arts):
        if not arts:
            return None
        arts_sorted = sorted(arts, key=lambda x: x.get("w", 0), reverse=True)
        return arts_sorted[0].get("url")

    # Combine all possible artworks for fallback
    main_artworks = video.get("artwork", []) + video.get("boxart", []) + video.get("storyart", [])

    if type_ == "show" and video.get("seasons"):
        msg_list = []
        for season in video["seasons"]:
            season_name = season.get("longName") or season.get("shortName") or f"Season {season.get('seq', 1)}"
            season_year = season.get("year") or ""
            # Try season artwork first, else fallback to main show artwork
            season_artworks = season.get("artwork", [])
            poster_url = get_largest_artwork(season_artworks) or get_largest_artwork(main_artworks) or "No poster found"
            msg_list.append(f"{poster_url}\n{title} - {season_name} - ({season_year})")
        await message.reply_text("\n\n".join(msg_list), quote=True)
    else:
        year = video.get("year", "N/A")
        poster_url = get_largest_artwork(main_artworks) or "No poster found"
        await message.reply_text(f"{poster_url}\n{title} - ({year})", quote=True)
