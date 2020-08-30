from discord.ext import commands
from helpers import query_logic, players_logic, get_prefix


class Valve(commands.Cog):
    def __init__(self, bot):
        @bot.command()
        async def query(ctx, address):
            """
            Queries a server
            s!query x.x.x.x:PORT
            s!query 144.12.123.51:27017
            """
            return await query_logic(ctx, address, bot)

        @bot.command()
        async def pquery(ctx, address):
            """
            Lists players on a server
            s!pquery x.x.x.x:PORT
            s!pquery 144.12.123.51:27017
            """
            return await players_logic(ctx, address, bot)

        @query.error
        @pquery.error
        async def do_repeat_handler(ctx, error):
            if isinstance(error, commands.MissingRequiredArgument):
                if error.param.name == 'address':
                    print(ctx)
                    await ctx.send("Please format your command like: `"+get_prefix(bot, ctx.guild.id)+"command 144.12.123.51:27017`")


def setup(bot):
    bot.add_cog(Valve(bot))
