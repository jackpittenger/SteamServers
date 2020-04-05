import discord
from discord.ext import commands
from helpers import query_logic


class Database(commands.Cog):
    def __init__(self, bot):
        @bot.command()
        @commands.has_permissions(manage_guild=True)
        async def create(ctx, address, *, name):
            """
            Creates a server to call
            :param ctx:
            :param address:
            :param name:
            :return:
            """

            # implement regex check
            if bot.db.servers.find({'discord_server': ctx.guild.id}).count() >= 5:
                return await ctx.send("Max servers reached! Please join the support server to request more servers")
            bot.db.servers.insert_one({'discord_server': ctx.guild.id, 'address': address, 'name': name})
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

        @bot.command()
        async def status(ctx, name=""):
            """
            Displays  a saved server
            :param ctx:
            :param name:
            :return:
            """
            results = bot.db.servers.find({'discord_server': ctx.guild.id})
            if not results.count():
                return await ctx.send("No servers added! Add one with s!create")
            if name == "" and results.count() == 1:
                server = results[0]
            else:
                result = bot.db.servers.find_one({'discord_server': ctx.guild.id, 'name':name})
                if result:
                    server = result
                else:
                    return await ctx.send("Invalid server! Please choose one from s!servers")
            return await query_logic(ctx, server["address"])


def setup(bot):
    bot.add_cog(Database(bot))
