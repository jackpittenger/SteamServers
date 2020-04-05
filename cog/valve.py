from discord.ext import commands
<<<<<<< HEAD
from helpers import query_logic
=======
import a2s
import socket
>>>>>>> bdfb0bb94bff2117a284f35994b4a00d29c6265c


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

        @query.error
        async def do_repeat_handler(ctx, error):
            print(error)
            if isinstance(error, commands.MissingRequiredArgument):
                if error.param.name == 'address':
                    await ctx.send("Please format your command like: `s!query 144.12.123.51:27017`")


def setup(bot):
    bot.add_cog(Valve(bot))
