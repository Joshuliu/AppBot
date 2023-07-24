import discord
from discord.ext import commands
import rethinkdb as r
import traceback
import datetime

class CommandErrorHandler:

    def __init__(self, bot):
        self.bot = bot

    async def on_command_error(self, ctx, error):
        err = getattr(error, 'original', error)
        def erroremb(error): return discord.Embed(title='An Error Occured',description=error,color=0xff0000)
        try: 
            if isinstance(err, commands.CommandNotFound):
                return
            await ctx.message.clear_reactions()
            await ctx.message.add_reaction(NOREACT)
        except: pass
        if hasattr(ctx.command, 'on_error'):
            return
        
        ignored = (commands.CommandNotFound)
        
        if isinstance(err, ignored):
            return
        elif isinstance(err, commands.NoPrivateMessage):
            try:
                return await ctx.send(embed=erroremb("This command cannot be used in DMs as the bot does not know which server you are referencing."))
            except: pass
        elif isinstance(err, commands.NotOwner):
            try:
                return await ctx.send(embed=erroremb(f'This command is for developers only.'))
            except:
                pass
        elif isinstance(err, commands.UserInputError):
            try:
                return await ctx.send(embed=erroremb(f'Usage: `{ctx.prefix}{ctx.command.signature}`\nType `{ctx.prefix}help {ctx.command}` for more help.'))
            except:
                pass
        error = traceback.format_exception(type(error), error, error.__traceback__)
        description = ''
        for errorln in error:
            if 'TimeoutError' in errorln:
                return await ctx.author.send(embed=erroremb(f"It looks like you haven't responded in a while. Type `{ctx.prefix}{ctx.command}` to try again."))

            if "KeyError: 'type'" in errorln:
                for appname, appdata in self.bot.db.get(str(ctx.guild.id))["apps"].run(self.bot.conn).items():
                    if "type" not in appdata:
                        self.bot.db.get(str(ctx.guild.id)).replace(r.row.without({"apps":{appname:True}})).run(self.bot.conn)
                await ctx.send(embed=erroremb(f'**IMPORANT**: You have found a major bug that we\'ve been trying to fix for a long time. Originally, this bug would break your entire bot. We have created a temporary solution to allow your bot to continue working, but we still haven\'t found the central cause. If you can consistently reproduce this bug, please join the [support server](https://www.appbot.site) and notify the developer(s). We will reward your server.'))
                return await self.bot.get_channel(427930645365391360).send(embed=erroremb(f'{ctx.guild.name} ({ctx.guild.id}) found a "KeyError: \'type\'" bug.'))

            if isinstance(err, discord.Forbidden):
                if '.send(' in errorln:
                    forbiddenembed = discord.Embed(title='An Error Occured',description="It looks like I was unable to send any messages to you. Please make sure that DMs are enabled in settings.",color=0xff0000)
                    forbiddenembed.set_image(url='https://media.giphy.com/media/fnKmeCXYgceLws1ZE2/giphy.gif')
                    return await ctx.send(embed=forbiddenembed)

            description += '\n' + errorln

        try:
            await ctx.message.clear_reactions()
            await ctx.message.add_reaction(':error:433499721651453952')
            await ctx.author.send(embed=erroremb('An unhandled bug or error has been found and automatically reported. Join the support server [here](https://discord.gg/u5xGqzh) for more information.'))
        except: pass
        try:
            bug = await ctx.channel.create_invite(max_age=86400,max_uses=1)
            embed = discord.Embed(title=f'New Bug Detected',description=f'```py\n{description}```',color=0xff0000,timestamp=datetime.datetime.utcnow())
            embed.add_field(name='Source of Cause',value=f'Guild: [{ctx.guild.name}]({bug.url})\nGuild ID: {ctx.guild.id}\nCommand: {ctx.prefix}{ctx.invoked_with}\nUser: {ctx.author.display_name}\n')
            buglog = self.bot.get_channel(427930645365391360)
            try: await buglog.send(embed=embed)
            except: print(description)
            print(f'An Error Occured: {ctx.command}')
        except:
            embed = discord.Embed(title=f'New Bug Detected',description=f'```py\n{description}```',color=0xff0000,timestamp=datetime.datetime.utcnow())
            embed.add_field(name='Source of Cause',value=f'Guild: (DM Channel)\nCommand: {ctx.prefix}{ctx.invoked_with}\nUser: {ctx.author.display_name}\n')
            buglog = self.bot.get_channel(427930645365391360)
            try: await buglog.send(embed=embed)
            except: print(description)
            print(f'An Error Occured: {ctx.command}')

def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
