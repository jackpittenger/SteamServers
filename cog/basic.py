import discord
from discord import app_commands
from discord.ext import commands
class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot; 

    @app_commands.command(name="ping")
    @app_commands.guilds(discord.Object(441425708896747532))
    async def ping(self, interaction: discord.Interaction) -> None:
        """
        Pings the bot
        """
        await interaction.response.send_message("Pong!", ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Basic(bot))
