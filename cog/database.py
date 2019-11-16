import discord
from discord.ext import commands


class Database(commands.Cog):
    def __init__(self, bot):
        @bot.command()
        async def create(ctx, address, *, name):
            """
            Creates a server o call
            :param ctx:
            :param address:
            :param name:
            :return:
            """
            result = bot.db.servers.insert_one({'discord_server': ctx.guild.id, 'address': address, 'name': name})
            print(result)
            return await ctx.send(f'Added `{address}` as `{name}`')

        @bot.command()
        async def servers(ctx):
            """
            Returns a list of servers
            :param ctx:
            :return:
            """
            results = bot.db.servers.find({'discord_server': ctx.guild.id})
            if not results.count():
                return await ctx.send("No servers added! Add one with s!create")
            embed = discord.Embed(title="Server list",
                                  type='rich')
            for result in results:
                embed.add_field(name=result['name'], value=result['address'])
            return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Database(bot))
