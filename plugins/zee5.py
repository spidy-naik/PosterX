from pyrogram import Client, filters
from pyrogram.types import Message
import re
import requests
from datetime import datetime

@Client.on_message(filters.command("zee5") & filters.private)
async def zee5_poster(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Please send a valid ZEE5 URL.\nExample:\n`/zee5 https://zee5.com/...`")

    url = message.command[1]

    # Extract content ID
    pattern = r'/([0-9a-zA-Z-]+)$'
    match = re.search(pattern, url)
    if not match:
        return await message.reply_text("❌ Invalid ZEE5 URL format.")
    
    content_id = match.group(1)

    # Define headers/data (dummy token here, replace if needed)
    params = {
        'content_id': content_id,
        'device_id': 'xxxxxxxxxxxxxxxxxxxxxxxxx',
        'platform_name': 'mobile_web',
        'translation': 'en',
        'user_language': 'hi',
        'country': 'IN',
        'check_parental_control': 'false',
    }

    json_data = {
        'x-access-token': "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwbGF0Zm9ybV9jb2RlIjoiYW5kcm9pZF90dkBhcHBsaWNhdGlvbiIsImlzc3VlZEF0IjoiMjAyMy0xMi0yOFQwNDo1ODozMS42ODZaIiwicHJvZHVjdF9jb2RlIjoiemVlNUA5NzUiLCJ0dGwiOjg2NDAwMDAwLCJpYXQiOjE3MDM3Mzk1MTF9.TlhuTDwPArVukNy-hzWA4uqS_CPIeiaTHC8TS8BLH_Q",
        'X-Z5-Guest-Token': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    }

    try:
        response = requests.post(
            'https://spapi.zee5.com/singlePlayback/getDetails/secure',
            params=params,
            json=json_data
        )
        data = response.json()

        asset = data.get('assetDetails', {})
        title = asset.get('title', 'Unknown Title')
        list_image = asset.get('list_image', '')
        cover_image = asset.get('cover_image', '')
        release_date = asset.get('release_date', '')

        if not (list_image and cover_image):
            return await message.reply_text("❌ Poster not found in the response.")

        # Construct image URLs
        landscape = f"https://akamaividz2.zee5.com/image/upload/resources/{content_id}/list/{list_image}"
        portrait = f"https://akamaividz2.zee5.com/image/upload/resources/{content_id}/portrait/{cover_image}"

        # Parse release year
        try:
            release_year = datetime.strptime(release_date, "%Y-%m-%dT%H:%M:%S").year
        except:
            release_year = "Unknown"

        caption = f"**{title}** ({release_year})\n\n**Zee5 Poster**:\n{landscape}\n\n**Portrait**:\n{portrait}\n\ncc: @PostersUniverse2"

        await message.reply_text(caption)

    except Exception as e:
        await message.reply_text(f"❌ Error occurred:\n`{str(e)}`")