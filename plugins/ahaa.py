import re
from pyrogram import Client, filters
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlencode, urlunparse

async def fetch_html(url):
    """Fetch page HTML using Playwright"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, timeout=30000)
        html = await page.content()
        await browser.close()
    return html

async def scrape_movie(soup):
    # Title
    title_tag = soup.select_one("meta[property='og:title']")
    raw_title = title_tag["content"] if title_tag else "Unknown"

    # Extract year from page meta description if available
    desc_tag = soup.select_one("meta[property='og:description']")
    year_match = None
    if desc_tag:
        year_match = re.search(r"\b(\d{4})\b", desc_tag['content'])
    if not year_match:
        year_match = re.search(r"\b(\d{4})\b", raw_title)
    year = year_match.group(1) if year_match else "Unknown"

    # Language
    language_match = re.search(r"\b(Tamil|Telugu|Hindi|English|Malayalam|Kannada)\b", raw_title, re.I)
    language = language_match.group(1).capitalize() if language_match else ""

    # Clean title
    clean_title = re.sub(rf"\b{year}\b", "", raw_title)
    if language:
        clean_title = re.sub(rf"\b{language}\b", "", clean_title, flags=re.I)
    clean_title = clean_title.replace("Movie", "").strip()

    # Poster
    poster_tag = soup.select_one("meta[property='og:image']")
    poster_url = poster_tag["content"] if poster_tag else None
    if poster_url:
        parsed = urlparse(poster_url)
        poster_url = urlunparse(parsed._replace(query=urlencode({"width": "4000"})))

    return poster_url, clean_title, year, language

async def scrape_series(soup):
    # Title
    title_tag = soup.select_one("div.details-header-content-title h1")
    title = title_tag.get_text(strip=True) if title_tag else "Unknown"

    # Info paragraph
    info_tag = soup.select_one("div.details-header-content-info p")
    year = "Unknown"
    season_text = ""
    if info_tag:
        info_text = info_tag.get_text(strip=True)
        year_match = re.search(r"\b(\d{4})\b", info_text)
        if year_match:
            year = year_match.group(1)
        season_match = re.search(r"(\d+ Season[s]?)", info_text)
        if season_match:
            season_text = f"Season {season_match.group(1).split()[0]}"

    # Language detection (meta title)
    lang_tag = soup.select_one("meta[property='og:title']")
    language = ""
    if lang_tag:
        lang_match = re.search(r"(Tamil|Telugu|Hindi|English|Malayalam|Kannada)", lang_tag['content'], re.I)
        if lang_match:
            language = lang_match.group(1).capitalize()

    # Poster
    poster_tag = soup.select_one("meta[property='og:image']")
    poster_url = poster_tag["content"] if poster_tag else None
    if poster_url:
        parsed = urlparse(poster_url)
        poster_url = urlunparse(parsed._replace(query=urlencode({"width": "4000"})))

    season_info_text = f" - {season_text}" if season_text else ""
    return poster_url, f"{title}{season_info_text}", year, language

@Client.on_message(filters.command("ahaa"))
async def aha_handler(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: /aha <Aha Movie or Series URL>", quote=True)

    url = message.command[1].strip()
    try:
        html = await fetch_html(url)
    except Exception as e:
        return await message.reply(f"❌ Failed to load page: {e}", quote=True)

    soup = BeautifulSoup(html, "html.parser")

    if "/movie/" in url:
        poster_url, title, year, language = await scrape_movie(soup)
    elif "/webseries/" in url:
        poster_url, title, year, language = await scrape_series(soup)
    else:
        return await message.reply("❌ URL must contain /movie/ or /webseries/", quote=True)

    if poster_url:
        msg = f"{poster_url}\n{title} - ({year}) ({language})"
    else:
        msg = f"{title} - ({year}) ({language})\n❌ Poster not found"

    await message.reply_text(msg, quote=True)