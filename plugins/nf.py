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
    
    # Fetch data from your API
    api_url = f"https://netflix-en.gregory24thom-ps-on23-96.workers.dev/?movieid={movie_id}"
    try:
        resp = requests.get(api_url, timeout=10).json()
    except Exception as e:
        return await message.reply(f"❌ Failed to fetch data: {e}", quote=True)
    
    if resp.get("status") != "success":
        return await message.reply("❌ Movie not found!", quote=True)
    
    metadata = resp.get("metadata", {}).get("video", {})
    title = metadata.get("title", "N/A")
    synopsis = metadata.get("synopsis", "N/A")
    year = metadata.get("year", "N/A")
    rating = metadata.get("rating", "N/A")
    runtime_sec = metadata.get("runtime", 0)
    runtime_min = runtime_sec // 60
    poster_url = metadata.get("artwork", [{}])[0].get("url")
    
    # Prepare the caption
    caption = f"🎬 <b>{title}</b> ({year})\n\n"
    caption += f"⭐ Rating: {rating}/10\n"
    caption += f"⏱ Runtime: {runtime_min} min\n\n"
    caption += f"{synopsis}"
    
    # Send the poster with caption
    await message.reply_photo(photo=poster_url, caption=caption)