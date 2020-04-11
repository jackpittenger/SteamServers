import discord
from discord.ext import commands
from helpers import query_logic, players_logic


class Database(commands.Cog):
    def __init__(self, bot):
        @bot.command()
        @commands.has_permissions(manage_guild=True)
        async def create(ctx, address, *, name):
            """
            Creates a saved server
            s!create x.x.x.x:27017 Name
            s!create 144.12.123.51:27017 ToasterRP
            """
            if bot.db.servers.find({'discord_server': ctx.guild.id}).count() >= 5 and\
                    ctx.guild.id != 353751307460542476:
                return await ctx.send("Max servers reached! Please join the support server to request more servers")
            bot.db.servers.insert_one({'discord_server': ctx.guild.id, 'address': address, 'name': name})
            return await ctx.send(f'Added `{address}` as `{name}`')

        @bot.command()
        async def servers(ctx):
            """
            Returns a list of saved servers
            s!servers
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
        async def delete(ctx, *, name):
            """
            Deletes a saved server
            s!delete name
            s!delete ToasterRP
            """
            result = bot.db.servers.delete_one({'discord_server': ctx.guild.id, 'name': name})
            if not result.deleted_count:
                return await ctx.send("The server was not found, and therefore not deleted!")
            return await ctx.send(f'Server `{name}` was removed!')

        @bot.command()
        async def status(ctx, *, name=""):
            """
            Queries a saved server. If you only have one server you don't need to specify a name.
            s!status
            s!status name
            s!status ToasterRP
            """
            return await _check_sever(bot, ctx, name, query_logic)

        @bot.command()
        async def players(ctx, *, name=""):
            """
            Shows the players on a saved server. If you only have one server you don't need to specify a name.
            s!players
            s!players name
            s!players ToasterRP
            """
            return await _check_sever(bot, ctx, name, players_logic)

async def get_server(bot, ctx, name):
    server = None
    results = bot.db.servers.find({'discord_server': ctx.guild.id})
    if not results.count():
        await ctx.send("No servers added! Add one with s!create")
    elif name == "" and results.count() == 1:
        server = results[0]
    else:
        result = bot.db.servers.find_one({'discord_server': ctx.guild.id, 'name': name})
        if result:
            server = result
        else:
            await ctx.send("Invalid server! Please choose one from s!servers")
    return server

async def _check_sever(bot, ctx, name, func):
    server = await get_server(bot, ctx, name)
    if server:
        return await func(ctx, server["address"])
    return None

def setup(bot):
    bot.add_cog(Database(bot))
