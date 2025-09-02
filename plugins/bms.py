from pyrogram import Client, filters
from pyrogram.types import Message
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


async def fetch_posters(url: str):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                page = await browser.new_page()
                await page.goto(url, timeout=60000)
                content = await page.content()
            finally:
                await browser.close()

        soup = BeautifulSoup(content, "html.parser")
        posters = []

        # Extract og:image
        og_image = soup.find("meta", property="og:image")
        if og_image:
            posters.append(og_image.get("content"))

        # Extract images from assets
        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src")
            if src and "assets-in.bmscdn.com" in src:
                posters.append(src)

        posters = list(set(posters))  # remove duplicates

        if not posters:
            return None

        return posters

    except Exception as e:
        return f"❌ Error: {e}"


@Client.on_message(filters.command("bms") & filters.private)
async def poster_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Send URL like:\n`/bms bms_url`")

    url = message.command[1]
    waiting = await message.reply_text("🔍 Fetching...")

    result = await fetch_posters(url)

    await waiting.delete()

    if not result:
        return await message.reply_text("❌ No posters found.")
    if isinstance(result, str):  # error case
        return await message.reply_text(result)

    # Send posters one by one
    for poster in result:
        try:
            await message.reply_photo(poster)
        except Exception:
            await message.reply_text(poster)