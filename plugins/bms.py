from pyrogram import Client, filters
from pyrogram.types import Message
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


async def fetch_posters(url):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=60000)
            content = await page.content()
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

        if not posters:
            return "❌ No posters found."

        posters = list(set(posters))
        return "\n".join(posters)

    except Exception as e:
        return f"❌ Error: {e}"


@Client.on_message(filters.command("poster") & filters.private)
async def poster_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Send URL like:\n`/poster bms_url`")

    url = message.command[1]
    await message.reply_text("🔍 Fetching...")

    result = await fetch_posters(url)
    await message.reply_text(result)