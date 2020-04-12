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
            Queries a saved server automatically in determined interval
            s!autostatus name minutes
            s!autostatus myServer 45
            """
            if 1440 < minutes < 30:
                return await ctx.send('Minutes should be greater than 30 and less than 1440 minutes!')

            await create_status_timer(bot, ctx, name, minutes * 60)


async def create_status_timer(bot, ctx, name, seconds):
    server = await get_server(bot, ctx, name)
    if server:
        bot.db.servers.update_one(
            {'discord_server': ctx.guild.id, 'name': name},
            {"$set": {'timer': {'channel': ctx.channel.id, 'interval': seconds}}}
        )
        _start_timer(bot, ctx.channel.id, server["address"], seconds)


def _initialize_timers(bot):
    results = bot.db.servers.find({'timer': {'$exists': True}})
    for server in results:
        print(server['timer']['channel'])
        _start_timer(bot, server["timer"]["channel"], server["address"], server["timer"]["interval"])


def _start_timer(bot, channel_id, server_address, seconds):
    async def sender(*args, **kwargs):
        channel = bot.get_channel(channel_id)

        if channel:
            await channel.send(*args, **kwargs)

    def wrapper():
        try:
            asyncio.run_coroutine_threadsafe(query_logic(None, server_address, sender), bot.loop)
        finally:
            _start_timer(bot, channel_id, server_address, seconds)

    timer = Timer(seconds, wrapper)
    timers[str(channel_id) + ":" + server_address] = timer
    timer.start()


def setup(bot):
    bot.add_cog(Automation(bot))
    _initialize_timers(bot)
