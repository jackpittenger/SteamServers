import discord
from discord.ext import commands
import a2s
import socket


class Valve(commands.Cog):
    def __init__(self, bot):
        @bot.command()
        async def query(ctx, address):
            """
            Queries the server
            :param ctx:
            :param address:
            :return:
            """
            data = address.split(":")

            try:
                info = a2s.info((data[0], int(data[1])))
            except socket.timeout:
                return await ctx.send("Server timeout! Check the IP:Port")
            except socket.gaierror:
                return await ctx.send("Resolution error! Check the IP:Port")

            embed = discord.Embed(title="Server information",
                                  type='rich')
            embed.add_field(name="Address", value=address+"%s%s" % ((" 🛡" if (info['vac_enabled']) else ""),
                                                                    (" 🔒" if info['password_protected'] else "")))
            embed.add_field(name="Server Name", value=info['server_name'])
            embed.add_field(name="Map", value=info['map'])
            embed.add_field(name="Players", value=f'{info["player_count"]}/{info["max_players"]}%s' %
                                                  f' ({info["bot_count"]} Bot%s)' % ("s" if (info['bot_count'] > 1)
                                                                                     else ""))
            embed.add_field(name="Game", value=info['game'])
            return await ctx.send(embed=embed)

        @query.error
        async def do_repeat_handler(ctx, error):
            if isinstance(error, commands.MissingRequiredArgument):
                if error.param.name == 'address':
                    await ctx.send("Please format your command like: `s!query 144.12.123.51:27017`")


def setup(bot):
    bot.add_cog(Valve(bot))
