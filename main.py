import os
from UI.BotUI import BotUI
import asyncio
from dotenv import dotenv_values

if __name__ == "__main__":
    bot = BotUI()
    asyncio.run(bot.run())
