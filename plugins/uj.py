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

            # Wait until the <video> element is loaded
            await page.wait_for_selector("video#video")

            # Extract poster URL
            poster_url = await page.get_attribute("video#video", "poster")

            # Extract page title from <h1 class="content-title">Urmi</h1>
            title_text = await page.text_content("h1.content-title")
            
            # Extract year from page sub-detail
            year_text = await page.text_content(".content-sub-detail p:last-child")  # usually last <p> has year

            title_with_year = f"{title_text.strip()} ({year_text.strip()})" if year_text else title_text.strip()

            await browser.close()

    except Exception as e:
        return await message.reply(f"❌ Failed to fetch: {e}")

    if not poster_url:
        return await message.reply("❌ Poster not found!")

    # Send plain text response
    await message.reply(f"{poster_url}\n{title_with_year}")
