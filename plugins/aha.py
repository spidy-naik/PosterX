import re
from pyrogram import Client, filters
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

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
            html = await page.content()  # just get the content; no need to wait for meta
            await browser.close()
    except Exception as e:
        return await message.reply(f"❌ Failed to load page: {e}", quote=True)

    soup = BeautifulSoup(html, "html.parser")

    # Title
    title_tag = soup.select_one("meta[property='og:title']")
    title = title_tag["content"] if title_tag else "Unknown"

    # Description
    desc_tag = soup.select_one("meta[property='og:description']")
    description = desc_tag["content"] if desc_tag else "No description found"

    # Poster
    poster_tag = soup.select_one("meta[property='og:image']")
    poster_url = poster_tag["content"] if poster_tag else None

    # Year: extract 4-digit year from title
    year_match = re.search(r"\b(\d{4})\b", title)
    year = year_match.group(1) if year_match else "Unknown"

    # Send message
    if poster_url:
        await message.reply_text(f"**{title} ({year})**\n\n{description}\n\n{poster_url}", quote=True)
    else:
        await message.reply_text(f"**{title} ({year})**\n\n{description}\n❌ Poster not found", quote=True)
