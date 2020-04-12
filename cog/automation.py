import asyncio
from threading import Timer
from cog.database import get_server
from helpers import query_logic
from discord.ext import commands

timers = {}


class Automation(commands.Cog):
    def __init__(self, bot):
        @bot.command()
        @commands.has_permissions(manage_guild=True)
        async def autostatus(ctx, name, minutes: int):
            """
            Queries a saved server automatically in determined interval in the channel this command is called.
            Only displays if there is a change in player count.
            s!autostatus name minutes
            s!autostatus myServer 45
            """
            if minutes < 30 or minutes > 1440:
                return await ctx.send('Minutes should be greater than 30 and less than 1440!')
            await create_status_timer(bot, ctx, name, minutes * 60)
            await ctx.send('Auto status successfully added to server \'%s\'' % name)

        @bot.command()
        @commands.has_permissions(manage_guild=True)
        async def removeauto(ctx, name):
            """
            Removes an auto server
            s!removeauto name
            s!removeauto myServer
            """
            if str(ctx.guild.id)+name not in timers:
                return await ctx.send("That server is not currently setup!")
            bot.db.servers.update_one(
                {'discord_server': ctx.guild.id, 'name': name},
                {"$unset": {'timer': None}}
            )
            timers[str(ctx.guild.id) + name].cancel()
            timers[str(ctx.guild.id) + name] = None
            return await ctx.send("Server removed from autostatus!")


async def create_status_timer(bot, ctx, name, seconds):
    server = await get_server(bot, ctx, name)
    if server:
        bot.db.servers.update_one(
            {'discord_server': ctx.guild.id, 'name': name},
            {"$set": {'timer': {'channel': ctx.channel.id, 'interval': seconds}}}
        )
        _start_timer(bot, ctx.channel.id, server["address"], seconds, name, ctx.guild.id)


def _initialize_timers(bot):
    results = bot.db.servers.find({'timer': {'$exists': True}})
    for server in results:
        print(server)
        _start_timer(bot, server["timer"]["channel"], server["address"], server["timer"]["interval"], server['name'],
                     server["discord_server"])


def _start_timer(bot, channel_id, server_address, seconds, name, d_id):
    async def sender(*args, **kwargs):
        channel = bot.get_channel(channel_id)

        if channel:
            await channel.send(*args, **kwargs)

    def wrapper():
        try:
            asyncio.run_coroutine_threadsafe(query_logic(None, server_address, sender, name, bot, d_id), bot.loop)
        finally:
            _start_timer(bot, channel_id, server_address, seconds, name, d_id)

    timer = Timer(seconds, wrapper)
    timers[str(d_id)+name] = timer
    timer.start()


def setup(bot):
    bot.add_cog(Automation(bot))
    _initialize_timers(bot)
