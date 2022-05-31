import asyncio
import time
import datetime
import math
from enum import Enum
from threading import Thread, Timer
from discord.ext import commands
import discord
from discord import app_commands
from helpers import query_server_for_summary, query_server_for_players  

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

    @app_commands.command(name="create_auto")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.autocomplete(server_name=server_name_autocomplete)
    @app_commands.describe(
            server_name="The server name to query",
            minutes="The frequency of updates in minutes; [10-10080]",
            auto_type="Should this query for a summary (as in query) or players (as in query_players)",
            channel="What channel should updates be sent to?"
    )
    @app_commands.guilds(discord.Object(441425708896747532))
    async def create_auto(self, interaction: discord.Interaction, server_name: str, minutes: app_commands.Range[int, 10, 10080], auto_type: AutomationType, channel : discord.TextChannel):
        """
        Queries a saved server automatically in a defined interval in a defined channel.
        """
        if minutes < 10 or minutes > 10080:
            await interaction.response.send_message('Minutes should be greater than 10 and less than 10080!')
            return
        await interaction.response.defer()
        if self.bot.db.auto.find_one({'discord_server': interaction.guild_id, 'name': server_name, 'auto_type': auto_type.value}) is not None:
            await interaction.followup.send(content="This server already has an auto of this type! To readd it, please delete it first")
        else:
            self.bot.db.auto.insert_one({'discord_server': interaction.guild_id, 'name': server_name, 'auto_type': auto_type.value, 'frequency': minutes, 'channel': channel.id})
            await interaction.followup.send(content="Auto %s successfully added to server `%s`" % (auto_type.name, server_name))

    @app_commands.command(name="list_autos")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.guilds(discord.Object(441425708896747532))
    async def list_autos(self, interaction: discord.Interaction):
        await interaction.response.defer()
        autos = self.bot.db.auto.find({'discord_server': interaction.guild_id}, limit=5)
        embed = discord.Embed(title="Autos list", type="rich")
        for auto in autos:
            embed.add_field(name=auto['name']+" | "+AutomationType(auto['auto_type']).name.upper(), value=str(auto['frequency'])+" minutes")
        if autos.retrieved == 0:
            await interaction.followup.send(content="You don't have any autos added! Create one with `/create_auto`")
            return
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="delete_auto")
    @app_commands.describe(
            name="The server name to query",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.guilds(discord.Object(441425708896747532))
    async def delete_auto(self, interaction: discord.Interaction, name: str):
        """
        Removes an auto
        """
        await interaction.response.send_message("Auto deleted!")

class Threaded(Thread):
    def __init__(self, bot):
        self.bot = bot
        Thread.__init__(self)
        self.daemon = True
        self.start()


async def setup(bot):
    await bot.add_cog(Automation(bot))
