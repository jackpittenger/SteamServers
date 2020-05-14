import discord
import a2s
import socket
import requests


async def query_logic(ctx, address, sender=None, name=None, bot=None, guild=None):
    sender = sender or ctx.send
    data = address.split(":")
    try:
        info = a2s.info((data[0], int(data[1])))
    except socket.timeout:
        return await sender("Server timeout! Check the IP:Port")
    except socket.gaierror:
        return await sender("Resolution error! Check the IP:Port")
    except IndexError:
        return await sender("Please format your command like: `s!query 144.12.123.51:27017`")
    if guild is not None:
        print("here")
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
    embed.add_field(name="Game", value=info.game)
    return await sender(embed=embed)


async def players_logic(ctx, address):
    data = address.split(":")
    try:
        info = a2s.players((data[0], int(data[1])))
    except socket.timeout:
        return await ctx.send("Server timeout! Check the IP:Port")
    except socket.gaierror:
        return await ctx.send("Resolution error! Check the IP:Port")
    except IndexError:
        return await ctx.send("Please format your command like: `s!query 144.12.123.51:27017`")
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

    max_name_length = len(max([d.name for d in info], key=len))
    max_name_length = max_name_length if max_name_length <= 16 else 16
    output = "Name"+" "*(max_name_length-4)+"|Duration\n"
    output += "¯"*(max_name_length+11)+"\n"
    for player in info:
        output += player.name[0:max_name_length] + " "*(max_name_length-len(player.name))+"|"+player.duration+"\n"
    if len(output) > 1900:
        r = requests.post("https://www.hastepaste.com/api/create", data={"text": output, "raw": "false"})
        if r.status_code == 200:
            return await ctx.send("Too many players for discord! See the players here: "+r.text)
        else:
            return await ctx.send("Your server has too many players to post in Discord, but our HastePaste request "
                                  "failed. Please try again later, or contact support.")
    return await ctx.send("```"+output+"```")


def check_last_amount(bot, guild, name):
    return bot.db.servers.find_one({'discord_server': guild, 'name': name})['timer']


def set_last_amount(bot, guild, name, amount):
    return bot.db.servers.update_one(
        {'discord_server': guild, 'name': name},
        {"$set": {'timer.last': amount}}
    )
