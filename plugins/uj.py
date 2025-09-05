from pyrogram import Client, filters
from playwright.async_api import async_playwright

@Client.on_message(filters.command("ultra") & filters.private)
async def ultra_handler(client, message):
    if len(message.command) < 2:
        return await message.reply("❗ Usage:\n/ultra <UltraJhakaas URL>")

    url = message.command[1].strip()
    poster_url = None
    title_text = None
    year_text = None

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=30000)

            # Wait for either video or image poster
            await page.wait_for_selector("video[poster], .content-image img.poster", timeout=10000)

            # Video poster first
            video_element = await page.query_selector("video[poster]")
            if video_element:
                poster_url = await video_element.get_attribute("poster")

            # Fallback to image poster
            if not poster_url:
                img_element = await page.query_selector(".content-image img.poster")
                if img_element:
                    poster_url = await img_element.get_attribute("src")
                    if not title_text:
                        title_text = await img_element.get_attribute("alt") or await img_element.get_attribute("title")

            # Extract title from h1 if not from image
            if not title_text:
                title_elem = await page.query_selector("h1.content-title")
                if title_elem:
                    title_text = (await title_elem.text_content()).strip()

            # Extract year
            if not year_text:
                sub_detail = await page.query_selector_all(".content-sub-detail p")
                for p in sub_detail:
                    text = await p.text_content()
                    if text and text.strip().isdigit() and len(text.strip()) == 4:
                        year_text = text.strip()
                        break

            await browser.close()

    except Exception as e:
        return await message.reply(f"❌ Failed to fetch: {e}")

    if not poster_url:
        return await message.reply("❌ Poster not found!")

    # Format title with year
    if title_text and year_text:
        title_with_year = f"{title_text} ({year_text})"
    elif title_text:
        title_with_year = title_text
    else:
        title_with_year = "Unknown Title"

    # Send poster URL + Title (Year)
    await message.reply(f"**{poster_url}\n\n{title_with_year}**")
