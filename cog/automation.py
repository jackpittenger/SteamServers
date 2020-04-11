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
            s!status ToasterRP 1440
            """
            if minutes <= 0:
                return await ctx.send('Minutes should be greater than \'0\'!')
            
            await create_status_timer(bot, ctx, name, minutes)

async def create_status_timer(bot, ctx, name, minutes):
    server = await get_server(bot, ctx, name)
    if server:
        bot.db.servers.update_one(
            { 'discord_server': ctx.guild.id, 'name': name }, 
            { "$set": { 'timer': { 'channel': ctx.channel.id, 'interval': minutes } } }
        )
        _start_timer(bot, ctx.channel.id, server["address"], minutes)

def _initialize_timers(bot):
    results = bot.db.servers.find({ 'timer':  { '$exists': True } })
    for server in results:
        _start_timer(bot, server["timer"]["channel"], server["address"], server["timer"]["interval"])

def _start_timer(bot, channel_id, serverAddress, minutes):
    async def sender(*args, **kwargs):
        channel = bot.get_channel(channel_id)

        if channel:
            await channel.send(*args, **kwargs)

    def wrapper():
        try:
            asyncio.run(query_logic(None, serverAddress, sender))
        finally:
            _start_timer(bot, channel_id, serverAddress, minutes)
    
    # create a new timer
    timer = Timer(minutes, wrapper)
    
    # store the current timer
    timers[str(channel_id) + ":" + serverAddress] = timer
    
    # start timer thread
    timer.start()

def setup(bot):
    bot.add_cog(Automation(bot))
    _initialize_timers(bot)
