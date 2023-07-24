import discord
from discord.ext import commands
import matplotlib.pyplot as plt
import speedtest
import datetime
import time
import psutil
import json
import os

def embed(title, description = None): return discord.Embed(title=title,description=description,color=0x29b6f6)
def error(errormsg): return discord.Embed(title='An Error Occured',description=errormsg,color=0xff0000)
EMBEDCOLOR = 0x29b6f6
YESEMOJI = '<:yes:426190071473897502>'
NOEMOJI = '<:no:426190098854445059>'
YESREACT = ':yes:426190071473897502'
NOREACT = ':no:426190098854445059'
pinglogs = []
start_time = datetime.datetime.now()

class Other:
    """These commands are not necessary, but exist for extra measure."""
    def __init__(self, bot):
        self.bot = bot
    @commands.command(aliases=['commands'])
    async def help(self, ctx, command = None):

        prefix = ctx.prefix
        if ctx.prefix == "<@424817451293736961> ": prefix = "@AppBot "

        if ctx.guild is not None: # If the command was run in a guild
            data = await self.bot.data(ctx.guild.id)

            helpemb = discord.Embed(
                title="AppBot Help",
                description="Welcome to AppBot's commands! The default prefix is `/` and AppBot mention (`@AppBot`), but you can always customize it in  `/config`. If you would like a more detailed explanation of all the commands, read our website [documentation](https://www.appbot.site/documentation).",
                color=EMBEDCOLOR,
                timestamp=datetime.datetime.utcnow()
            )
            helpemb.set_footer(text=f"Still need help? Type {prefix}support to join the support server.")
            if self.bot.has_perms(ctx, data, 2):
                helpemb.add_field(
                    name=f"{prefix}config",
                    value=f"""
                    The configuration menu allows you to configure everything, from applications, permissions, to the bot's settings. Use reactions to select your desired action.
                    For a detailed explanation of how to use the config command, check out the configuration tab in our [Documentation](https://www.appbot.site/documentation).
                    """)
            if self.bot.has_perms(ctx, data, 1):
                helpemb.add_field(
                    name=f"{prefix}review @member",
                    value="Review a specific member's application based off of the user provided."
                )
                helpemb.add_field(
                    name=f"{prefix}review",
                    value="Have a menu sent allowing you to review members in different ways."
                )
                helpemb.add_field(
                    name=f"{prefix}apps",
                    value="Retrieve a list of submitted applications and basic information about each one."
                )
            for app in data['apps'].values():
                if app['type'] == "apply":
                    helpemb.add_field(
                        name=f"{prefix}apply",
                        value="Apply for a position in this server."
                    )
                    break
            for app in data['apps'].values():
                if app['type'] == "register":
                    helpemb.add_field(
                        name=f"{prefix}register",
                        value="Register to access this server."
                    )
                    break
            for app in data['apps'].values():
                if app['type'] is "report":
                    helpemb.add_field(
                        name=f"{prefix}report",
                        value="Send a report application into this server."
                    )
                    break
            helpemb.add_field(
                name=f"{prefix}positions",
                value="Get a list of positions to apply for."
            )
            helpemb.add_field(
                name="Other Commands",
                value=f"""
                `{prefix}about` - Gives some information about the bot.
                `{prefix}invite` - Retrieve a bot invite to send to others.
                `{prefix}support` - Retrieve an invite to our support server.
                `{prefix}donate` - Receive a donation link.
                `{prefix}upvote` - Receive links to upvote AppBot.
                `{prefix}ping` - Retrieve the bot's response time in milliseconds.
                """
            )
            await ctx.send(embed=helpemb)
        else: # If the command was run in a DM:
            desc = """
            Welcome to AppBot's help menu! This bot is made to manage applications for your server. 
            AppBot's commands are meant to be used in servers so that the bot knows which server's applications you want to view/edit/apply for.
            We recommend running this command in your server so that you know what commands you are allowed to run.
            The default prefix is `/` and AppBot mention (`@AppBot`), but running `/config` in your server allows you to customize it per server. 
            Read our [documentation](https://www.appbotsite/documentation) to check out all the commands.",
            """
            await ctx.send(embed=embed("AppBot Help",desc))

    @commands.command(brief='Member',description='Get the support server invite link')
    @commands.cooldown(rate=1,per=3.0,type=commands.BucketType.guild)
    async def support(self, ctx):
        await ctx.send(embed=embed('Support Server','**https://www.appbot.site/support**'))

    @commands.command(brief='Member',aliases=['information'])
    async def about(self, ctx):
        about = embed('About AppBot','AppBot- A Bot for In-Discord Job Applications')
        about.add_field(name='Features',value="•Customizable in about every aspect of the app\n•Up to 25 questions\n•Support for multiple job positions\n•Applications are private (In a DM with the applier)")
        about.add_field(name='Guilds',value=f'{len(self.bot.guilds)} (Current Goal: 2500)')
        about.add_field(name='The Bot',value=f'Made by {str(self.bot.get_user(394402252498010113))} in the `Discord.py` Framework')
        about.add_field(name='Support',value='Please support me simply by doing any of the things below:\nUpvote the bot [here](https://discordbots.org/bot/424817451293736961/vote) | Tell your friends about [the bot](https://www.appbot.site)')
        await ctx.send(embed=about)

    @commands.command()
    @commands.cooldown(rate=1,per=3.0,type=commands.BucketType.guild)
    async def upvote(self, ctx):
        upv = embed('Upvote AppBot','Upvotes give a reputation of the bot to bot lists. Upvote the bot to help support it today.')
        upv.add_field(name='Discord Bot List', value='**https://discordbots.org/bot/appbot/vote**')
        await ctx.send(embed=upv)

    @commands.command()
    @commands.cooldown(rate=1,per=3.0,type=commands.BucketType.guild)
    async def invite(self, ctx):
        await ctx.send(embed=embed('Invite','**https://www.appbot.site/invite**'))

    @commands.command()
    @commands.cooldown(rate=1,per=3.0,type=commands.BucketType.guild)
    async def donate(self, ctx):
        await ctx.send(embed=embed('Donate','**https://www.patreon.com/AppBot**'))
    
    @commands.command()
    async def ping(self, ctx):
        """Get the bot's response time"""
        resp = await ctx.send(embed=embed('Pong!','Loading...'))
        diff = resp.created_at - ctx.message.created_at
        totalms = 1000*diff.total_seconds()
        pinglogs.append(totalms)
        edit = embed(f'Pong!',f'Response Time: {abs(totalms)}ms.')
        #edit.add_field(name="Average Ping",value=f"{int(sum(pinglogs)/len(pinglogs))}ms from {len(pinglogs)} tests.")
        await resp.edit(embed=edit)

    @commands.command()
    @commands.cooldown(rate=1,per=3.0,type=commands.BucketType.guild)
    async def uptime(self, ctx):
        """Get the bot's uptime"""
        seconds = time.time() - start_time
        day = int(seconds // (24 * 3600))
        seconds = seconds % (24 * 3600)
        hour = int(seconds // 3600)
        seconds %= 3600
        minutes = int(seconds // 60)
        seconds %= 60
        seconds = int(seconds)
        embed = discord.Embed('Bot Uptime',f'{day} Days, {hour} Hours, {minutes} Minutes, {seconds} Seconds')
        with open('/proc/uptime', 'r') as file:
            seconds = float(file.readline().split()[0])
        day = int(seconds // (24 * 3600))
        seconds = seconds % (24 * 3600)
        hour = int(seconds // 3600)
        seconds %= 3600
        minutes = int(seconds // 60)
        seconds %= 60
        seconds = int(seconds)
        embed.add_field(name='System Uptime',value=f'{day} Days, {hour} Hours, {minutes} Minutes, {seconds} Seconds')
        await ctx.send(embed=embed)

    @commands.command(aliases=['sys'],hidden=True)
    async def system(self, ctx):
        if not ctx.author.id == 394402252498010113:
            return await ctx.send(embed=error('This command is for developers only. *u dont need to see my system stats*'))
        loading = embed("<a:loading:422579038918279169> Loading System Stats...", None)
        stats = await ctx.send(embed=loading,delete_after=30.0)
        emb = embed("Current Bot System Status", None)
        cpupercentage = await self.bot.loop.run_in_executor(None,psutil.cpu_percent)
        emb.add_field(name="CPU Utilization",value=f'{cpupercentage}%')
        memory = await self.bot.loop.run_in_executor(None,psutil.virtual_memory)
        emb.add_field(name="Memory Usage",value=f"{round(memory.used/1048576, 2)}/{round(memory.total/1048576, 2)} MB ({memory.percent}% Used)")
        s = speedtest.Speedtest()
        bestserver = await self.bot.loop.run_in_executor(None,s.get_best_server)
        emb.add_field(name="<a:loading:422579038918279169> Running Internet Speed Test...",value=f'SpeedTest Server Host: [{bestserver["sponsor"]}]({bestserver["url"]}) at {bestserver["name"]}')
        await stats.edit(embed=emb)
        emb.remove_field(2)
        dlspeed = await self.bot.loop.run_in_executor(None,s.download)
        ulspeed = await self.bot.loop.run_in_executor(None,s.upload)
        emb.add_field(name="Download Speed",value=f"{round(dlspeed/1048576,2)} MB/S")
        emb.add_field(name="Upload Speed",value=f"{round(ulspeed/1048576,2)} MB/S")
        await stats.edit(embed=emb)

    @commands.command()
    async def announce(self, ctx,*,content,brief='Developer',description='Announce to all servers that the bot is in'):
        if not ctx.author.id == 394402252498010113:
            return 
        areyousure = await ctx.send(embed=embed("Confirm Action",f"Are you sure you want to send your announcement to {len(bot.guilds)}+ servers?",color=0xff0000))
        for reaction in [YESREACT,NOREACT]:
            await areyousure.add_reaction(reaction)
        def check(reaction,user):
            return reaction.message.id == areyousure.id and user == ctx.message.author and str(reaction.emoji) in [YESEMOJI,NOEMOJI]
        reaction, user = await self.bot.wait_for('reaction_add',timeout=60,check=check)
        servers_sent = 0
        sentto = []
        if str(reaction.emoji) == YESEMOJI:
            for guild in bot.guilds:
                if bot.get_user(253202252821430272) in guild.members or guild.owner.id == 370777160216215553:
                    continue
                try:
                    if guild.owner.id not in sentto:
                        await guild.owner.send(embed=embed('AppBot Announcement', description=content, color=0x29B6F6))
                        servers_sent += 1
                        sentto.append(guild.owner.id)
                except: pass
            await ctx.send(embed=embed('Announcement Sent',f'Your announcement has just been sent to {servers_sent} out of {len(bot.guilds)} servers.'))
        elif str(reaction.emoji) == NOEMOJI:
            ctx.author.send(embed=error('Action cancelled.'))

    @commands.command(hidden=True)
    async def db(self, ctx):
        if not ctx.author.id == 394402252498010113:
            return await ctx.send(embed=error('This command is for developers only. *boi dont be stealing dbs aight?*'))
        hburl = hastebin.post(str(data[ctx.guild.name]).encode('utf-8'))
        hburldivide = hburl.rsplit('com/')
        hbraw = hburldivide[0] + 'com/raw/' + hburldivide[1]
        await ctx.send(embed=embed('Database',hbraw),delete_after=30.0)
        await ctx.message.delete

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send(embed=embed(YESEMOJI + ' AppBot has shut down.'))
        await ctx.message.delete()
        await self.bot.logout()

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def cog_reload(self, ctx, *, cog: str):
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(embed=error(f'{type(e).__name__} - {e}'))
        else:
            await ctx.send('k')
            os.system('clear')

    @commands.command()
    @commands.is_owner()
    async def guilds(self, ctx):
        with open("/home/joshuliu/AppBot/sub/guilds.json") as file:
            data = json.load(file)

        dates = data["dates"]
        appbot = data["appbot"]
        applicationbot = data["applicationbot"]
        plt.plot(dates, appbot, color='blue')
        plt.plot(dates, applicationbot, color='red')
        plt.xlabel('Date (UTC)')
        plt.ylabel('Servers')
        plt.title(f'Servers Since {dates[0]}')
        plt.savefig('graph.png')

        await ctx.send(file=discord.File('/home/joshuliu/AppBot/graph.png'))
    


def setup(bot):
    bot.add_cog(Other(bot))