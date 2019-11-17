import discord
from discord.ext import commands


class Database(commands.Cog):
    def __init__(self, bot):
        @bot.command()
        @commands.has_permissions(manage_guild=True)
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

        @bot.command()
        @commands.has_permissions(manage_guild=True)
        async def delete(ctx, name):
            """
            Deletes a server
            :param ctx:
            :param name:
            :return:
            """
            result = bot.db.servers.delete_one({'discord_server': ctx.guild.id, 'name': name})
            if not result.deleted_count:
                return await ctx.send("The server was not found, and therefore not deleted!")
            return await ctx.send(f'Server `{name}` was removed!')


def setup(bot):
    bot.add_cog(Database(bot))
