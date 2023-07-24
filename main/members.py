import discord
from discord.ext import commands
import rethinkdb as r
from urllib.parse import quote

db = r.table("guilds")
def embed(title, description): return discord.Embed(title=title,description=description,color=0x29b6f6)
def error(errormsg): return discord.Embed(title='An Error Occured',description=errormsg,color=0xff0000)
YESEMOJI = '<:yes:426190071473897502>'
NOEMOJI = '<:no:426190098854445059>'
YESREACT = ':yes:426190071473897502'
NOREACT = ':no:426190098854445059'

class Members:
    """These commands are for use by members who are using the applications."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["app list"])
    @commands.guild_only()
    async def positions(self, ctx):
        data = self.bot.db.get(str(ctx.guild.id))["apps"].run(self.bot.conn)

        whichapp = embed('All Applications',f'These are all the available positions in {ctx.guild.name}.')
        appnum = 0
        applicable = {}
        for app, appdata in data.items():
            if appdata['open']:
                status = 'Open'
            else: status = 'Closed'
            appnum += 1
            applicable[app] = appdata

            whichapp.add_field(
                name = str(appnum) + '. ' + app,
                value = f"""
                    Type: {appdata['type']}
                    Total Questions: {len(appdata['app'])}
                    Status: {status}
                """
            )
        await ctx.send(embed = whichapp)
        
    @commands.command(aliases=['questions'])
    async def format(self, ctx, *, app):
        data = self.bot.db.get(str(ctx.guild.id))["apps"].run(self.bot.conn)
        if app not in data: return await ctx.send(embed=error(f'The application "{app}" was not found. Type `{ctx.prefix}positions` to view the available applications.'))
        appdata = data[app]
        exampleapp = embed(f'{appdata["type"].capitalize()} for {app}: {ctx.author.display_name}',f"This is the application format for the server {ctx.guild.name}.")
        for question in appdata["app"]:
            exampleapp.add_field(name=question,value='(Your answer)')
        exampleapp.set_footer(text=f'Ready to {appdata["type"]}? Type `{ctx.prefix}{appdata["type"]}` in {ctx.guild.name}!')
        await ctx.send(embed=exampleapp)
        
    @commands.command(aliases=['register','report'])
    @commands.guild_only()
    async def apply(self, ctx, *, appname = None):
        """Apply for a position using this command."""
        data = await self.bot.data(ctx.guild.id)
        applier = ctx.author

        # Blacklisted Check
        for role in ctx.author.roles:
            if str(role.id) in data['blacklist']:
                return await ctx.send(embed=error('You are not allowed to apply.'))

        # Other random actions
        await ctx.message.add_reaction(YESREACT)
        async def waitdm(ctx):
            def channel(message): 
                return message.author == ctx.message.author and message.channel == message.author.dm_channel
            message = await self.bot.wait_for('message',check=channel,timeout=900.0)
            return message

        # If the user isn't in the data yet...
        if not str(ctx.author.id) in data['members']: 
            data['members'][str(ctx.author.id)] = {}
        
        # ---- This section determines which app the user wants. ---- #
        # This function sends the user a menu asking to pick an app, or selecting the only one if there's one.
        async def get_app():
            if len(data['apps']) == 1: # If there's only one application...
                appnum = 1
                applicable = {list(data["apps"].keys())[0]:"fuck"}
            else:
                whichapp = embed('Select an Application','Select an application to continue.')
                whichapp.set_footer(text=f'Wanted to see other applications? You can use {ctx.prefix}apply, {ctx.prefix}register, or {ctx.prefix}report for more options.')
                appnum = 0
                applicable = {}
                for app, appdata in data['apps'].items():
                    if appdata['open']:
                        status = 'Open'
                    else: status = 'Closed'
                    if appdata['type'] != ctx.invoked_with.lower(): continue # Exclude only if the app isn't the specified type
                    appnum += 1
                    applicable[app] = appdata

                    whichapp.add_field(name=str(appnum) + '. ' + app,value=f"Type: {appdata['type']}\nTotal Questions: {len(appdata['app'])}\nStatus: {status}")
                if appnum == 0: return ctx.invoked_with.lower() # If there are no app, we return the invoked cmd to "return return" later
                if len(applicable) == 1: return list(applicable.keys())[0] # If there is only one app of a type, the bot autoselects that single app.
                await ctx.author.send(embed = whichapp)
                gey = {'DM':True} # Forcing the bot to listen to dms
                appnum = await self.bot.getnum(ctx, gey, 1, appnum)
            return list(applicable.keys())[appnum - 1] # Returns the App Name

        tricky = {'apply':f'`{ctx.prefix}register` or `{ctx.prefix}report`','register':f'`{ctx.prefix}apply` or `{ctx.prefix}report`','report':f'`{ctx.prefix}apply` or `{ctx.prefix}register`',}
        if appname is not None: # If appname was provided, then...
            if not appname in data['apps'].keys(): # if app wasn't found,
                await applier.send(embed=error(f'The application {appname} was not found.'))
                appname = await get_app() # we'll ask until it's found.
                if appname in ['apply','register','report']: return await ctx.send(embed=error(f'There were no applications of this type found. Try typing {tricky[appname]}.'))
        else:
            appname = await get_app() # Otherwise if it wasn't provided, we'll ask for it.

            if appname in data['members'][str(ctx.author.id)]: # If the user applied for this position already...
                return await applier.send(embed=error(f'It looks like you\'ve already applied for this position! Please wait for a response.'))

            if appname.lower() in ['apply','register','report']: # Tricky way to exit if no apps of a specific type was found
                return await ctx.send(embed=error(f'There were no applications of this type found. Try typing {tricky[appname.lower()]}.'))
        appdata = data['apps'][appname] # Getting App Data based off of app name
        # ---- Section ends here. ---- #

        # Required role check
        if "requiredrole" in data['apps'][appname]:
            role = discord.utils.get(ctx.guild.roles, id=int(data['apps'][appname]["requiredrole"]))
            if role is not None:
                if role not in ctx.author.roles:
                    return await ctx.author.send(embed=error(f"You must have the {role.name} role to {appdata['type']}."))

        # Closed app check and return
        if not appdata['open']:
            return await ctx.author.send(embed=error('This application is currently closed.'))

        # This section asks to start or not.
        await applier.send(embed=embed(f'{appdata["type"].capitalize()} for {appname}: {ctx.author.name}',appdata['intro']))
        ready = embed('Ready?',f'Ready to {ctx.invoked_with}? (Use reactions to continue)')
        ready.add_field(name=f'{YESEMOJI} Begin',value='Begin filling out the application.')
        ready.add_field(name=f'{NOEMOJI} Cancel',value='Cancel the application')
        ready.set_footer(text='You can type "cancel" at any time to exit.')
        start = await applier.send(embed=ready)
        for reaction in [YESREACT,NOREACT]:
            await start.add_reaction(reaction)
        rct = await self.bot.waitrct(ctx, start, [YESEMOJI, NOEMOJI])
        if rct == NOEMOJI: # If applier selects no, it'll 
            return await applier.send(embed=embed('Application Cancelled','You have cancelled applying.'))

        appemb = embed(f'{appdata["type"].capitalize()} for {appname}: {ctx.author.name}','Enter the answers to the question(s) below.')
        app = await applier.send(embed=appemb)

        answers = []
        # Asking questions start here...
        for qnum, question in enumerate(appdata['app']):

            # Creating the question and adding it to the embed
            appemb.add_field(name=f'{qnum + 1}. {question}',value='(Enter your answer below.)')
            await app.edit(embed=appemb)

            # Officially asking for answer here
            ansobj = await waitdm(ctx)
            answer = ansobj.content

            if answer.lower() == 'cancel': # Cancelling
                return await applier.send(embed=embed('Application Cancelled','You have cancelled applying.'))

            for attachment in ansobj.attachments: # Adding Image Attachments
                answer += f"View [{attachment.filename}]({attachment.url})\n"

            if len(answer) < 1 or len(answer) > 999: # Handler for large answers
                gist_id = self.bot.create_gist(question, answer)
                url = f"https://www.appbot.site/answers/{quote(ctx.guild.name)}/{quote(ctx.author.display_name)}/{quote(appname)}/{gist_id}"
                await applier.send(embed=error(f'Your answer has been converted to a [url]({url}) because it was too long for Discord\'s embed limits. Please answer the next question.'))
                answer = f"*The answer provided by the applier was too long to be displayed within Discord. View the applier's answer [here]({url}).*"

            appemb.set_field_at(qnum, name=f'{qnum + 1}. {question}', value=answer)
            answers.append(answer)
            if qnum + 1 not in [5, 10, 15, 20, 25]:
                continue
            else: # This whole if statement moves the app embed down every 5 answers
                await app.edit(embed=embed(f'{appdata["type"].capitalize()} for {appname}: {ctx.author.name}','Continue downwards to the next message.'))
                app = await applier.send(embed=appemb)

        # App Submission starts here
        while True:
            sure = await applier.send(embed=embed(f'Are you sure?','Are you sure you want to submit your application?'))
            for reaction in [YESREACT,NOREACT]:
                await sure.add_reaction(reaction)
            rct = await self.bot.waitrct(ctx, sure, [YESEMOJI, NOEMOJI])
            if rct == YESEMOJI:
                break
            if rct == NOEMOJI:
                return await applier.send(embed=embed('Application Cancelled','Your application has not been submitted.'))
        if not str(ctx.author.id) in data['members']:
            data['members'][str(ctx.author.id)] = {}
        db.get(str(ctx.guild.id)).update({'members':{str(ctx.author.id):{appname:answers}}}).run(self.bot.conn)
        await applier.send(embed=embed('Application Submitted','Your application has successfully been submitted. '))

        await self.bot.log(ctx, data, 'Application Submitted',f'{ctx.author.name} has just submitted his application for {appname}.')

def setup(bot):
    bot.add_cog(Members(bot))
