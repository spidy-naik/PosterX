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
            await page.wait_for_selector(".details-header")  # ensures page loaded
            html = await page.content()
            await browser.close()
    except Exception as e:
        return await message.reply(f"❌ Failed to load page: {e}", quote=True)

    soup = BeautifulSoup(html, "html.parser")

    # Poster: fetch from background-image style
    poster_url = None
    div_tag = soup.select_one(".details-header.hide-bg")
    if div_tag:
        style = div_tag.get("style", "")
        match = re.search(r'url\(&quot;(.*?)&quot;\)', style)
        if match:
            poster_url = match.group(1)
        else:
            # fallback: sometimes &quot; not used
            match = re.search(r'url\((.*?)\)', style)
            if match:
                poster_url = match.group(1)

    # Title
    title_tag = soup.select_one(".details-header-content-title h1")
    title = title_tag.get_text(strip=True) if title_tag else "Unknown"

    # Year: look for 4-digit number in content info
    year = "Unknown"
    info_tag = soup.select_one(".details-header-content-info p")
    if info_tag:
        match = re.search(r"\b(\d{4})\b", info_tag.get_text())
        if match:
            year = match.group(1)

    # Description
    desc_tag = soup.select_one("#description")
    description = desc_tag.get_text(strip=True) if desc_tag else "No description found"

    # Send message
    if poster_url:
        await message.reply_text(f"**{title} ({year})**\n\n{description}\n\n{poster_url}", quote=True)
    else:
        await message.reply_text(f"**{title} ({year})**\n\n{description}\n❌ Poster not found", quote=True)
