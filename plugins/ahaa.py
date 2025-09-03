import re
from pyrogram import Client, filters
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlencode, urlunparse

@Client.on_message(filters.command("ahaa"))
async def aha_series_scraper(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: /ahaseries <Aha Series URL>", quote=True)

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
    title_tag = soup.select_one("div.details-header-content-title h1")
    raw_title = title_tag.get_text(strip=True) if title_tag else "Unknown"
    # Remove any prefix like 'Watch ' and suffix like ' Online only on Aha'
    title = re.sub(r"^Watch\s+", "", raw_title, flags=re.I)
    title = re.sub(r"\s+Online only on Aha$", "", title, flags=re.I)

    # Info paragraph for year and season
    info_tag = soup.select_one("div.details-header-content-info p")
    year = "Unknown"
    season_text = ""
    if info_tag:
        info_text = info_tag.get_text(strip=True)
        # Year
        year_match = re.search(r"\b(\d{4})\b", info_text)
        if year_match:
            year = year_match.group(1)
        # Season
        season_match = re.search(r"(\d+)\s*Season[s]?", info_text, re.I)
        if season_match:
            season_text = f"Season {season_match.group(1)}"

    # Language detection (from meta title)
    lang_tag = soup.select_one("meta[property='og:title']")
    language = ""
    if lang_tag:
        lang_match = re.search(r"(Tamil|Telugu|Hindi|English|Malayalam|Kannada)", lang_tag['content'], re.I)
        if lang_match:
            language = lang_match.group(1).capitalize()

    # Poster URL
    poster_tag = soup.select_one("meta[property='og:image']")
    poster_url = poster_tag["content"] if poster_tag else None
    poster_url_final = None
    if poster_url:
        parsed = urlparse(poster_url)
        poster_url_final = urlunparse(parsed._replace(query=urlencode({"width": "4000"})))

    # Build message
    season_info_text = f" - {season_text}" if season_text else ""
    msg = f"{poster_url_final}\n{title}{season_info_text} - ({year}) ({language})" if poster_url_final else f"{title}{season_info_text} - ({year}) ({language})\n❌ Poster not found"

    await message.reply_text(msg, quote=True)
