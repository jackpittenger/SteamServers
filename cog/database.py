from discord.ext import commands
import discord
from discord import app_commands
from helpers import query_server_for_summary, query_server_for_players  


class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def server_name_autocomplete(self, interaction: discord.Interaction, current: str):
        servers = self.bot.db.servers.find({'discord_server': interaction.guild_id})
        result_dict = []
        for result in servers:
            result_dict.append(discord.app_commands.Choice(name=result['name'], value=result['name']))
        return result_dict
    
    @app_commands.command(name="create_server")
    @app_commands.describe(
            server_address="The IP:Port to query. For example, 144.12.123.51:27017",
            name="The name to give the server. For example, Awesome RP"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.guilds(discord.Object(441425708896747532))
    async def create_server(self, interaction: discord.Interaction, server_address: str, name: str) -> None:
        """
        Create a new saved server. Requires MANAGE_GUILD
        """
        await interaction.response.defer()
        if self.bot.db.servers.count_documents({'discord_server': interaction.guild_id}) > 30:
            await interaction.followup.send(content="You already have too many servers!")
        elif self.bot.db.servers.find_one({'discord_server': interaction.guild_id,"$or":[ {"name":name}, {"address":server_address}]}) is not None:
            await interaction.followup.send(content="Either this server name or server address is already being used!")
        else:
            self.bot.db.servers.insert_one({'discord_server': interaction.guild_id, 'address': server_address, 'name': name})
            await interaction.followup.send(content="Created!")

    @app_commands.command(name="servers")
    @app_commands.guilds(discord.Object(441425708896747532))
    async def servers(self, interaction: discord.Interaction) -> None:
        """
        Lists saved servers 
        """
        await interaction.response.defer()
        results = self.bot.db.servers.find({'discord_server': interaction.guild_id})
        embed = discord.Embed(title="Server list",
                type='rich')
        for result in results:
            embed.add_field(name=result['name'], value=result['address'])
        if results.retrieved == 0: 
            await interaction.followup.send(content="No servers added! Add one with `/create_server`")
            return
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="delete_server")
    @app_commands.autocomplete(server_name=server_name_autocomplete)
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.guilds(discord.Object(441425708896747532))
    async def delete_server(self, interaction: discord.Interaction, server_name: str) -> None:
        """
        Deletes a saved server. Requires MANAGE_GUILD
        """
        await interaction.response.defer()
        result = self.bot.db.servers.delete_one({'discord_server': interaction.guild_id, 'name': server_name})
        if not result.deleted_count:
            await interaction.followup.send(content="Server not found!")
        else:
            self.bot.db.auto.delete_many({'discord_server': interaction.guild_id, 'name': server_name})
            await interaction.followup.send(content=f"Server `{server_name}` deleted")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Database(bot))
