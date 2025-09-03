import json
from pyrogram import Client, filters
from playwright.async_api import async_playwright

@Client.on_message(filters.command("tarang"))
async def tarangplus_scraper(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: /tarang <TarangPlus URL>", quote=True)
    
    url = message.command[1].strip()

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=30000)
            content = await page.content()
            await browser.close()
    except Exception as e:
        return await message.reply(f"❌ Failed to load page: {e}", quote=True)

    # Extract JSON-LD
    import re
    json_ld_match = re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', content, re.DOTALL)
    if not json_ld_match:
        return await message.reply("❌ Failed to find video metadata", quote=True)

    try:
        data = json.loads(json_ld_match.group(1))
    except Exception as e:
        return await message.reply(f"❌ Failed to parse metadata: {e}", quote=True)

    # Extract fields
    title = data.get("name", "Unknown")
    description = data.get("description", "")
    poster_url = ""
    thumbnail_list = data.get("thumbnailUrl", [])
    if isinstance(thumbnail_list, list) and len(thumbnail_list) > 0:
        poster_url = thumbnail_list[0]

    upload_date = data.get("uploadDate", "Unknown")
    duration = data.get("duration", "Unknown")  # ISO 8601 duration
    content_url = data.get("contentUrl", url)

    # Build message
    msg = f"**{title}**\n\n"
    msg += f"📅 Release Date: {upload_date}\n"
    msg += f"⏱ Duration: {duration}\n"
    msg += f"🔗 Watch: {content_url}\n\n"
    msg += f"{description}\n\n"
    if poster_url:
        msg = f"{poster_url}\n\n" + msg

    await message.reply_text(msg, quote=True)