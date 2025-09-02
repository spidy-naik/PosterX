import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# --- Setup logger ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Console handler (warnings/errors only)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
console_format = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
console_handler.setFormatter(console_format)

# File handler (full debug logs)
file_handler = logging.FileHandler("bms_debug.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_format = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
file_handler.setFormatter(file_format)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Silence Pyrogram/TgCrypto debug spam
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("TgCrypto").setLevel(logging.WARNING)


async def fetch_posters(url: str):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            # Create a context with user-agent
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/139.0.0.0 Safari/537.36"
                )
            )

            page = await context.new_page()

            # Hide webdriver property
            await page.evaluate(
                "() => { Object.defineProperty(navigator, 'webdriver', {get: () => undefined}) }"
            )

            await page.goto(url, timeout=60000)
            content = await page.content()
            await browser.close()

        # Parse HTML
        soup = BeautifulSoup(content, "html.parser")
        posters = []

        og_image = soup.find("meta", property="og:image")
        if og_image:
            posters.append(og_image.get("content"))

        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src")
            if src and "assets-in.bmscdn.com" in src:
                posters.append(src)

        posters = list(set([p for p in posters if p]))
        return posters if posters else None

    except Exception as e:
        logger.exception("Error in fetch_posters")
        return f"❌ Error: {e}"


@Client.on_message(filters.command("bms") & filters.private)
async def poster_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Send URL like:\n`/bms bms_url`")

    url = message.command[1]
    waiting = await message.reply_text("🔍 Fetching poster...")

    result = await fetch_posters(url)
    await waiting.delete()

    if not result:
        return await message.reply_text("❌ No poster found.")
    if isinstance(result, str):  # error message
        return await message.reply_text(result)

    # Send only the first (main) poster
    try:
        await message.reply_photo(result[0])
    except Exception as e:
        logger.warning(f"Failed to send photo: {result[0]} | Error: {e}")
        await message.reply_text(result[0])
