import httpx
import logging
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.types import Message

# --- Setup logger ---
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


async def fetch_poster(url: str):
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            r = await client.get(url)

        logger.debug(f"Fetched URL: {url} | Status: {r.status_code}")
        logger.debug(f"Response length: {len(r.text)} chars")

        soup = BeautifulSoup(r.text, "html.parser")

        posters = []

        # Look for meta og:image (property or name)
        og_property = soup.find_all("meta", attrs={"property": "og:image"})
        og_name = soup.find_all("meta", attrs={"name": "og:image"})

        logger.debug(f"Found og:image (property): {og_property}")
        logger.debug(f"Found og:image (name): {og_name}")

        for tag in og_property + og_name:
            posters.append(tag.get("content"))

        # Extra fallback: BookMyShow asset images
        imgs = soup.find_all("img")
        logger.debug(f"Found {len(imgs)} <img> tags")

        for img in imgs:
            src = img.get("src") or img.get("data-src")
            if src and "assets-in.bmscdn.com" in src:
                posters.append(src)

        posters = list(set([p for p in posters if p]))
        logger.debug(f"Collected posters: {posters}")

        return posters if posters else None

    except Exception as e:
        logger.exception("Error in fetch_poster")
        return f"❌ Error: {e}"


@Client.on_message(filters.command("bms") & filters.private)
async def poster_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Send URL like:\n`/bms bms_url`")

    url = message.command[1]
    waiting = await message.reply_text("🔍 Fetching poster...")

    result = await fetch_poster(url)
    await waiting.delete()

    if not result:
        return await message.reply_text("❌ No poster found.")
    if isinstance(result, str):  # error case
        return await message.reply_text(result)

    # Send all posters
    for poster in result:
        try:
            await message.reply_photo(poster)
        except Exception as e:
            logger.warning(f"Failed to send photo: {poster} | Error: {e}")
            await message.reply_text(poster)
