from pyrogram import Client, filters
from playwright.async_api import async_playwright

@Client.on_message(filters.command("ultra") & filters.private)
async def ultra_handler(client, message):
    if len(message.command) < 2:
        return await message.reply("❗ Usage:\n/ultra <UltraJhakaas URL>")

    url = message.command[1].strip()

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=30000)

            poster_url = None
            title_text = None

            # 1️⃣ Check for <img> format
            img_element = await page.query_selector(".content-image img.poster")
            if img_element:
                poster_url = await img_element.get_attribute("src")
                title_text = await img_element.get_attribute("alt") or await img_element.get_attribute("title")

            # 2️⃣ If not found, fallback to <video> poster
            if not poster_url:
                video_element = await page.query_selector("video[poster]")
                if video_element:
                    poster_url = await video_element.get_attribute("poster")
                    # try to extract title from h1.content-title
                    title_elem = await page.query_selector("h1.content-title")
                    if title_elem:
                        title_text = await title_elem.text_content()

            # 3️⃣ Try to find year from content-sub-detail
            year_text = None
            sub_detail = await page.query_selector_all(".content-sub-detail p")
            for p in sub_detail:
                text = await p.text_content()
                if text and text.strip().isdigit() and len(text.strip()) == 4:
                    year_text = text.strip()
                    break

            title_with_year = f"{title_text.strip()} ({year_text})" if title_text and year_text else title_text.strip() if title_text else "Unknown Title"

            await browser.close()

    except Exception as e:
        return await message.reply(f"❌ Failed to fetch: {e}")

    if not poster_url:
        return await message.reply("❌ Poster not found!")

    await message.reply(f"{poster_url}\n{title_with_year}")
