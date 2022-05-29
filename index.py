from dotenv import load_dotenv
import os
import asyncio
from pymongo import MongoClient
from urllib.parse import quote_plus
import discord
from discord.ext import commands
load_dotenv()

cogs = ["cog.basic", "cog.valve"]

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="s!", intents=discord.Intents.default())

    async def startup(self):
        await bot.wait_until_ready();
        await bot.tree.sync(guild=discord.Object(441425708896747532))
        print("Successfully synced commands")
        print(f"Connected as {bot.user}")

    async def setup_hook(self):
        
        for extension in cogs:
            try:
                await bot.load_extension(extension)
                print(f"Loaded {extension}")
            except Exception as e:
                print(f"Failed to load {extension}")
                print(f"[ERROR] {e}")

        self.loop.create_task(self.startup())

bot = Bot() 

bot.db = MongoClient("mongodb://%s:%s@%s/%s" % (
    quote_plus(os.getenv('MONGO_USERNAME')),
    quote_plus(os.getenv('MONGO_PASSWORD')),
    os.getenv('MONGO_HOST'),
    os.getenv('MONGO_DATABASE')))[os.getenv('MONGO_DATABASE')]


@bot.event
async def on_ready():
    print(f'Logged in with '+str(len(bot.guilds))+" guilds")


if __name__ == "__main__":
    try:
        bot.run(os.getenv("TOKEN"))
    except KeyboardInterrupt:
        bot.close()

