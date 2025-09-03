import re
pyrogram import Client, filters
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

@Client.on_message(filters.command("ultraplay"))
async def ultraplay_simple(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: /ultraplay <Ultraplay URL>", quote=True)

    url = message.command[1].strip()

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=30000)
            await page.wait_for_selector("h1.content-title")  # ensures JS-rendered title exists
            html = await page.content()
            await browser.close()
    except Exception as e:
        return await message.reply(f"❌ Failed to load page: {e}", quote=True)

    soup = BeautifulSoup(html, "html.parser")

    # Poster URL
    poster_tag = soup.select_one(".content-image img")
    poster_url = poster_tag["src"] if poster_tag else None

    # Title
    title_tag = soup.select_one("h1.content-title")
    title = title_tag.get_text(strip=True) if title_tag else "Unknown"

    # Year
    year = "Unknown"
    for p_tag in soup.select(".content-sub-detail p"):
        text = p_tag.get_text(strip=True)
        match = re.search(r"\b(\d{4})\b", text)
        if match:
            year = match.group(1)
            break

    # Build and send response
    if poster_url:
        await message.reply_text(f"**{poster_url}\n\n{title} ({year})**", quote=True)
    else:
        await message.reply_text(f"{title} ({year})\n❌ Poster not found", quote=True)
