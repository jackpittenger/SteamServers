import asyncio
import time
import datetime
import math
from threading import Thread, Timer
from cog.database import get_server
from helpers import query_logic
from discord.ext import commands

timers = {}
start_minutes = math.floor((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds() / 60) 


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
            bot.db.servers.update_one(
                {'discord_server': ctx.guild.id, 'name': name},
                {"$set": {'timer': {'channel': ctx.channel.id, 'interval': minutes * 60}}}
            )
            await ctx.send('Auto status successfully added to server \'%s\'' % name)

        @bot.command()
        @commands.has_permissions(manage_guild=True)
        async def removeauto(ctx, name):
            """
            Removes an auto server
            s!removeauto name
            s!removeauto myServer
            """
            if bot.db.servers.find_one({'discord_server': ctx.guild.id, 'name': name, 'timer': {'$exists': True}}) is None:
                return await ctx.send("That server is not currently setup!")
            bot.db.servers.update_one(
                {'discord_server': ctx.guild.id, 'name': name},
                {"$unset": {'timer': None}}
            )
            return await ctx.send("Server removed from autostatus!")


class Threaded(Thread):
    def __init__(self, bot):
        self.bot = bot
        Thread.__init__(self)
        self.daemon = True
        self.start()
    
    def run(self):
        time.sleep(10) # Temporary way to let the bot boot up - should probably come up with a better way
        while True:
            asyncio.run_coroutine_threadsafe(self.server_fetch(self.bot), self.bot.loop)
            time.sleep(60)
 
    async def server_fetch(self, bot):
        results = bot.db.servers.find({'timer': {'$exists': True}})
        time_now = math.floor((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds() / 60)
        for server in results:
            if start_minutes-time_now != 0 and (time_now - start_minutes) % (server["timer"]["interval"] / 60) != 0:
                continue
            async def sender(*args, **kwargs):
                channel = self.bot.get_channel(server["timer"]["channel"])
                if channel:
                    await channel.send(*args, **kwargs)
        
            await query_logic(None, server["address"], sender, server["name"], bot, server["discord_server"]) 


def setup(bot):
    bot.add_cog(Automation(bot))
    Threaded(bot)
