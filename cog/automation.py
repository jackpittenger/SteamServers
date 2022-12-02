import asyncio
import time
import discord
from enum import Enum
from threading import Thread, Timer
from discord.ext import commands
from discord import app_commands
from helpers import query_server_for_summary, query_server_for_players  
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError

class AutomationType(Enum):
    summary = 0
    players = 1

class Automation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def server_name_autocomplete(self, interaction: discord.Interaction, current: str):
        servers = self.bot.db.servers.find({'discord_server': interaction.guild_id})
        result_dict = []
        for result in servers:
            result_dict.append(discord.app_commands.Choice(name=result['name'], value=result['name']))
        return result_dict

    async def auto_autocomplete(self, interaction: discord.Interaction, current: str):
        autos = self.bot.db.auto.find({'discord_server': interaction.guild_id})
        return [discord.app_commands.Choice(name=auto['name']+" | "+AutomationType(auto["auto_type"]).name.upper(), value=auto['name']+str(auto["auto_type"])) for auto in autos]

    @app_commands.command(name="create_auto")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.autocomplete(server_name=server_name_autocomplete)
    @app_commands.describe(
            server_name="The server name to query",
            minutes="The frequency of updates in minutes; [10-10080]",
            auto_type="Should this query for a summary (as in query) or players (as in query_players)",
            channel="What channel should updates be sent to?"
    )
    async def create_auto(self, interaction: discord.Interaction, server_name: str, minutes: app_commands.Range[int, 10, 10080], auto_type: AutomationType, channel : discord.TextChannel):
        """
        Queries a saved server automatically in a defined interval in a defined channel. Requires MANAGE_GUILD
        """
        if minutes < 10 or minutes > 10080:
            await interaction.response.send_message('Minutes should be greater than 10 and less than 10080!')
            return
        await interaction.response.defer()
        server = self.bot.db.servers.find_one({'discord_server': interaction.guild_id, 'name': server_name})
        if server is None:
            await interaction.followup.send(content="That server doesn't exist!")
        elif self.bot.db.auto.find_one({'discord_server': interaction.guild_id, 'name': server_name, 'auto_type': auto_type.value}) is not None:
            await interaction.followup.send(content="This server already has an auto of this type! To readd it, please delete it first")
        elif self.bot.db.exempt.count_documents({'server': interaction.guild_id}) == 0 and self.bot.db.auto.count_documents({'discord_server': interaction.guild_id}) >= 5:
            await interaction.followup.send(content="You already have the max amount of autos added! To get more, please message on the support Discord (https://discord.gg/EKVQPxF).")
        else:
            self.bot.db.auto.insert_one({'discord_server': interaction.guild_id, 'name': server_name, 'address': server['address'], 'auto_type': auto_type.value, 'frequency': minutes*60, 'last_update': 0, 'channel': channel.id})
            await interaction.followup.send(content="Auto %s successfully added to server `%s`" % (auto_type.name, server_name))

    @app_commands.command(name="list_autos")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def list_autos(self, interaction: discord.Interaction):
        """
        List the currently setup autos. Requires MANAGE_GUILD
        """
        await interaction.response.defer()
        autos = self.bot.db.auto.find({'discord_server': interaction.guild_id}, limit=5)
        embed = discord.Embed(title="Autos list", type="rich")
        for auto in autos:
            embed.add_field(name=auto['name']+" | "+AutomationType(auto['auto_type']).name.upper(), value=str(auto['frequency']/60)+" minutes")
        if autos.retrieved == 0:
            await interaction.followup.send(content="You don't have any autos added! Create one with `/create_auto`")
            return
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="delete_auto")
    @app_commands.autocomplete(auto=auto_autocomplete)
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(
            auto="The auto to delete"
    )
    async def delete_auto(self, interaction: discord.Interaction, auto: str):
        """
        Deletes a saved auto. Requires MANAGE_GUILD 
        """
        await interaction.response.defer()
        result = self.bot.db.auto.delete_one({'discord_server':interaction.guild_id, 'name':auto[:-1], 'auto_type': int(auto[-1])})
        if not result.deleted_count:
            await interaction.followup.send(content="Auto not found!")
        else:
            await interaction.followup.send(content="Auto deleted!")

class Threaded(Thread):
    def __init__(self, bot):
        self.bot = bot
        Thread.__init__(self)
        self.daemon = True
        self.start()

    def run(self):
        print("Booting up automation thread")
        while True:
            time.sleep(60)
            asyncio.run_coroutine_threadsafe(self.process(self.bot), self.bot.loop)

    async def process(self, bot):
        currentTime = time.time()
        autos_needing_processing = bot.db.auto.find({"$expr": {"$lt": [{"$add": ["$frequency", "$last_update"]}, currentTime]}})
        mongoActions = [] 
        for auto in autos_needing_processing:
            try:
                mongoActions.append(UpdateOne({"_id": auto["_id"]}, {"$set": {"last_update": currentTime}})) 
                if auto['auto_type'] == 0:
                    #Querying for a summary
                    msg = await query_server_for_summary(auto["address"])
                else:
                    #Querying for players
                    msg = await query_server_for_players(auto["address"])
                # Get channel
                channel = bot.get_channel(auto["channel"])
                if channel is None or not isinstance(channel, discord.TextChannel):
                    print("Deleting failed auto due to improper channel")
                    bot.db.auto.delete_one({"_id": auto["_id"]})
                    raise Exception("Unable to access channel or channel is not a text channel")
                else:
                    if isinstance(msg, str):
                        await channel.send(msg)
                    else:
                        await channel.send(embed=msg)
            except Exception as e:
                print(f"Exception running auto {auto['name']} {auto['auto_type']} of server {auto['discord_server']}") 
                print(e)
        if len(mongoActions) != 0:
            try:
                bot.db.auto.bulk_write(mongoActions, ordered=False)
            except BulkWriteError as bwe:
                print("Error in bulk write of auto")
                print(bwe)


async def setup(bot):
    await bot.add_cog(Automation(bot))
    Threaded(bot)
