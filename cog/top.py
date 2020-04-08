import os
import dbl
import discord
from discord.ext import commands


class TopGG(commands.Cog):
    """Handles interactions with the top.gg API"""

    def __init__(self, bot):
        if os.getenv("DEBUG") == "true":
            print("Running in dev mode!")
        else:
            self.bot = bot
            self.token = os.getenv("DBL_TOKEN")
            self.dblpy = dbl.DBLClient(self.bot, self.token, autopost=True)


def setup(bot):
    bot.add_cog(TopGG(bot))
