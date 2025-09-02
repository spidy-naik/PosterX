from pyrogram import Client, filters, __version__
from pyrogram.raw.all import layer
from info import API_ID, API_HASH, ADMINS, BOT_TOKEN, PORT
from aiohttp import web
from plugins.route import routes
import time

async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app

class Bot(Client):
    def __init__(self):
        super().__init__(
            name='poster_bot',
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins={"root": "plugins"}
        )

    async def start(self):
        start_time = time.time()
        await super().start()

        me = await self.get_me()
        print(f"{me.first_name} is started now ❤️")
        seconds = round(time.time() - start_time, 2)
        for admin in ADMINS:
            await self.send_message(
                chat_id=admin,
                text=f"<b>✅ ʙᴏᴛ ʀᴇsᴛᴀʀᴛᴇᴅ\n🕥 ᴛɪᴍᴇ ᴛᴀᴋᴇɴ - <code>{seconds} sᴇᴄᴏɴᴅs</code></b>"
            )

    async def stop(self, *args):
        await super().stop()
        print("Bot stopped.")


app = Bot()
app.run()