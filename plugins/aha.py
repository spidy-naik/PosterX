import re
from pyrogram import Client, filters
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

@Client.on_message(filters.command("aha"))
async def aha_scraper(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: /aha <Aha URL>", quote=True)

    url = message.command[1].strip()

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=30000)
            html = await page.content()
            await browser.close()
    except Exception as e:
        return await message.reply(f"❌ Failed to load page: {e}", quote=True)

    soup = BeautifulSoup(html, "html.parser")

    # Title
    title_tag = soup.select_one("meta[property='og:title']")
    raw_title = title_tag["content"] if title_tag else "Unknown"

    # Extract year (4 digits)
    year_match = re.search(r"\b(\d{4})\b", raw_title)
    year = year_match.group(1) if year_match else "Unknown"

    # Extract language (if present)
    language_match = re.search(r"\b(Tamil|Telugu|Hindi|English|Malayalam|Kannada)\b", raw_title, re.I)
    language = language_match.group(1).capitalize() if language_match else ""

    # Clean title by removing year and language words
    clean_title = re.sub(rf"\b{year}\b", "", raw_title)
    if language:
        clean_title = re.sub(rf"\b{language}\b", "", clean_title, flags=re.I)
    clean_title = clean_title.replace("Movie", "").strip()

    # Poster URL
    poster_tag = soup.select_one("meta[property='og:image']")
    poster_url = poster_tag["content"] if poster_tag else None

    # Modify width to 4000
    poster_url_final = None
    if poster_url:
        parsed = urlparse(poster_url)
        qs_clean = {"width": "4000"}
        poster_url_final = urlunparse(parsed._replace(query=urlencode(qs_clean)))

    # Build message
    if poster_url_final:
        msg = f"{poster_url_final}\n{clean_title} - ({year}) ({language})"
    else:
        msg = f"{clean_title} - ({year}) ({language})\n❌ Poster not found"

    await message.reply_text(msg, quote=True)