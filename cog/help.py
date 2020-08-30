import discord
from discord.ext import commands
from helpers import get_prefix

class Help(commands.Cog):
    def __init__(self, bot):
        @bot.command(pass_context=True, name="help")
        async def help_command(ctx, command=None):
            """
            Displays information about commands
            s!help
            """
            try:
                if not command:
                    help_embed = discord.Embed(title='Commands',
                                               description='Use `'+get_prefix(bot, ctx.guild.id)+'help command` for more information!')
                    command_descriptions = ""
                    for y in bot.walk_commands():
                        if not y.cog_name and not y.hidden:
                            command_descriptions += '`{}` - {}'.format(y.name, y.help.split("\n")[0]) + '\n'
                    help_embed.add_field(name='Commands', value=command_descriptions, inline=False)
                    return await ctx.send('', embed=help_embed)

                if not bot.get_command(command):
                    return await ctx.send("Invalid command!")
                return await ctx.send('', embed=discord.Embed(title=command,
                                                              description=bot.get_command(command).help.replace("s!", get_prefix(bot, ctx.guild.id))))

            except Exception as e:
                await ctx.send("I can't send embeds! Please add me to this guild with the correct permissions")


def setup(bot):
    bot.add_cog(Help(bot))
