import discord
from discord.ext import commands
import rethinkdb as r
import asyncio
import json

EMBEDCOLOR = 0x29b6f6
LOADINGEMOJI = '<a:loading:422579038918279169>'
YESEMOJI = '<:yes:426190071473897502>'
NOEMOJI = '<:no:426190098854445059>'
YESREACT = ':yes:426190071473897502'
NOREACT = ':no:426190098854445059'

# ['1⃣','2⃣','3⃣','4⃣','5⃣']

def embed(title, description): return discord.Embed(title=title,description=description,color=0x29b6f6)
def error(errormsg): return discord.Embed(title='An Error Occured',description=errormsg,color=0xff0000)

class Administrator:
    """These commands can only be run by people who have the administrator permission, or have a pe"""
    def __init__(self, bot):
        self.bot = bot

    async def app_setup(self, ctx, app_name, guild_data):

        user = self.bot.getchannel(ctx, guild_data)
        data = {}

        # Getting the application type
        app_type = await user.send(embed=embed('What type of application are you creating? Use reactions to select.','**1. Job** - The user is sending in an application for a position, whether it\'s for a position like moderator, builder, etc.\n\n**2. Registration** - The user is registering, whether it would be for member verification, or getting basic information from members before they get access to all the channels.\n\n**3. Report** If you are using this for some kind of bug report application, or some behavior report application, this option would be perfect for you.'))
        reactions = ['1⃣','2⃣','3⃣']
        for reaction in reactions:
            await app_type.add_reaction(reaction)
        apprct = await self.bot.waitrct(ctx, app_type, reactions)
        types = {'1⃣':'apply','2⃣':'register','3⃣':'report'}
        data['type'] = types[apprct]
        apptype = types[apprct]

        # Getting a required role
        areyousure = await user.send(embed=embed("Add a Required Role?","Set a specific required role to apply for a position. (e.g. You must have moderator to apply for administrator.)"))
        for reaction in [YESREACT,NOREACT]:
            await areyousure.add_reaction(reaction)
        choice = await self.bot.waitrct(ctx, areyousure, [YESEMOJI, NOEMOJI])
        if choice == YESEMOJI:
            while True:
                await user.send(embed=embed('Select Role','What role must be required to apply? (Enter the name of a role)'))
                role = await self.bot.waitmsg(ctx, guild_data['DM'])
                try: 
                    roleobj = await commands.RoleConverter().convert(ctx, role)
                    data['requiredrole'] = str(roleobj.id)
                    break
                except:
                    errperms = error('The specified role was not found. Please try again.')
                    await user.send(embed=errperms)
        else: await user.send(embed=embed("Action cancelled.",f'The bot will not give the accepted applier a role. You can change this later.'))

        # Getting an introduction
        while True:
            intro_examples = {'1⃣':f'Thank you for applying for {app_name}! Make sure to answer all the questions truthfully.','2⃣':f'Thank you for registering as a {app_name}! Make sure to be honest.','3⃣':f'Thanks for reporting this user. Make sure to be honest in your report application.'}
            await user.send(embed=embed('Send an Introduction. This is the first message that the user sees before starting their application. An example is shown below:',intro_examples[apprct]))
            intro = await self.bot.waitmsg(ctx, guild_data['DM'])
            if await self.bot.cancel(intro): return None
            if len(intro) > 999: await user.send(embed=error("Your introduction must have less than 1000 characters. Please try again."))
            else: break
        data['intro'] = intro


        # Getting app questions ---------------------

        # Creating the example app, with the embed
        exemb = embed(f'{apptype.capitalize()} for {app_name}: {ctx.author.name}',f'Enter all your questions seperately below. When you are done, react to this message with {YESEMOJI}.')
        exapp = await user.send(embed=exemb)
        exrct = await exapp.add_reaction(YESREACT)

        # Returns whatever came first, message or reaction emoji
        async def first_cum_first_serve():
            done, pending = await asyncio.wait(
                [self.bot.waitmsg(ctx, guild_data['DM'], obj=True), self.bot.waitrct(ctx, exapp, [YESEMOJI])], 
                timeout = 600.0,
                return_when = asyncio.FIRST_COMPLETED
            )
            return done.pop().result()

        appqns = []
        qns_added = 0

        while True: 
            # Getting the message or reaction emoji
            returned = await first_cum_first_serve()
            if hasattr(returned, "content"):
                if await self.bot.cancel(returned.content): return None
            if str(returned) == YESEMOJI or qns_added == 25: # Breaking out if it's an emoji or max qns reached
                if qns_added == 0: # Prevent breaking if no questions were added
                    await exapp.edit(embed=error('Enter at least one question to continue.'))
                    await exapp.remove_reaction(YESREACT, ctx.guild.me)
                    exapp = await user.send(embed=exemb)
                    await exapp.add_reaction(YESREACT)
                    continue
                else:
                    break

            # Add to question tracker, then adding field to embed
            qns_added += 1 
            if len(returned.content) > 250: 
                await exapp.edit(embed=error('Your question must be at or below 250 characters due to Discord\'s embed limits.'))
                await exapp.remove_reaction(YESREACT, ctx.guild.me)
                exapp = await user.send(embed=exemb)
                await exapp.add_reaction(YESREACT)            
                continue
            # Checks and handlers for over 10 and 20 questions
            if qns_added == 10 or qns_added == 20:
                await exapp.edit(embed=embed('Question Limit Warning',f'You have made {qns_added} out of the maximum of 25 questions.'))
                await exapp.remove_reaction(YESREACT, ctx.guild.me)
                exapp = await user.send(embed=exemb)
                await exapp.add_reaction(YESREACT)

            exemb.add_field(name=returned.content,value='(Example Answer Here)')
            appqns.append(returned.content)

            # Deleting message to keep things aesthetic, only if possible
            try: await returned.delete()
            except: pass

            await exapp.edit(embed=exemb)

            if qns_added == 25:
                await user.send(embed=embed('Maximum Questions Reached','You have set a total of 25 questions, which is the maximum number of questions per application.'))
                break
        data['app'] = appqns

        # -------------------------------------------

        # Get an acceptance role
        areyousure = await user.send(embed=embed("Add an Acceptance Role?","Do you want the bot to automatically give an applier a role if a reviewer accepts his or her application?"))
        for reaction in [YESREACT,NOREACT]:
            await areyousure.add_reaction(reaction)
        choice = await self.bot.waitrct(ctx, areyousure, [YESEMOJI, NOEMOJI])
        if choice == YESEMOJI:
            while True:
                await user.send(embed=embed('Select Role','What role would you like to give the accepted applier? (Enter the name of a role)'))
                role = await self.bot.waitmsg(ctx, guild_data['DM'])
                try: 
                    roleobj = await commands.RoleConverter().convert(ctx, role)
                    await ctx.guild.me.add_roles(roleobj,reason='Permissions Test')
                    await ctx.guild.me.remove_roles(roleobj,reason='Permissions Test')
                    data['acceptrole'] = str(roleobj.id)
                    break
                except:
                    errperms = error('Either the role was not found, or the bot does not have permission to add this role. Please try again.')
                    errperms.set_image(url='https://media.giphy.com/media/CjsyUwRqLYpsmnjEud/giphy.gif') 
                    await user.send(embed=errperms)
        else: await user.send(embed=embed("Action cancelled.",f'The bot will not give the accepted applier a role. You can change this later.'))

        # Getting acceptance message
        accept_examples = {'1⃣':'Your job application has been accepted!','2⃣':f'You have successfully registered to {ctx.guild.name}!','3⃣':'Your report has been accepted. The user will be punished accordingly.'}
        await user.send(embed=embed('Set an acceptance message. This will be the message that the user will receive upon being accepted.',accept_examples[apprct]))
        accept = await self.bot.waitmsg(ctx, guild_data['DM'])
        if await self.bot.cancel(accept): return None
        data['accept'] = accept

        data['open'] = True # App is open by default

        return data

    @commands.command(aliases=['config'])
    @commands.guild_only()
    async def configuration(self, ctx):
        """Configure applications, channels, bot behavior, and more."""
        data = await self.bot.data(ctx.guild.id)
        user = self.bot.getchannel(ctx, data)

        if not self.bot.has_perms(ctx, data, 2): return await ctx.send(embed=error('You do not have permission to use this command.'))
        await ctx.message.add_reaction(':yes:426190071473897502')

        if data['apps'] == {}: # If apps haven't been setup yet...

            await user.send(embed=embed("Application Configuration","It looks like this is your first time creating your application! You will be making a fully customized application that will automatically give the application sender a role upon being accepted. Type anything to get started, or type ''Cancel'' at any time to stop."))
            begin = await self.bot.waitmsg(ctx, data['DM'])
            if await self.bot.cancel(begin): return await user.send(embed=embed('Cancelled','You have successfully cancelled configuration.'))
            # Begin here or not? ^

            # Defining App Name
            await user.send(embed=embed('Application Name','What would you like to call this application? (e.g. Moderator, Member, etc.)'))
            while True:
                app_name = await self.bot.waitmsg(ctx, data['DM'])
                if app_name not in data["apps"]:
                    break
                await user.send(embed=error("This application already exists. Please enter another name."))
            if await self.bot.cancel(app_name): return await user.send(embed=embed('Cancelled','You have successfully cancelled configuration.'))

            # The actual app creation in \/ this func \/
            appdata = await self.app_setup(ctx, app_name, data)
            if appdata == None: 
                await user.send(embed=embed('Application Cancelled','You have cancelled the creation of this application.'))
                return
            self.bot.db.get(str(ctx.guild.id)).update({'apps': {app_name : appdata}}).run(self.bot.conn)
            await user.send(embed=embed('Application Created',f'Your first application has been successfully created.\nType `{ctx.prefix}config` again to configure applications or add more.\nType `{ctx.prefix}review <member>` to review a member.\nMembers can type `{ctx.prefix}apply` to apply.\nUse `{ctx.prefix}help` for additional information, or feel free to join the [support server](https://appbot.site/support).'))

        else: # If apps have already been setup...

            while True:

                configpanel = embed('Configuration Panel','From configuring applications to customizing the bot, get your job done here.')
                configpanel.add_field(name=':one: Application Settings',value='Create, delete, and edit applications and behavior here.')
                configpanel.add_field(name=':two: Channels and Permissions',value='Set the a channel for logs and archives, a role to review and/or configure applications, or blacklist or whitelist users with specific roles from applying.')
                configpanel.add_field(name=':three: Bot Settings',value='Change the bot\'s prefixes, make the bot DM messages or send to the same channel.')
                configpanel.add_field(name=':four: Exit',value='Exit the configuration panel')
                configp = await user.send(embed=configpanel)
                #self.bot.log.debug(f"Sent config menu")
                for reaction in ["1⃣","2⃣","3⃣","4⃣"]: 
                    await configp.add_reaction(reaction)
                rct = await self.bot.waitrct(ctx, configp, ["1⃣","2⃣","3⃣","4⃣"])
                #self.bot.log.debug("Added reactions to config menu")
                if rct == "1⃣": # Config Panel - App Config
                    while True:
                        desc = 'Select what you would like to do next.'
                        appconfig = embed('Configuration Panel - Application Settings', desc)
                        appconfig.add_field(name=':one: Create an Application',value='\uFEFF',inline=False)
                        appconfig.add_field(name=':two: Edit an Application',value='\uFEFF',inline=False)
                        appconfig.add_field(name=':three: Delete an Application',value='\uFEFF',inline=False)
                        appconfig.add_field(name=':four: Open/close an application',value='\uFEFF',inline=False)
                        appconfig.add_field(name=':five: Back',value='\uFEFF')
                        appconfig = await user.send(embed=appconfig)

                        for reaction in ["1⃣","2⃣","3⃣","4⃣","5⃣"]: 
                            await appconfig.add_reaction(reaction)
                        rct = await self.bot.waitrct(ctx, appconfig, ["1⃣","2⃣","3⃣","4⃣","5⃣"])

                        if rct == "1⃣": # App Config - Create App
                            await user.send(embed=embed('Application Name','What would you like the application to be called?'))
                            while True:
                                app_name = await self.bot.waitmsg(ctx, data['DM'])
                                if app_name not in data["apps"]:
                                    break
                                await user.send(embed=error("This application already exists. Please enter another name."))

                            # The actual app creation in \/ this func \/
                            appdata = await self.app_setup(ctx, app_name, data)
                            if appdata == None: 
                                await user.send(embed=embed('Application Cancelled','You have cancelled the creation of this application.'))
                                continue
                            self.bot.db.get(str(ctx.guild.id)).update({'apps': {app_name : appdata}}).run(self.bot.conn)
                            await user.send(embed=embed('Application Created',f'Your application has been successfully created.\nType `{ctx.prefix}config` again to configure applications or add more.\nType `{ctx.prefix}review <member>` to review a member, or `{ctx.prefix}review` by itself to review more.\nMembers can type `{ctx.prefix}apply` to apply.\nUse `{ctx.prefix}help` for additional information, or feel free to join the [support server](https://appbot.site/support).'))
                            await self.bot.log(ctx, data, "Application Created", f"{ctx.author.display_name} has created the application for {app_name}.")

                        elif rct == "2⃣": # App Config - Edit App
                            appname = await self.bot.get_app(ctx, data)
                            appdata = data['apps'][appname]
                            if 'requiredrole' in appdata:
                                roleobj = discord.utils.get(ctx.guild.roles, id=int(appdata['requiredrole']))
                                if roleobj != None:
                                    app_requiredrole = roleobj.name
                                else:
                                    app_requiredrole = 'Deleted'
                            else:
                                app_requiredrole = 'None Set'
                            if 'acceptrole' in appdata:
                                roleobj = discord.utils.get(ctx.guild.roles, id=int(appdata['acceptrole']))
                                if roleobj != None:
                                    app_acceptrole = roleobj.name
                                else:
                                    app_acceptrole = 'Deleted'
                            else:
                                app_acceptrole = 'None Set'
                            while True:
                                exampleapp = embed(f'Apply for {appname}: {ctx.author.name}',f"This is the application for {ctx.guild.name}.")
                                for qnum,question in zip(range(len(appdata['app'])), appdata['app']):
                                    exampleapp.add_field(name=f"{qnum + 1}. {question}",value='(Your answer)')
                                await user.send(embed=exampleapp)
                                editcfg = embed(f'Edit Application: {appname}','Edit your application here. You can change the name, add/remove/edit questions, change other assets, etc.')
                                editcfg.add_field(name=':one: Edit Application Name',value=f'**Current Name: **{appname}')
                                editcfg.add_field(name=':two: Required Role',value=f'**Current Required Role:** {app_requiredrole}')
                                editcfg.add_field(name=':three: Change the Introduction',value=f'**Current Introduction: **{appdata["intro"]}')
                                editcfg.add_field(name=':four: Configure Questions',value=f'**Current Total Questions: **{len(appdata["app"])}')
                                editcfg.add_field(name=':five: Acceptance Role',value=f'**Current Acceptance Role: **{app_acceptrole}')
                                editcfg.add_field(name=':six: Acceptance Message',value=f'**Current Acceptance Message: **{appdata["accept"]}')
                                editcfg.add_field(name=':seven: Back',value='Go Back to Application Configuration')
                                appeditmsg = await user.send(embed=editcfg)
                                for reaction in ["1⃣","2⃣","3⃣","4⃣","5⃣","6⃣","7⃣"]: 
                                    await appeditmsg.add_reaction(reaction)
                                rct = await self.bot.waitrct(ctx, appeditmsg, ["1⃣","2⃣","3⃣","4⃣","5⃣","6⃣","7⃣"])
                                await appeditmsg.delete()

                                if rct == "1⃣": # Edit App Name
                                    await user.send(embed=embed('New Application Name','What would you like your new application name to be?').set_footer(text='Type cancel to stop at any time.'))
                                    newname = await self.bot.waitmsg(ctx, data['DM'])
                                    if newname.lower() == 'cancel': 
                                        await user.send(embed=embed('Cancelled',f'Your application {appname} has not changed it\'s name.'))
                                        break
                                    data['apps'][newname] = data['apps'][appname]
                                    del data['apps'][appname]
                                    oldname = appname
                                    appname = newname
                                    for member, memberapps in data['members'].items():
                                        if appname in memberapps.keys():
                                            data['members'][member][newname] = data['members'][member][appname]
                                            del data['members'][member][appname]
                                    await self.bot.save(ctx.guild.id, data)
                                    await self.bot.log(ctx, data, "Application Edited",f"{ctx.author.display_name} has changed an application name from {oldname} to {appname}.")

                                elif rct == "2⃣": # Required Role
                                    await user.send(embed=embed('New Required Role','What would you like your new required role to be to apply?'))
                                    while True:
                                        role = await self.bot.waitmsg(ctx, data['DM'])
                                        try: 
                                            roleobj = await commands.RoleConverter().convert(ctx, role)
                                            self.bot.db.get(str(ctx.guild.id)).update({'apps':{appname:{'requiredrole':str(roleobj.id)}}}).run(self.bot.conn)
                                            break
                                        except:
                                            await user.send(embed=error('This role was not found. Please try again.'))
                                    await self.bot.log(ctx, data, "Application Edited",f"{ctx.author.display_name} has changed the required role for the application {appname} to {role}.")

                                elif rct == "3⃣": # Change Intro
                                    while True:
                                        await user.send(embed=embed('New Introduction','What would you like your new introduction to be?'))
                                        newintro = await self.bot.waitmsg(ctx, data['DM'])
                                        self.bot.db.get(str(ctx.guild.id)).update({'apps':{appname:{'intro':newintro}}}).run(self.bot.conn)
                                        await self.bot.log(ctx, data, "Application Edited",f"{ctx.author.display_name} has changed the introduction to the application {appname}.")
                                        if len(newintro) > 999: await user.send(embed=error("Your introduction must have less than 1000 characters. Please try again."))
                                        else: break
                                    
                                elif rct == "4⃣": # Config Questions
                                    totalqns = len(appdata["app"])
                                    qcnfg = embed('Questions Configuration','Add, Remove, Edit Questions')
                                    qcnfg.add_field(name=':one: Add Questions',value='**Maximum Questions:** 25')
                                    qcnfg.add_field(name=':two: Remove Questions',value=f'**Current Total Questions: **{totalqns}')
                                    qcnfg.add_field(name=':three: Edit Questions',value='Change the questions you have set right now')
                                    qcnfg.add_field(name=':four: Back',value='Go back to Application Configuration')
                                    while True:
                                        appqnscfg = await user.send(embed=qcnfg)
                                        for reaction in ["1⃣","2⃣","3⃣","4⃣"]: 
                                            await appqnscfg.add_reaction(reaction)
                                        rct = await self.bot.waitrct(ctx, appqnscfg, ["1⃣","2⃣","3⃣","4⃣"])

                                        if rct == "1⃣": # Add questions

                                            if len(appdata['app']) == 25: 
                                                await user.send(embed=error('You are not allowed to have over 25 questions.')) 
                                                continue

                                            await user.send(embed=embed('Add Questions','After which question would you like to add a question? Enter 0 to add a question before the first one. (For example, "3" allows you to add a question in between the current question 2 and 3.'))
                                            qnum = await self.bot.getnum(ctx, data, 0, len(appdata["app"]))

                                            await user.send(embed=embed(f'Add Question {qnum+1}',f'What do you want question {qnum+1} to be?').set_footer(text='Type cancel to stop here.'))
                                            addedqn = await self.bot.waitmsg(ctx, data['DM'])
                                            if addedqn.lower() == 'cancel': 
                                                await user.send(embed=embed('Cancelled',f'Your application {appname} has not changed it\'s name.'))
                                                break

                                            appdata['app'].insert(qnum, addedqn)
                                            await user.send(embed=embed('Question Inserted',f'Your question has been inserted successfully. You now have {len(appdata["app"])} questions.'))

                                            for member, memberapps in data['members'].items():
                                                if appname in memberapps.keys():
                                                    data['members'][member][appname].insert(qnum, '*This application was submitted prior to this question being added, meaning an answer was not provided.*')

                                            await self.bot.save(ctx.guild.id, data)
                                            await self.bot.log(ctx, data, "Application Edited",f"{ctx.author.display_name} has added a question after question {qnum} to the application {appname}.")
                                            totalqns += 1

                                        elif rct == "2⃣": # Remove questions

                                            if len(appdata['app']) == 1: 
                                                await user.send(embed=error('You are not allowed to have less than 1 question.')) 
                                                continue

                                            await user.send(embed=embed('Remove Questions',f'Which question would you like to remove? (Enter a number within 1 and {len(appdata["app"])})'))
                                            remove = await self.bot.getnum(ctx, data, 1, len(appdata["app"]))

                                            # Deleting Question
                                            del appdata["app"][remove - 1]

                                            # Member App Deleting Answers
                                            for member, memberapps in data['members'].items():
                                                if appname in memberapps.keys():
                                                    del data['members'][member][appname][remove - 1]

                                            await self.bot.save(ctx.guild.id, data)
                                            await self.bot.log(ctx, data, "Application Edited",f"{ctx.author.display_name} has removed question {remove} from the application {appname}.")
                                            totalqns -= 1

                                        elif rct == "3⃣": # Edit questions
                                        
                                            await user.send(embed=embed('Edit Questions','Which question would you like to edit? (Enter a number.)'))
                                            qnum = await self.bot.getnum(ctx, data, 1, len(appdata["app"]))

                                            await user.send(embed=embed(f'What do you want question {qnum} to be?',f'**Before: **{appdata["app"][qnum - 1]}').set_footer(text='Type cancel to stop at any time.'))
                                            editedqn = await self.bot.waitmsg(ctx, data['DM'])
                                            if editedqn.lower() == 'cancel': 
                                                await user.send(embed=embed('Cancelled',f'Your application {appname} has not changed it\'s name.'))
                                                break
                                            appdata['app'][qnum - 1] = editedqn

                                            # Member App Deleting Answers
                                            for member, memberapps in data['members'].items():
                                                if appname in memberapps.keys():
                                                    answer = data['members'][member][appname][qnum - 1]
                                                    warning = '\n**Warning:** *This application was submitted prior to having this question edited. The answer may not be accurate.*'
                                                    if not answer.endswith(warning):
                                                        answer += warning
                                                    del data['members'][member][appname][qnum - 1]
                                                    data['members'][member][appname].insert(qnum - 1, answer)

                                            await user.send(embed=embed('Question Edited',f'Your question has been edited successfully.'))
                                            await self.bot.save(ctx.guild.id, data)
                                            await self.bot.log(ctx, data, "Application Edited",f"{ctx.author.display_name} has edited question {qnum} for the application {appname}.")

                                        elif rct == "4⃣": # Break out
                                            await user.send(embed=embed('Exited Question Editing','Returning to application editing menu...'))
                                            break

                                    if rct != "4⃣":
                                        exampleapp = embed(f'Apply for {appname}: {ctx.author.name}',f"This is the application for {ctx.guild.name}.")
                                        for question in appdata['app']:
                                            exampleapp.add_field(name=question,value='(Your answer)')
                                        await user.send(embed=exampleapp)

                                elif rct == "5⃣": # Acceptance Role
                                    await user.send(embed=embed('New Acceptance Role','What would you like your new acceptance role to be?'))
                                    while True:
                                        role = await self.bot.waitmsg(ctx, data['DM'])
                                        try: 
                                            roleobj = await commands.RoleConverter().convert(ctx, role)
                                            await ctx.guild.me.add_roles(roleobj,reason='Permissions Test')
                                            await ctx.guild.me.remove_roles(roleobj,reason='Permissions Test')
                                            self.bot.db.get(str(ctx.guild.id)).update({'apps':{appname:{'acceptrole':str(roleobj.id)}}}).run(self.bot.conn)
                                            break
                                        except:
                                            errperms = error('Either the role was not found, or the bot does not have permission to add this role. Please try again.')
                                            errperms.set_image(url='https://media.giphy.com/media/CjsyUwRqLYpsmnjEud/giphy.gif') 
                                            await user.send(embed=errperms)
                                    await self.bot.log(ctx, data, "Application Edited",f"{ctx.author.display_name} has changed the acceptance role to the application {appname} to {role}.")

                                elif rct == "6⃣":  # Acceptance Message
                                    await user.send(embed=embed('New Acceptance Message','What would you like your new acceptance message to be?'))
                                    newaccept = await self.bot.waitmsg(ctx, data['DM'])
                                    self.bot.db.get(str(ctx.guild.id)).update({'apps':{appname:{'accept':newaccept}}}).run(self.bot.conn)
                                    await self.bot.log(ctx, data, "Application Edited",f"{ctx.author.display_name} has changed the acceptance message to the application {appname}.")

                                elif rct == "7⃣": # Exit App Config - Back to Main Menu
                                    await user.send(embed=embed('Exited Application Editing','Returning to application configuration menu...'))
                                    break

                        elif rct == "3⃣": # App Config - Delete App
                            appname = await self.bot.get_app(ctx, data)
                            sure = await self.bot.sure(ctx, data, f'Are you sure you want to delete the {appname} application?')
                            if sure:
                                self.bot.db.get(str(ctx.guild.id)).replace(r.row.without({"apps":{appname: True}})).run(self.bot.conn)
                                for memberid, memberapps in data['members'].items():
                                    if appname in memberapps:
                                        self.bot.db.get(str(ctx.guild.id)).replace(r.row.without({'members':{memberid:{appname:True}}})).run(self.bot.conn)
                                desc = 'You have successfully deleted your application.'
                                if len(data['apps']) == 0: desc += f' Type `{ctx.prefix}config` again to create your new application.'
                                await user.send(embed=embed('App Deleted',desc))
                                await self.bot.log(ctx, data, "Application Deleted",f"{ctx.author.display_name} has deleted the application {appname}.")
                                if len(data['apps']) == 0: return
                            else: 
                                await user.send(embed=embed('Cancelled',f'The {appname} application was not deleted.'))

                        elif rct == "4⃣": # App Config - Open/close App 
                            appname = await self.bot.get_app(ctx, data)
                            appdata = data['apps'][appname]
                            if appdata['open']:
                                self.bot.db.get(str(ctx.guild.id)).update({'apps':{appname:{'open':False}}}).run(self.bot.conn)
                                status = 'closed'
                            else:
                                self.bot.db.get(str(ctx.guild.id)).update({'apps':{appname:{'open':True}}}).run(self.bot.conn)
                                status = 'opened'
                            await user.send(embed=embed('Application ' + status.capitalize(),f'The application {appname} has successfully been {status}.'))
                            await self.bot.log(ctx, data, f"Application {status.capitalize()}",f"{ctx.author.display_name} has {status} the application {appname}.")

                        elif rct == "5⃣": # Exit App Config - Back to Main Menu
                            await user.send(embed=embed('Exited App Configuration','Returning to main configuration menu...'))
                            break

                elif rct == "2⃣":# Channels and Perms
                    while True:
                        channelpanel = embed('Channels and Permissions','Set roles, channels, permissions, etc. for the bot here.')
                        channelpanel.add_field(name=':one: Blacklist or whitelist roles',value='Set any amount of roles to blacklist/whitelist.')
                        channelpanel.add_field(name=':two: Set a Log Channel',value='Set a channel which will log all application-related actions')
                        channelpanel.add_field(name=':three: Set an Archives Channel',value='Set a channel to log applications after being accepted/denied')
                        channelpanel.add_field(name=':four: Add/remove an App Editing Role',value='Add or remove a role so that anyone with it can configure applications')
                        channelpanel.add_field(name=':five: Add/remove an App Reviewing Role',value='Add or remove a role so that anyone with it can review applications')
                        channelpanel.add_field(name=':six: Back',value='Exit the channels panel and return to the main configuration panel.')
                        channelp = await user.send(embed=channelpanel)

                        for reaction in ["1⃣","2⃣","3⃣","4⃣","5⃣","6⃣"]: 
                            await channelp.add_reaction(reaction)
                        rct = await self.bot.waitrct(ctx, channelp, ["1⃣","2⃣","3⃣","4⃣","5⃣","6⃣"])
                        if rct == "1⃣": # Blacklisting/whitelisting

                            desc = ''
                            remove = []
                            for role_id in data['blacklist']:
                                roleobj = discord.utils.get(ctx.guild.roles, id = int(role_id))
                                if roleobj is None: # Creates list of nonexistent roles
                                    remove.append(str(role_id))
                                    continue
                                desc += f'{roleobj.name}\n'

                            if desc == '': desc = '(None set)' # If no blacklisted roles have been set yet

                            for role_id in data['blacklist']: # Removes nonexistent roles from data
                                if str(role_id) in remove:
                                    data['blacklist'].remove(str(role_id))

                            await user.send(embed=embed('Enter the name of the role you would like to blacklist/whitelist. The current blacklisted ones are shown below:',desc))
                            while True:

                                rolename = await self.bot.waitmsg(ctx, data['DM'])
                                roleobj = discord.utils.get(ctx.guild.roles, name = rolename)

                                if roleobj is None:
                                    await user.send(embed=embed('Role not Found',f'The role "{rolename}" was not found. Please try again.'))
                                    continue

                                if str(roleobj.id) in data['blacklist']:
                                    data['blacklist'].remove(str(roleobj.id)) # Whitelisting if blacklisted previously
                                    wh_bl = 'whitelisted'

                                else:
                                    data['blacklist'].append(str(roleobj.id)) # Blacklisting if not whitelisted
                                    wh_bl = 'blacklisted'

                                await self.bot.save(ctx.guild.id, data)
                                break
                            await self.bot.log(ctx, data, f"Role {wh_bl.capitalize()}",f"{ctx.author.display_name} has {wh_bl.capitalize()} the role {rolename}.")
                            await user.send(embed=embed(f'Role {wh_bl.capitalize()}',f'The role {roleobj.name} has been {wh_bl}.'))

                        elif rct == "2⃣": # Log Channel
                            current = data['logs']
                            if current is None: 
                                channelname = '(None set)'
                            else:
                                channelnameobj = self.bot.get_channel(current)
                                if channelnameobj == None:
                                    channelname = '(Deleted)'
                                else:
                                    channelname = channelnameobj.name
                            await user.send(embed=embed('What channel do you want the bot to log all bot actions in?',f'Enter the name of the channel (e.g. `logs`).\nCurrent log channel: {channelname}'))
                            while True:
                                channelname = await self.bot.waitmsg(ctx, data['DM'])
                                channelobj = discord.utils.get(ctx.guild.channels, name = channelname)
                                if channelobj is None:
                                    await user.send(embed=error('This channel was not found. Please try again.'))
                                    continue
                                self.bot.db.get(str(ctx.guild.id)).update({"logs":str(channelobj.id)}).run(self.bot.conn)
                                break
                            await self.bot.log(ctx, data, f"Log Channel Set",f"{ctx.author.display_name} has set the log channel to `#{channelname}`.")

                        elif rct == "3⃣": # Archives Channel
                            current = data['archives']
                            if current is None: 
                                channelname = '(None set)'
                            else:
                                channelnameobj = self.bot.get_channel(current)
                                if channelnameobj is None:
                                    channelname = '(Deleted)'
                                else:
                                    channelname = channelnameobj.name
                            await user.send(embed=embed('What channel do you want the bot to log reviewed applications in?',f'Enter the name of the channel (e.g. `archived-apps`).\nCurrent log channel: {channelname}'))
                            while True:
                                channelname = await self.bot.waitmsg(ctx, data['DM'])
                                channelobj = discord.utils.get(ctx.guild.channels, name = channelname)
                                if channelobj is None:
                                    await user.send(embed=error('This channel was not found. Please try again.'))
                                    continue
                                self.bot.db.get(str(ctx.guild.id)).update({"archives":str(channelobj.id)}).run(self.bot.conn)
                                break
                            await self.bot.log(ctx, data, f"Archives Channel Set",f"{ctx.author.display_name} has set the archives channel to `#{channelname}`.")

                        elif rct == "4⃣": # App Edit Role
                            desc = ''
                            remove = []
                            for role_id in data['appeditroles']:
                                roleobj = discord.utils.get(ctx.guild.roles, id = int(role_id))
                                if roleobj is None: # Creates list of nonexistent roles
                                    remove.append(str(role_id))
                                    continue
                                desc += f'{roleobj.name}\n'

                            if desc == '': desc = '(None set)' # If no appedit roles have been set yet

                            for role_id in data['appeditroles']: # Removes nonexistent roles from data
                                if role_id in remove:
                                    data['appeditroles'].remove(role_id)
                            await user.send(embed=embed('Enter the name of the role you would like to add/remove from the list of roles set to edit applications. The current ones are shown below:',desc))

                            while True:

                                rolename = await self.bot.waitmsg(ctx, data['DM'])
                                roleobj = discord.utils.get(ctx.guild.roles, name = rolename)

                                if roleobj is None:
                                    await user.send(embed=embed('Role not Found',f'The role "{rolename}" was not found. Please try again.'))
                                    continue

                                if str(roleobj.id) in data['appeditroles']:
                                    data['appeditroles'].remove(str(roleobj.id)) # removing if added previously
                                    rm_ad = 'removed'

                                else:
                                    data['appeditroles'].append(str(roleobj.id)) # adding if not already
                                    rm_ad = 'added'

                                await self.bot.save(ctx.guild.id, data)
                                break

                            await self.bot.log(ctx, data, f"Application Editing Role {rm_ad.capitalize()}",f"{ctx.author.display_name} has {rm_ad} the role {roleobj.name} to the list of application editing roles.")
                            await user.send(embed=embed(f'Role {rm_ad.capitalize()}',f'The role {roleobj.name} has been {rm_ad}.'))

                        elif rct == "5⃣": # App Review Role
                            desc = ''
                            remove = []
                            for role_id in data['appreviewroles']:
                                roleobj = discord.utils.get(ctx.guild.roles, id = int(role_id))
                                if roleobj is None: # Creates list of nonexistent roles
                                    remove.append(str(role_id))
                                    continue
                                desc += f'{roleobj.name}\n'

                            if desc == '': desc = '(None set)' # If no appedit roles have been set yet

                            for role_id in data['appreviewroles']: # Removes nonexistent roles from data
                                if role_id in remove:
                                    data['appreviewroles'].remove(str(role_id))

                            await user.send(embed=embed('Enter the name of the role you would like to add/remove from the list of roles set to edit applications. The current ones are shown below:',desc))
                            while True:

                                rolename = await self.bot.waitmsg(ctx, data['DM'])
                                roleobj = discord.utils.get(ctx.guild.roles, name = rolename)

                                if roleobj is None:
                                    await user.send(embed=embed('Role not Found',f'The role "{rolename}" was not found. Please try again.'))
                                    continue

                                if str(roleobj.id) in data['appreviewroles']:
                                    data['appreviewroles'].remove(str(roleobj.id)) # removing if added previously
                                    rm_ad = 'removed'

                                else:
                                    data['appreviewroles'].append(str(roleobj.id)) # adding if not already
                                    rm_ad = 'added'

                                await self.bot.save(ctx.guild.id, data)
                                break

                            await self.bot.log(ctx, data, f"Application Reviewing Role {rm_ad.capitalize()}",f"{ctx.author.display_name} has {rm_ad} the role {roleobj.name} to the list of application reviewing roles.")
                            await user.send(embed=embed(f'Role {rm_ad.capitalize()}',f'The role {roleobj.name} has been {rm_ad}.'))

                        elif rct == "6⃣": # Back to main config menu
                            await user.send(embed=embed('Exited Channel/Permissions Configuration','Returning to main configuration menu...'))
                            break

                elif rct == "3⃣": # Bot Settings
                    while True:
                        botsettings = embed('Bot Settings','Change basic bot functionality here.')
                        botsettings.add_field(name=':one: Add/remove Custom Prefixes',value='Add or remove a prefix to the bot.')
                        botsettings.add_field(name=':two: Toggle Channel or DM',value='Choose whether you want the bot to DM you or send messages in the same channel. This applies to configuration and reviewing.')
                        botsettings.add_field(name=':three: Reset the Bot',value="Reset the bot to factory settings. This will also wipe possible existent bugs.")
                        botsettings.add_field(name=':four: Back',value='Back to main configuration menu')
                        botcfg = await user.send(embed=botsettings)

                        for reaction in ["1⃣","2⃣","3⃣","4⃣"]: 
                            await botcfg.add_reaction(reaction)
                        rct = await self.bot.waitrct(ctx, botcfg, ["1⃣","2⃣","3⃣","4⃣"])
                        if rct == "1⃣": # Custom Prefixes
                            desc = '@AppBot'
                            remove = []
                            if str(ctx.guild.id) not in self.bot.prefixes:
                                self.bot.prefixes[str(ctx.guild.id)] = ['/']
                            for prefix in self.bot.prefixes[str(ctx.guild.id)]:
                                desc += f', {prefix}'

                            await user.send(embed=embed('Enter prefixes to add. Enter an existing prefix to remove it. The current ones are shown below:',desc))
                            while True:
                                prefix = await self.bot.waitmsg(ctx, data['DM'])
                                if prefix in self.bot.prefixes[str(ctx.guild.id)]:
                                    self.bot.prefixes[str(ctx.guild.id)].remove(prefix) # removing if added previously
                                    rm_ad = 'removed'
                                else:
                                    self.bot.prefixes[str(ctx.guild.id)].append(prefix) # adding if not already
                                    rm_ad = 'added'

                                with open('prefixes.json','w') as file: json.dump(self.bot.prefixes, file, indent=4)
                                
                                break

                            await self.bot.log(ctx, data, f"Prefix {rm_ad.capitalize()}",f'{ctx.author.display_name} has {rm_ad} the prefix {prefix}.')
                            await user.send(embed=embed(f'Prefix {rm_ad.capitalize()}',f'The prefix {prefix} has been {rm_ad}.'))

                        elif rct == "2⃣":
                            if data['DM']:
                                self.bot.db.get(str(ctx.guild.id)).update({"DM":False}).run(self.bot.conn)
                                await user.send(embed=embed(f'The bot will now send configuration messages in the same channel.','Select this menu option again to change configuration messages back to your DMs.'))
                            else:
                                self.bot.db.get(str(ctx.guild.id)).update({"DM":True}).run(self.bot.conn)
                                await user.send(embed=embed(f'The bot will now send configuration messages in the your DM.','Select this menu option again to change configuration messages to the same channel that the command was invoked in.'))
                            await self.bot.save(ctx.guild.id, data)
                            await self.bot.log(ctx, data, f"Bot Messaging Edited",f'{ctx.author.display_name} has changed the bot\'s way of messaging for reviewing and configuring.')

                        elif rct == "3⃣": # Reset Bot
                            num_of_apps = len(data['apps'])
                            sure = await self.bot.sure(ctx, data, f'Are you sure you want to reset the bot and delete all your {num_of_apps} applications?')
                            if sure:
                                await self.bot.log(ctx, data, f"Bot Reset",f'{ctx.author.display_name} has reset AppBot for this server. (Warning: This log channel will also be reset, meaning you will have to reset a log channel.)')
                                self.bot.db.get(str(ctx.guild.id)).replace({"apps":{},"members":{},'DM':True, 'blacklist':[], 'logs': None, 'archives': None, 'appeditroles': [], 'appreviewroles': []}).run(self.bot.conn)
                                return await user.send(embed=embed('Bot Reset','Your bot has been reset. Type `/config` in your server to set it up again.'))
                            else:
                                await user.send(embed=embed('Action Cancelled','Your applications have not been deleted.'))

                        elif rct == "4⃣":
                            await user.send(embed=embed('Exited Bot Configuration','Returning to main configuration menu...'))
                            break
                            
                elif rct == "4⃣": # Exit
                    await user.send(embed=embed('Configuration Exited','You have successfully exited the configuration.'))
                    return

def setup(bot):
    bot.add_cog(Administrator(bot))