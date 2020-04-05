from discord.ext import commands
from helpers import query_logic


class Valve(commands.Cog):
    def __init__(self, bot):
        @bot.command()
        async def query(ctx, address):
            """
            Queries the server
            :param ctx:
            :param address:
            :return:
            """
            return await query_logic(ctx, address)


def setup(bot):
    bot.add_cog(Valve(bot))
