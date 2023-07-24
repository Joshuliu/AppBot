import discord
from discord.ext import commands
import asyncio
import speedtest
import requests
import hastebin
import itertools
import datetime
import aiohttp
import psutil
import logging
import time
import json
import os

with open('prefixes.json') as file:
    prefixes = json.load(file)
def customprefix(bot, message):
    try:
        prefixlist = prefixes[str(message.guild.id)]
        if os.path.basename(__file__) == 'appbotdev.py': 
            prefixlist.append('.')
        return commands.when_mentioned_or(*prefixlist)(bot,message)
    except:
        return '/'
bot = commands.AutoShardedBot(command_prefix=customprefix,case_insensitive=True)
bot.remove_command('help')

import rethinkdb as r
bot.conn = r.connect(db="appbot")
db = r.table("guilds")
bot.db = r.table("guilds")

EMBEDCOLOR = 0x29b6f6
LOADINGEMOJI = '<a:loading:422579038918279169>'
YESEMOJI = '<:yes:426190071473897502>'
NOEMOJI = '<:no:426190098854445059>'
YESREACT = ':yes:426190071473897502'
NOREACT = ':no:426190098854445059'
start_time = time.time()

# DEFAULT = {"apps":{},"members":{},'DM':True, 'blacklist':[], 'logs': None, 'archives': None, 'appeditroles': [], 'appreviewroles': []}

# DATA FUNCTIONS
async def get_data(guild_id):
    data = db.get(str(guild_id)).run(bot.conn)
    if data is not None:
        return data
    else:
        data = {"id":str(guild_id),"apps":{},"members":{},'DM':True, 'blacklist':[], 'logs': None, 'archives': None, 'appeditroles': [], 'appreviewroles': []}
        db.insert(data).run(bot.conn)
        return data 

async def save_data(guild_id,data):
    db.get(str(guild_id)).update(data).run(bot.conn)

# OTHER GLOBAL FUNCTIONS
def embed(title, description = None): return discord.Embed(title=title,description=description,color=EMBEDCOLOR)
def error(errormsg): return discord.Embed(title='An Error Occured',description=errormsg,color=0xff0000)
def getchannel(ctx, data):
    if data['DM']:
        return ctx.author
    else:
        return ctx

async def waitmsg(ctx, dm, obj=False):
    def channel(message): 
        if dm:
            return message.author == ctx.message.author and message.channel == message.author.dm_channel
        else: return message.author == ctx.message.author and message.channel == ctx.message.channel
    message = await bot.wait_for('message',check=channel,timeout=300.0)
    if obj:
        return message
    else:
        return message.content
async def waitrct(ctx, message, reactions):
    def rctcheck(reaction,user): 
        return reaction.message.id == message.id and user == ctx.message.author and str(reaction.emoji) in reactions
    reaction, user = await bot.wait_for('reaction_add',timeout=300.0,check=rctcheck)
    return str(reaction.emoji)

async def getnum(ctx, data, min, max): #Getting a number within a provided range
    global channel
    user = getchannel(ctx, data)
    def channel(message): 
        if data['DM']:
            return message.author == ctx.message.author and message.channel == message.author.dm_channel
        else: return message.author == ctx.message.author and message.channel == ctx.message.channel
    while True:
        anum = await bot.wait_for('message',check=channel,timeout=600.0)
        try: 
            anum = int(anum.content)
            if min <= anum <= max:
                return anum
            else:
                await user.send(embed=error(f'Please enter a valid question number in within {min} and {max}.'))
        except: 
            await user.send(embed=error('Please enter a number.'))
async def areyousure(ctx, data, suredesc):
    global channel
    areyousure = await getchannel(ctx, data).send(embed=embed("Are you sure?",suredesc))
    for reaction in [YESREACT,NOREACT]:
        await areyousure.add_reaction(reaction)
    reaction = await waitrct(ctx, areyousure, [YESEMOJI,NOEMOJI])
    if reaction == YESEMOJI:
        return True
    else: return False
async def getapp(ctx, data):
    user = getchannel(ctx, data)
    if len(data['apps']) == 1:
        appnum = 1
    else:
        whichapp = embed('Select an Application','Select an application to continue.')
        appnum = 0
        for app, appdata in data['apps'].items():
            appnum += 1
            if appdata['open']:
                status = 'Open'
            else: status = 'Closed'
            whichapp.add_field(name=str(appnum) + '. ' + app,value=f"Type: {appdata['type']}\nTotal Questions: {len(appdata['app'])}\nStatus: {status}")
        await user.send(embed = whichapp)
        appnum = await getnum(ctx, data, 1, len(data['apps']))
    return list(data['apps'].keys())[appnum - 1] # Returns the App Name
async def cancel(text):
    if text.lower() == 'cancel':
        return True
    else: return False
async def log(ctx, data, action, description):
    log_id = data['logs']
    if log_id is None: return

    logchannel = bot.get_channel(int(log_id))
    if logchannel is None: return await ctx.author.send(embed=error("The bot was unable to log an action. Please resolve this issue as soon as possible."))

    try: await logchannel.send(embed=discord.Embed(title=action, description=description, color=EMBEDCOLOR, timestamp=datetime.datetime.utcnow()))
    except: await ctx.author.send(embed=error("The bot was unable to log an action. Please resolve this issue as soon as possible."))

def has_perms(ctx, data, permtype :int): # 0 = no perms, 1 = review perms, 2 = config perms
    if permtype not in [0, 1, 2]: return print('INVALID PERMTYPE')
    if ctx.author.guild_permissions.administrator:
        return True
    for role in ctx.author.roles:
        if str(role.id) in data['appeditroles']:
            if permtype is 2:
                return True
        if str(role.id) in data['appreviewroles']:
            if permtype is 1:
                return True
    return False
def create_gist(q, a):
    data = requests.post(
        "https://api.github.com/gists", 
        json = {
            "description": "AppBot - a Discord bot made for staff application management within Discord.",
            "public": True,
            "files": {
                "answer.md": {
                    "content": f"# {q}\n#### {a}"
                }
            }
        }, 
        headers = {
            'Content-Type' : 'application/json',
            "Authorization": "token e03nfsdl49g0fvajsdkf2j4i9340rwkejf2q0w0eo9"
        }
    )
    data = json.loads(data.content.decode('utf-8')) # Convert bytes to str, str to json
    gist_id = data['html_url'][24:]
    return gist_id

bot.session = aiohttp.ClientSession(loop=bot.loop)

startup_extensions = [
    "main.administrator",
    "main.reviewer",
    "main.members",
    "sub.error handler",
    "sub.post servers",
    "sub.eval",
    "sub.other"
]
for extension in startup_extensions:
    try:
        bot.load_extension(extension)
    except Exception as e:
        exc = f"{type(e).__name__}: {e}"
        print(f'Failed to load extension {extension}\n{exc}')

bot.data = get_data
bot.save = save_data
bot.getchannel = getchannel
bot.prefixes = prefixes

bot.waitmsg = waitmsg
bot.waitrct = waitrct
bot.getnum = getnum
bot.sure = areyousure
bot.has_perms = has_perms
bot.log = log

bot.create_gist = create_gist
bot.get_app = getapp
bot.cancel = cancel


@bot.event
async def on_ready():
    os.system("clear")
    print("\n\n████████████████████████████████████████████████████████\n")
    print(" ______                  _____           __                   ")
    print("/\  _  \                /\  __`\        /\ \__                ")
    print("\ \ \L\ \  _____   _____\ \ \L\ \    ___\ \ ,_\               ")
    print(" \ \  __ \/\ '__`\/\ '__`\ \  _ <'  / __`\ \ \/               ")
    print("  \ \ \/\ \ \ \L\ \ \ \L\ \ \ \L\ \/\ \L\ \ \ \_              ")
    print("   \ \_\ \_\ \ ,__/\ \ ,__/\ \____/\ \____/\ \__\             ")
    print("    \/_/\/_/\ \ \/  \ \ \/  \/___/  \/___/  \/__/             ")
    print("             \ \_\   \ \_\                                    ")
    print("              \/_/    \/_/   AppBot 2.0 - 2x more bugs        ")
    print("\n████████████████████████████████████████████████████████\n\n")

@bot.event
async def on_guild_join(guild):
    await guild.owner.send(embed=embed('Thank you for adding AppBot!','Thank you for adding AppBot, the most feature-packed bot made for applications built into Discord!\n\nReady to get started?\nType `/config` to create your first application.\n\nWhat\'s next?\nType `/config` after setting up your first application to access a menu which allows you to add more applications, set a log channel, change the prefix, and much more.\n\nIf you require more assistance, please join the [support server](https://www.appbot.gq/support).'))

@bot.event
async def on_message(message):
    appbotguild = discord.utils.get(bot.guilds, id = 423374132873527297)
    ctx = await bot.get_context(message)
    if ctx.valid:
        if ctx.author.bot: return
        if not bot.is_ready(): return await message.channel.send(embed=error("The bot is still starting up. Please wait patiently."))
        await bot.invoke(ctx)

@bot.event
async def on_member_remove(member):
    data = await get_data(member.guild.id)
    if str(member.id) in data['members']:
        db.get(str(member.guild.id)).replace(r.row.without({'members':{str(member.id):True}})).run(bot.conn)

async def presence():
    await bot.wait_until_ready()
    cycle = ['apps for {} users'.format(len(bot.users)),'apps for {} servers'.format(len(bot.guilds)),f'for @AppBot help']
    statusnum = 0
    while not bot.is_closed():
        await bot.change_presence(activity=discord.Activity(name=cycle[statusnum],type=discord.ActivityType.watching))
        statusnum += 1
        if statusnum == 2: statusnum = 0
        await asyncio.sleep(30)

bot.loop.create_task(presence())

#███████████████████████████████████████ Startup █████████████████████████████████████████

#███████████████ 🔽 Main Bot 🔽 ████████████████████
if os.path.basename(__file__) == 'appbot.py': 
    bot.run(MAIN_BOT_TOKEN)
elif os.path.basename(__file__) == 'appbotdev.py':
    bot.run(TEST_BOT_TOKEN)
else: 
    print("This file must be called \"appbot.py\" or \"appbotdev.py\". Connection closed.")
#███████████████ 🔼 Test Bot 🔼 ████████████████████

#█████████████████████████████████████████████████████████████████████████████████████████
