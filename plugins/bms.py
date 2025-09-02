import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import re

# --- Logger setup ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
file_handler = logging.FileHandler("bms_debug.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(console_handler)
logger.addHandler(file_handler)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("TgCrypto").setLevel(logging.WARNING)


async def fetch_movie_info(url: str):
    """Fetch title, year, and landscape poster from BookMyShow"""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            
            # Create context with user-agent (correct way)
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/139.0.0.0 Safari/537.36"
                )
            )

            page = await context.new_page()
            
            # Stealth: hide webdriver property
            await page.evaluate(
                "() => { Object.defineProperty(navigator, 'webdriver', {get: () => undefined}) }"
            )

            await page.goto(url, timeout=60000)
            content = await page.content()
            await browser.close()

        soup = BeautifulSoup(content, "html.parser")

        # Extract title
        og_title = soup.find("meta", property="og:title")
        title_text = og_title.get("content") if og_title else "Unknown Title"

        # Extract year from title
        year_match = re.search(r"\((\d{4})\)", title_text)
        year = year_match.group(1) if year_match else "Unknown Year"

        # Extract landscape poster
        og_image = soup.find("meta", property="og:image")
        poster_url = og_image.get("content") if og_image else None

        logger.debug(f"Title: {title_text}, Year: {year}, Poster: {poster_url}")
        return {"title": title_text, "year": year, "poster": poster_url}

    except Exception as e:
        logger.exception("Error in fetch_movie_info")
        return f"❌ Error: {e}"


@Client.on_message(filters.command("bms") & filters.private)
async def poster_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Send URL like:\n`/bms bms_url`")

    url = message.command[1]
    waiting = await message.reply_text("🔍 Fetching movie info...")

    result = await fetch_movie_info(url)
    await waiting.delete()

    if isinstance(result, str):
        return await message.reply_text(result)
    if not result["poster"]:
        return await message.reply_text(f"❌ No poster found for {result['title']}")

    # Send poster with caption
    caption = f"🎬 {result['title']} ({result['year']})"
    await message.reply_photo(result["poster"], caption=caption)
