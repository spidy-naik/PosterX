from pyrogram import Client, filters
from pyrogram.types import Message
from playwright.async_api import async_playwright

async def fetch_ultra_poster(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, timeout=15000)

        # Title
        title = await page.locator("h1.content-title").inner_text()

        # Year
        year_text = await page.locator("div.content-sub-detail").inner_text()
        year = None
        for part in year_text.split("|"):
            part = part.strip()
            if part.isdigit() and len(part) == 4:
                year = part

        # Poster
        poster = await page.locator("video").get_attribute("poster")

        await browser.close()
        return {"title": title, "year": year, "poster": poster}

@Client.on_message(filters.command("ultra") & filters.private)
async def ultra_handler(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage:\n`/ultra <UltraJhakass URL>`", quote=True)

    url = message.command[1].strip()
    details = await fetch_ultra_poster(url)

    if not details or not details["poster"]:
        return await message.reply("❌ Poster not found!", quote=True)

    caption = f"🎬 **{details['title']}** ({details['year']})"
    await message.reply_photo(details["poster"], caption=caption)
