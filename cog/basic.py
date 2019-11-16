from discord.ext import commands


class Basic(commands.Cog):
    def __init__(self, bot):
        @bot.command()
        async def ping(ctx):
            """
            Pings the bot
            :param ctx:
            :return:
            """
            return await ctx.send("Pong!")


def setup(bot):
    bot.add_cog(Basic(bot))
