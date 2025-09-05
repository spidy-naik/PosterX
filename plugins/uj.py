from pyrogram import Client, filters
from pyrogram.types import Message
from playwright.async_api import async_playwright

@Client.on_message(filters.command("ultra") & filters.private)
async def ultra_handler(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❗ Usage:\n/ultra <UltraJhakaas URL>")

    url = message.command[1].strip()

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=30000)

            # ✅ Wait until <video id="video"> is available
            await page.wait_for_selector("video#video")

            # Extract poster attribute
            poster = await page.get_attribute("video#video", "poster")

            # Extract page title
            page_title = await page.title()
            title = page_title.split(" - ")[0].strip()
            year = ""
            if "(" in title and ")" in title:
                year = title.split("(")[-1].replace(")", "").strip()
                title = title.split("(")[0].strip()

            await browser.close()

    except Exception as e:
        return await message.reply(f"❌ Failed to fetch: {e}")

    if not poster:
        return await message.reply("❌ Poster not found!")

    caption = f"🎬 <b>{title}</b> {f'({year})' if year else ''}"
    await message.reply_photo(photo=poster, caption=caption)
