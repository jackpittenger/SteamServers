from dotenv import load_dotenv
import os
from pymongo import MongoClient
from urllib.parse import quote_plus
from discord.ext import commands
load_dotenv()


bot = commands.Bot(command_prefix="s!", description="Testing")
bot.db = MongoClient("mongodb://%s:%s@%s/%s" % (
    quote_plus(os.getenv('MONGO_USERNAME')),
    quote_plus(os.getenv('MONGO_PASSWORD')),
    os.getenv('MONGO_HOST'),
    os.getenv('MONGO_DATABASE')))[os.getenv('MONGO_DATABASE')]
cogs = ["cog.basic", 'cog.valve', 'cog.database']


@bot.event
async def on_ready():
    print(f'Logged in')


@bot.command()
async def load(extension_name : str):
    """Loads an extension."""
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        print(e)
        return


@bot.command()
async def unload(extension_name : str):
    """Unloads an extension."""
    bot.unload_extension(extension_name)


if __name__ == "__main__":
    for extension in cogs:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))
    bot.run(os.getenv("TOKEN"))
