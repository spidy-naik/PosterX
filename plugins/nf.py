from pyrogram import Client, filters
import requests
import re

@Client.on_message(filters.command("nf"))
async def netflix_handler(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: /nf <Netflix URL>", quote=True)
    
    url = message.command[1].strip()
    
    # Extract movieid from Netflix URL
    match = re.search(r'/title/(\d+)', url)
    if not match:
        return await message.reply("❌ Invalid Netflix URL!", quote=True)
    
    movie_id = match.group(1)
    
    # Fetch data from API
    api_url = f"https://netflix-en.gregory24thom-ps-on23-96.workers.dev/?movieid={movie_id}"
    try:
        resp = requests.get(api_url, timeout=10).json()
    except Exception as e:
        return await message.reply(f"❌ Failed to fetch data: {e}", quote=True)
    
    if resp.get("status") != "success":
        return await message.reply("❌ Movie not found!", quote=True)
    
    video = resp.get("metadata", {}).get("video", {})
    title = video.get("title", "N/A")
    year = video.get("year", "N/A")
    
    # Get 1280x720 poster
    poster_url = None
    for art in video.get("artwork", []):
        if art.get("w") == 1280 and art.get("h") == 720:
            poster_url = art.get("url")
            break
    
    if not poster_url:
        poster_url = video.get("artwork", [{}])[0].get("url", "")
    
    # Prepare message
    msg = f"{poster_url}\n\n{title} - ({year})"
    await message.reply_text(msg)