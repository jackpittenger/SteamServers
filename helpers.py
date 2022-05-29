import discord
import a2s
import socket
import requests
from beautifultable import BeautifulTable

async def query_server_for_summary(address: str):
    data = address.split(":")
    try:
        info = a2s.info((data[0], int(data[1])))
    except socket.timeout:
        return "Server timeout! Check the IP:Port"
    except socket.gaierror:
        return "Resolution error! Check the IP:Port"
    except IndexError:
        return "Please format your command like: `/query 144.12.123.51:27017`"
    except Exception as e:
        return "Unknown error! Check the command, and contact support if this continues."
    
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
    return embed


async def query_server_for_players(address: str):
    data = address.split(":")
    try:
        info = a2s.players((data[0], int(data[1])))
    except socket.timeout:
        return "Server timeout! Check the IP:Port"
    except socket.gaierror:
        return "Resolution error! Check the IP:Port"
    except IndexError:
        return "Please format your command like: `/pquery 144.12.123.51:27017`"
    except a2s.BufferExhaustedError as e:
        return "Buffer exhausted! Please confirm that the server has the following configuration:\n```host_name_store 1\nhost_info_show 1\nhost_players_show 2```"

    if not info or len(info) == 0:
        return "Server is empty!"

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
        name = player.name[0:24].encode("ascii", "ignore").decode()
        if name == "":
            name="Connecting..."     
        table.rows.append([name, player.duration, player.score])
    table.columns.header = ["Name", "Duration", "Score"]
    
    if len(str(table)) > 1900:
        r = requests.post("https://www.hastepaste.com/api/create", data={"text": str(table), "raw": "false"})
        if r.status_code == 200:
            return "Too many players for discord! See the players here: "+r.text
        else:
            return "Your server has too many players to post in Discord, but our HastePaste request failed. Please try again later, or contact support."
    return "```r\n"+str(table)+"```"


def check_last_amount(bot, guild, name):
    return bot.db.servers.find_one({'discord_server': guild, 'name': name})['timer']


def set_last_amount(bot, guild, name, amount):
    return bot.db.servers.update_one(
        {'discord_server': guild, 'name': name},
        {"$set": {'timer.last': amount}}
    )
