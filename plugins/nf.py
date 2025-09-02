from pyrogram import Client, filters
import requests
import re

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
    
    # Fetch metadata from API
    api_url = f"https://netflix-en.gregory24thom-ps-on23-96.workers.dev/?movieid={movie_id}"
    try:
        resp = requests.get(api_url, timeout=10).json()
    except Exception as e:
        return await message.reply(f"❌ Failed to fetch data: {e}", quote=True)
    
    if resp.get("status") != "success":
        return await message.reply("❌ Movie/Series not found!", quote=True)
    
    video = resp.get("metadata", {}).get("video", {})
    title = video.get("title", "N/A")
    year = video.get("year", "N/A")
    type_ = video.get("type", "movie")
    
    # Helper to get poster URL (prefer 1280x720)
    def get_poster(artworks):
        if not artworks:
            return ""
        for art in artworks:
            if art.get("w") == 1280 and art.get("h") == 720:
                return art.get("url")
        return artworks[0].get("url", "")
    
    if type_ == "show" and video.get("seasons"):
        # Series case: return poster for each season only
        msg_list = []
        for season in video["seasons"]:
            season_name = season.get("longName") or season.get("shortName") or "Season"
            season_year = season.get("year") or ""
            poster_url = get_poster(season.get("artwork", []))
            
            msg_list.append(f"{poster_url}\n{title} - {season_name} - ({season_year})")
        
        await message.reply_text("\n\n".join(msg_list), quote=True)
    
    else:
        # Movie case
        poster_url = get_poster(video.get("artwork", []))
        await message.reply_text(f"{poster_url}\n{title} - ({year})", quote=True)
