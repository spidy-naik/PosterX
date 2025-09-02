from pyrogram import Client, filters
from pyrogram.types import Message
import re
import requests
from datetime import datetime

@Client.on_message(filters.command("zee5") & filters.private)
async def zee5_poster(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "❌ Please send a valid ZEE5 URL.\nExample:\n`/zee5 https://zee5.com/...`"
        )

    url = message.command[1]

    # Extract content ID (last part of URL)
    match = re.search(r'/([0-9a-zA-Z-]+)$', url)
    if not match:
        return await message.reply_text("❌ Invalid ZEE5 URL format.")
    content_id = match.group(1)

    # Dummy headers/data for testing (replace with real tokens if needed)
    params = {
        'content_id': content_id,
        'device_id': 'dummy-device-id',
        'platform_name': 'mobile_web',
        'translation': 'en',
        'user_language': 'hi',
        'country': 'IN',
        'check_parental_control': 'false',
    }

    json_data = {
        'x-access-token': 'dummy-token',
        'X-Z5-Guest-Token': 'dummy-guest-token',
    }

    try:
        response = requests.post(
            'https://spapi.zee5.com/singlePlayback/getDetails/secure',
            params=params,
            json=json_data,
            timeout=20
        )
        data = response.json()

        asset = data.get('assetDetails', {})
        if not asset:
            return await message.reply_text("❌ No asset details found.")

        title = asset.get('title', 'Unknown Title')
        landscape = asset.get('list_image') or ''
        portrait = asset.get('cover_image') or ''
        release_date = asset.get('release_date', '')

        # Parse release year
        try:
            release_year = datetime.strptime(release_date, "%Y-%m-%dT%H:%M:%S").year
        except:
            release_year = "Unknown"

        if not (landscape or portrait):
            return await message.reply_text("❌ No poster images found.")

        caption = f"**{title}** ({release_year})\n\n"
        if landscape:
            caption += f"**Landscape Poster**:\n{landscape}\n\n"
        if portrait:
            caption += f"**Portrait Poster**:\n{portrait}\n\n"
        caption += "cc: @Mr_SPIDY"

        await message.reply_text(caption)

    except Exception as e:
        await message.reply_text(f"❌ Error occurred:\n`{str(e)}`")
