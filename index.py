from dotenv import load_dotenv
import os
import asyncio
from pymongo import MongoClient
from urllib.parse import quote_plus
from discord.ext import commands
load_dotenv()

bot = commands.Bot(command_prefix="s!", description="Thank you for using Steam Servers! Here are my commands:")
bot.loop = asyncio.get_event_loop()
bot.remove_command("help")
bot.db = MongoClient("mongodb://%s:%s@%s/%s" % (
    quote_plus(os.getenv('MONGO_USERNAME')),
    quote_plus(os.getenv('MONGO_PASSWORD')),
    os.getenv('MONGO_HOST'),
    os.getenv('MONGO_DATABASE')))[os.getenv('MONGO_DATABASE')]
cogs = ["cog.basic", 'cog.valve', 'cog.database', 'cog.error_handling', 'cog.top', 'cog.help', 'cog.automation']


@bot.event
async def on_ready():
    print(f'Logged in with '+str(len(bot.guilds))+" guilds")

if __name__ == "__main__":
    for extension in cogs:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))
    try:
        bot.loop.run_until_complete(bot.start(os.getenv("TOKEN")))
    except KeyboardInterrupt:
        bot.loop.run_until_complete(bot.logout())
    finally:
        bot.loop.close()
