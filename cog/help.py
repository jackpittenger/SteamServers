import discord
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        @bot.command(pass_context=True)
        async def help(ctx, command=None):
            """
            Displays information about commands
            s!help
            """
            try:
                if not command:
                    help_embed = discord.Embed(title='Commands',
                                               description='Use `s!help command` for more information!')
                    command_descriptions = ""
                    for y in self.bot.walk_commands():
                        if not y.cog_name and not y.hidden:
                            command_descriptions += '`{}` - {}'.format(y.name, y.help.split("\n")[0]) + '\n'
                    help_embed.add_field(name='Commands', value=command_descriptions, inline=False)
                    return await ctx.send('', embed=help_embed)

                if not self.bot.get_command(command):
                    return await ctx.send("Invalid command!")
                return await ctx.send('', embed=discord.Embed(title=command,
                                                              description=self.bot.get_command(command).help))

            except Exception as e:
                print(e)
                await ctx.send("I can't send embeds! Please add me to this guild with the correct permissions")


def setup(bot):
    bot.add_cog(Help(bot))
