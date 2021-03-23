import discord
import a2s
import socket
import requests
from beautifultable import BeautifulTable

async def query_logic(ctx, address, bot, sender=None, name=None, guild=None):
    sender = sender or ctx.send
    data = address.split(":")
    try:
        info = a2s.info((data[0], int(data[1])))
    except socket.timeout:
        return await sender("Server timeout! Check the IP:Port")
    except socket.gaierror:
        return await sender("Resolution error! Check the IP:Port")
    except IndexError:
        if guild is not None:
            return await sender("Please format your command like: `"+get_prefix(bot, guild.id)+"query 144.12.123.51:27017`")
        return
    except Exception as e:
        return await sender("Unknown error! Check the command, and contact support if this continues.")
    if guild is not None:
        last_amount = check_last_amount(bot, guild, name)
        if "last" in last_amount and last_amount["last"] == info.player_count:
            return
        set_last_amount(bot, guild, name, info.player_count)
    embed = discord.Embed(title="Server information",
                          type='rich')
    embed.add_field(name="Address", value=address + "%s%s" % ((" 🛡" if info.vac_enabled else ""),
                                                              (" 🔒" if info.password_protected else "")))
    embed.add_field(name="Server Name", value=info.server_name)
    embed.add_field(name="Map", value=info.map_name)
    embed.add_field(name="Players", value=f'{info.player_count}/{info.max_players}%s' %
                                          f' ({info.bot_count} Bot%s)' % ("s" if (info.bot_count != 1)
                                                                          else ""))
    embed.add_field(name="Game", value=info.game or "Unknown")
    return await sender(embed=embed)


async def players_logic(ctx, address, bot):
    data = address.split(":")
    try:
        info = a2s.players((data[0], int(data[1])))
    except socket.timeout:
        return await ctx.send("Server timeout! Check the IP:Port")
    except socket.gaierror:
        return await ctx.send("Resolution error! Check the IP:Port")
    except IndexError:
        return await ctx.send("Please format your command like: `"+get_prefix(bot, ctx.guild.id)+"pquery 144.12.123.51:27017`")
    except a2s.BufferExhaustedError as e:
        return await ctx.send("Buffer exhausted! Please confirm that the server has the following configuration"
                              ":\n```host_name_store 1\nhost_info_show 1\nhost_players_show 2```")

    if not info or len(info) == 0:
        return await ctx.send("Server is empty!")

    for d in info:
        seconds = d.duration % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        d.duration = "%d:%02d:%02d" % (hour, minutes, seconds)

    table = BeautifulTable()
    table.set_style(BeautifulTable.STYLE_BOX)
    for player in info:
        name = player.name[0:24]
        if name == "":
            name="Connecting..."     
        table.rows.append([name, player.duration, player.score])
    table.columns.header = ["Name", "Duration", "Score"]
    
    if len(str(table)) > 1900:
        r = requests.post("https://www.hastepaste.com/api/create", data={"text": str(table), "raw": "false"})
        if r.status_code == 200:
            return await ctx.send("Too many players for discord! See the players here: "+r.text)
        else:
            return await ctx.send("Your server has too many players to post in Discord, but our HastePaste request "
                                  "failed. Please try again later, or contact support.")
    return await ctx.send("```r\n"+str(table)+"```")


def check_last_amount(bot, guild, name):
    return bot.db.servers.find_one({'discord_server': guild, 'name': name})['timer']


def set_last_amount(bot, guild, name, amount):
    return bot.db.servers.update_one(
        {'discord_server': guild, 'name': name},
        {"$set": {'timer.last': amount}}
    )

def get_prefix(bot, guild_id):
    prefix = bot.db.servers.find_one({'discord_server': guild_id}, {'prefix': 1, '_id': 0})
    if prefix is not None and len(prefix) != 0:
        return prefix["prefix"]
    return bot.default_prefix

