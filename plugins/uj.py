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

            # Wait for the <video> poster
            await page.wait_for_selector("video#video")
            poster_url = await page.get_attribute("video#video", "poster")

            # Extract title
            title_text = await page.text_content("h1.content-title")
            
            # Extract all <p> inside .content-sub-detail
            p_elements = await page.query_selector_all(".content-sub-detail p")
            year_text = None
            for p in p_elements:
                text = await p.text_content()
                if text and text.strip().isdigit() and len(text.strip()) == 4:
                    year_text = text.strip()
                    break

            title_with_year = f"{title_text.strip()} ({year_text})" if year_text else title_text.strip()

            await browser.close()

    except Exception as e:
        return await message.reply(f"❌ Failed to fetch: {e}")

    if not poster_url:
        return await message.reply("❌ Poster not found!")

    await message.reply(f"{poster_url}\n{title_with_year}")
