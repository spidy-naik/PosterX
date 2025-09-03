from pyrogram import Client, filters
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re

@Client.on_message(filters.command("aha") & filters.private)
async def aha_scraper(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: /aha <Aha URL>", quote=True)

    url = message.command[1].strip()

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=30000)
            await page.wait_for_selector(".details-header-content-title h1")
            html = await page.content()
            await browser.close()
    except Exception as e:
        return await message.reply(f"❌ Failed to load page: {e}", quote=True)

    soup = BeautifulSoup(html, "html.parser")

    # Title
    title_tag = soup.select_one(".details-header-content-title h1")
    title = title_tag.get_text(strip=True) if title_tag else "Unknown"

    # Year (first 4-digit number in .details-header-content-info p)
    year = "Unknown"
    info_p = soup.select_one(".details-header-content-info p")
    if info_p:
        match = re.search(r"\b(\d{4})\b", info_p.get_text())
        if match:
            year = match.group(1)

    # Description
    desc_tag = soup.select_one("#description")
    description = desc_tag.get_text(strip=True) if desc_tag else "No description found."

    # Poster (update this selector if needed)
    poster_tag = soup.select_one(".details-header-content .details-header-content-image")  # update selector
    poster_url = None
    if poster_tag:
        style = poster_tag.get("style", "")
        match = re.search(r'url\((.*?)\)', style)
        if match:
            poster_url = match.group(1)

    # fallback: check for any img in details-header-content
    if not poster_url:
        img_tag = soup.select_one(".details-header-content img")
        poster_url = img_tag["src"] if img_tag else None

    # Build and send response
    if poster_url:
        await message.reply_text(
            f"**{title} ({year})**\n\n{description}\n\nPoster: {poster_url}", 
            quote=True
        )
    else:
        await message.reply_text(
            f"**{title} ({year})**\n\n{description}\n❌ Poster not found", 
            quote=True
        )
