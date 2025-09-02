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
    def get_main_artwork():
        arts = video.get("artwork", [])
        return arts[0].get("url") if arts else "No poster found"

    poster_url = get_main_artwork()

    if type_ == "show" and video.get("seasons"):
        msg_list = []
        for season in video["seasons"]:
            season_name = season.get("longName") or season.get("shortName") or f"Season {season.get('seq', 1)}"
            season_year = season.get("year") or ""
            msg_list.append(f"{poster_url}\n{title} - {season_name} - ({season_year})")
        await message.reply_text("\n\n".join(msg_list), quote=True)
    else:
        year = video.get("year", "N/A")
        await message.reply_text(f"{poster_url}\n{title} - ({year})", quote=True)
