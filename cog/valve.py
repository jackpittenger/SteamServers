from discord.ext import commands
import discord
from discord import app_commands
from helpers import query_server_for_summary, query_server_for_players  


class Valve(commands.Cog):
    def __init__(self, bot):
        self.bot = bot;
        
    @app_commands.command(name="query")
    @app_commands.describe(
            server_address="The IP:Port to query. For example, 144.12.123.51:27017"
    )
    @app_commands.guilds(discord.Object(441425708896747532))
    async def query(self, interaction: discord.Interaction, server_address: str):
        """
        Queries a server
        """
        await interaction.response.defer()
        summary = await query_server_for_summary(server_address)
        if type(summary) is str:
            await interaction.followup.send(content=summary)
        else:
            await interaction.followup.send(embed=summary)

    @app_commands.command(name="query_players")
    @app_commands.describe(
            server_address="The IP:Port to query. For example, 144.12.123.51:27017"
    )
    @app_commands.guilds(discord.Object(441425708896747532))
    async def query_players(self, interaction: discord.Interaction, server_address: str):
        """
        Queries a server and returns the players
        """
        await interaction.response.defer()
        summary = await query_server_for_players(server_address)
        await interaction.followup.send(content=summary)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Valve(bot))
