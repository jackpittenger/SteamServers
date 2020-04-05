import discord
import valve.source.a2s as a2s


async def query_logic(ctx, address):
    data = address.split(":")
    with a2s.ServerQuerier((data[0], int(data[1])), timeout=5) as server:
        info = server.info()
    embed = discord.Embed(title="Server information",
                          type='rich')
    embed.add_field(name="Address", value=address + "%s%s" % ((" 🛡" if (info['vac_enabled']) else ""),
                                                              (" 🔒" if info['password_protected'] else "")))
    embed.add_field(name="Server Name", value=info['server_name'])
    embed.add_field(name="Map", value=info['map'])
    embed.add_field(name="Players", value=f'{info["player_count"]}/{info["max_players"]}%s' %
                                          f' ({info["bot_count"]} Bot%s)' % ("s" if (info['bot_count'] > 1)
                                                                             else ""))
    embed.add_field(name="Game", value=info['game'])
    return await ctx.send(embed=embed)
