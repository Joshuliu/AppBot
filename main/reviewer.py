import discord
from discord.ext import commands
import rethinkdb as r

def embed(title, description): return discord.Embed(title=title,description=description,color=0x29b6f6)
def error(errormsg): return discord.Embed(title='An Error Occured',description=errormsg,color=0xff0000)
YESEMOJI = '<:yes:426190071473897502>'
NOEMOJI = '<:no:426190098854445059>'
YESREACT = ':yes:426190071473897502'
NOREACT = ':no:426190098854445059'

class Reviewer:
    """These commands can only be run by people who have the administrator permission or have the required roles."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['apps'])
    @commands.guild_only()
    async def applications(self, ctx):

        data = await self.bot.data(ctx.guild.id)
        if not self.bot.has_perms(ctx, data, 1): return await ctx.send(embed=error('You do not have permission to use this command.'))

        unreviewed = embed('Unreviewed Appliers', None) # Creating an embed showing app info by users
        unreviewed.set_footer(text=f'Tip: You can review a specific user with `{ctx.prefix}review @member`, or type `{ctx.prefix}review` by itself for more reviewing options.')
        for applierid, applierinfo in data['members'].items():
            applier = discord.utils.get(ctx.guild.members, id=int(applierid))
            if applier == None:
                continue
            if applierinfo == {}:
                continue

            apps = [] # Getting apps together "like, this"
            for appname in data['members'][applierid].keys():
                apps.append(appname) 
            apps = ', '.join(apps)

            info = f'ID: {applierid}\nMention: {applier.mention}\nSubmitted Applications: {apps}'

            unreviewed.add_field(name=str(applier),value=info)

        if len(unreviewed.fields) == 0: # If no one actually applied...
            return await ctx.send(embed=embed('No Applications Submitted','No applications have been submitted at the moment.'))

        await ctx.send(embed=unreviewed)

    async def decision(self, ctx, data, applierobj, appname, cancelling : bool = False):

        user = self.bot.getchannel(ctx, data)
        appdata = data['apps'][appname]

        actionembed = embed('Action Menu','Use reactions to make an action.')
        actionembed.add_field(name=f"{YESEMOJI} Accept Application",value=f"Select the check mark to accept {applierobj.name}'s application for {appname}.")
        actionembed.add_field(name=f":stop_button: Ignore Application",value=f"Select this button to leave {applierobj.name}'s application for {appname} unreviewed.")
        if cancelling: actionembed.add_field(name=f":no_entry: Stop Reviewing",value=f"Select this button to stop reviewing all applications.")
        actionembed.add_field(name=f"{NOEMOJI} Deny Application",value=f"Select the x to deny {applierobj.name}'s application for {appname}.")

        action = await user.send(embed=actionembed)

        if not cancelling: # Getting Applicable Reactions
            reacting = [YESREACT,"⏹",NOREACT]
            emojiing = [YESEMOJI,"⏹",NOEMOJI]
        else:
            reacting = [YESREACT,"⏹","⛔",NOREACT]
            emojiing = [YESEMOJI,"⏹","⛔",NOEMOJI]
        for reaction in reacting: # Adding Applicable Reactions
            await action.add_reaction(reaction)

        rct = await self.bot.waitrct(ctx, action, emojiing)

        exemb = embed(f'{appdata["type"].capitalize()} for {appname}: {applierobj.name}',f'This is the application for {appname}, sent by {applierobj.name}.')
        for q, a in zip(appdata['app'], data['members'][str(applierobj.id)][appname]):
            exemb.add_field(name=q,value=a)

        if rct == YESEMOJI:
            exemb.color = 0x00ff00
            await self.bot.log(ctx, data, f"Application Accepted",f'{ctx.author.display_name} has accepted {applierobj.name}\'s application for {appname}.')
            await applierobj.send(embed=embed('Application Accepted',appdata['accept']))
            await user.send(embed=embed('Application Accepted',f'You have accepted {applierobj.name}\'s application.'))

            if 'acceptrole' in data['apps'][appname]: # Acceptance Role
                memberobj = discord.utils.get(ctx.guild.members, id = applierobj.id)
                acceptrole = discord.utils.get(ctx.guild.roles, id = int(data['apps'][appname]['acceptrole']))
                try: await memberobj.add_roles(acceptrole, reason=f"{appname} Application by {applierobj.name} accepted by {ctx.author.name}")
                except: await ctx.author.send(embed=error(f'The bot was unable to give the user an autorole. Please fix this error immediately.\n`{ctx.prefix}config` > Application Settings > Edit Application > {appname} > Edit Acceptance Role'))

            r.table("guilds").get(str(ctx.guild.id)).replace(r.row.without({'members':{str(applierobj.id):{appname:True}}})).run(self.bot.conn)
        if rct == "⏹": await user.send(embed=embed('Application Ignored',f'You have ignored {applierobj.name}\'s application.'))
        if rct == "⛔":
            await user.send(embed=embed('Stopped Reviewing',f'You have stopped reviewing all applications.'))
            return 'cancel'
        if rct == NOEMOJI:
            exemb.color = 0xff0000
            await user.send(embed=embed('Denial Message',f'Enter a reason for why {applierobj.name}\'s application was denied.'))
            reason = await self.bot.waitmsg(ctx, data['DM'])
            await self.bot.log(ctx, data, f"Application Denied",f'{ctx.author.display_name} has denied {applierobj.name}\'s application for {appname} with the following reason: {reason}')
            await applierobj.send(embed=embed('Application Denied','Unfortunately, your application for ' + appname + ' was denied because of the following: ' + reason))
            r.table("guilds").get(str(ctx.guild.id)).replace(r.row.without({'members':{str(applierobj.id):{appname:True}}})).run(self.bot.conn)
            await user.send(embed=embed('Denial Successful',f'You have successfully denied {applierobj.display_name}.'))

        if rct in [YESEMOJI,NOEMOJI]:
            if data['archives'] is not None: # Archives
                channel = self.bot.get_channel(int(data['archives']))
                try: await channel.send(embed=exemb)
                except: await ctx.author.send(embed=error(f'The bot was unable to send the archived application. Please fix this error immediately.\n`{ctx.prefix}config` > Channels and Permissions > Set an archives channel'))

    @commands.command(aliases=['view'])
    @commands.guild_only()
    async def review(self, ctx, *, applier : discord.Member = None):
        data = await self.bot.data(ctx.guild.id)
        user = self.bot.getchannel(ctx, data)
        if not self.bot.has_perms(ctx, data, 1): return await ctx.send(embed=error('You do not have permission to use this command.'))
        await ctx.message.add_reaction(YESREACT)

        if applier is not None: # If user actually provided a name:

            # If the applier is in the db
            if str(applier.id) in data['members']:
                # If the data of the member isn't empty, continue on.
                if data['members'][str(applier.id)] != {}: pass

            else: 
                return await ctx.send(embed=error(f'The user {applier.display_name} has never applied. Please try again.'))
                # Otherwise, return with an error saying that the user has never applied before

            userapps = data['members'][str(applier.id)] # Dict of user apps
            if len(userapps) == 1: # If user only applied for one position...
                appnum = 1 # Select this app
            else: # Otherwise, make the reviewer select the user's app
                whichapp = embed('Select an Application','Select an application to continue.')
                appnum = 0
                for app, appdata in userapps.items():
                    appnum += 1
                    whichapp.add_field(name=str(appnum) + '. ' + app,value=f"Total Questions: {len(appdata)}")
                await user.send(embed = whichapp)
                appnum = await self.bot.getnum(ctx, data, 1, len(userapps))
                # Getting the specific app from a min/max number ^

            appname = list(userapps.keys())[appnum - 1]
            userans = userapps[appname]
            appdata = data['apps'][appname]

            exemb = embed(f'{appdata["type"].capitalize()} for {appname}: {applier.name}',f'This is the application for {appname}, sent by {applier.name}.')
            for q, a in zip(appdata['app'], userans):
                exemb.add_field(name=q,value=a)
            await user.send(embed=exemb)

            await self.decision(ctx, data, applier, appname)

        else:

            # Actual reviewing embeds start here
            unreviewed = embed('Unreviewed Appliers', None) # Creating an embed showing app info by users
            unreviewed.set_footer(text=f'Tip: You can review by app name, or review all applications at once by typing `{ctx.prefix}review` by itself.')
            for applierid, applierinfo in data['members'].items():
                applier = discord.utils.get(ctx.guild.members, id=int(applierid))
                if applier == None:
                    continue
                if applierinfo == {}:
                    continue

                apps = [] # Getting apps together "like, this"
                for appname in data['members'][applierid].keys():
                    apps.append(appname) 
                apps = ', '.join(apps)

                info = f'ID: {applierid}\nMention: {applier.mention}\nSubmitted Applications: {apps}'

                unreviewed.add_field(name=str(applier),value=info)

            if len(unreviewed.fields) == 0: # If no one actually applied...
                return await ctx.send(embed=embed('No Applications Submitted','No applications have been submitted at the moment.'))


            await user.send(embed=unreviewed)
            revopts = embed('Reviewer Options','Select what to do next using reactions.')
            revopts.add_field(name=':one: Review Specific Member',value='Review a specific member by name.')
            revopts.add_field(name=':two: Review by Application Name',value='Review all submitted applications from an application name.')
            revopts.add_field(name=':three: Review all Applications',value='Review every single application.')
            revopts.add_field(name=':four: Cancel',value='Exit the review menu.')
            revcfg = await user.send(embed=revopts)

            for reaction in ["1⃣","2⃣","3⃣","4⃣"]: 
                await revcfg.add_reaction(reaction)
            rct = await self.bot.waitrct(ctx, revcfg, ["1⃣","2⃣","3⃣","4⃣"])

            if rct == "1⃣":

                # Getting the specified user
                await user.send(embed=embed('Which user?','Which user would you like to review?'))
                while True:
                    whichuser = await self.bot.waitmsg(ctx, data['DM'])
                    try:
                        userobj = await commands.MemberConverter().convert(ctx,whichuser) 
                    except:
                        await user.send(embed=error(f'The user {whichuser} was not found. Please try again.'))
                        continue
                    if str(userobj.id) in data['members'] and data['members'][str(userobj.id)] != {}:
                        break
                    else:
                        if data['members'][str(userobj.id)] == {}:
                            del data['members'][str(userobj.id)]
                        await user.send(embed=error(f'The user {whichuser} has never applied. Please try again.'))

                # This section gets the specific user's app
                userapps = data['members'][str(userobj.id)]
                if len(userapps) == 1:
                    appnum = 1
                else:
                    whichapp = embed('Select an Application','Select an application to continue.')
                    appnum = 0
                    for app, appdata in userapps.items():
                        appnum += 1
                        whichapp.add_field(name=str(appnum) + '. ' + app,value=f"Total Questions: {len(appdata)}")
                    await user.send(embed = whichapp)
                    appnum = await self.bot.getnum(ctx, data, 1, len(userapps))

                appname = list(userapps.keys())[appnum - 1]
                userans = userapps[appname]
                appdata = data['apps'][appname]

                exemb = embed(f'{appdata["type"].capitalize()} for {appname}: {userobj.name}',f'This is the application for {appname}, sent by {userobj.name}.')
                for q, a in zip(appdata['app'], userans):
                    exemb.add_field(name=q,value=a)
                await user.send(embed=exemb)

                await self.decision(ctx, data, userobj, appname)

            elif rct == "2⃣":

                appname = await self.bot.get_app(ctx, data)
                appdata = data['apps'][appname]

                reviewing = {} # Puts together a dict of apps for a specific role
                for userid, apps in data['members'].items():
                    user = discord.utils.get(ctx.guild.members, id = int(userid))
                    if user is None: continue
                    username = user.name
                    for userappname in apps.keys(): 
                        if userappname == appname:
                            reviewing[userid] = data['members'][userid][appname]

                if reviewing == {}: # If no apps for a position was found...
                    return await user.send(embed=error(f'No applications for {appname} have been found.'))

                for userid, userapp in reviewing.items(): # For every app in the review list
                    user = discord.utils.get(ctx.guild.members, id = int(userid))
                    if user is None: continue
                    username = user.name
                    exemb = embed(f'{appdata["type"].capitalize()} for {appname}: {username}',f'This is the application for {appname}, sent by {username}.')
                    for q, a in zip(appdata['app'], userapp): # Creating \_
                        exemb.add_field(name=q,value=a)  #             \_the app embed is here
                    await user.send(embed=exemb) # Sending the app

                    decision = await self.decision(ctx, data, self.bot.get_user(int(userid)), appname, True)
                    if decision is 'cancel': return # Exit if user stopped reviewing

                await user.send(embed=embed(f'All Apps for {appname} Reviewed',f'No more applications for {appname} left here.'))

            elif rct == "3⃣":

                for appname, appdata in data['apps'].items():
                    reviewing = {} # Puts together a dict of apps for a specific role
                    for userid, apps in data['members'].items():
                        userobj = self.bot.get_user(int(userid))
                        if userobj is None: continue
                        username = userobj.name
                        for userappname in apps.keys(): 
                            if userappname == appname:
                                reviewing[userid] = data['members'][userid][appname]

                    if reviewing == {}: # If no apps for a position was found...
                        continue

                    for userid, userapp in reviewing.items(): # For every app in the review list
                        username = discord.utils.get(ctx.guild.members, id = int(userid))
                        exemb = embed(f'{appdata["type"].capitalize()} for {appname}: {username}',f'This is the application for {appname}, sent by {username}.')
                        for q, a in zip(appdata['app'], userapp): # Creating \_
                            exemb.add_field(name=q,value=a)  #             \_the app embed is here
                        await user.send(embed=exemb) # Sending the app

                        decision = await self.decision(ctx, data, self.bot.get_user(int(userid)), appname, True)
                        if decision is 'cancel': return # Exit if user stopped reviewing
                await user.send(embed=embed('All Applications Reviewed','You have finished reviewing all submitted applications.'))

            elif rct == "4⃣":
                await user.send(embed=embed('Review Menu Exited','You have successfully exited the menu.'))
                return

def setup(bot):
    bot.add_cog(Reviewer(bot))