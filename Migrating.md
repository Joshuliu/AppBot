# AppBot -> AppBot 2.0
This file basically shows how to move from AppBot to AppBot 2.0. A lot of changes have been made, and we want to make sure that you have the best experience moving over.

## What's going on?
AppBot is receiving a huge update. Features include:

* Much faster way to save data
* Combining commands to simplify bot usage
* Usage of AppBot's website within the bot
* More Application customization and options
* ...and a lot more!

## Early Testing
As of 07/16/2018, the pre-release was out. You can [add the bot](https://discordapp.com/oauth2/authorize?client_id=432478092456624138&permissions=8&scope=bot) if it's available. AppBot 2.0 may have already been implemented by the time you see this.

**Note:** The true owner of the server with the Dev. bot must be in the support server, and AppBot must be in the same server.

## Migrating Documentation

### Configuration
The original bot had many commands - `/setarchives`, `/prefix`, `/app`, etc. AppBot 2.0 combines all of the administrator commands into one huge command, `/config` (alias `/configuration`).

#### Initial Command Invoke
When you first run the command, you will get this menu. 
![Configuration Menu](https://i.imgur.com/42jyCm5.png)
###### Note: I do not use Light Theme - This was just for the tutorial. 

The original `/config` only did the first option - configuring applications. AppBot 2.0 contains all the features that anyone would need, all within `/config`.

### Applications

#### A Cleaner Look
Setting the questions in the configuration menu is easier than ever.
![Adding Questions](https://i.imgur.com/CcL9lcL.png)
##### How it works
When inputting questions, enter your questions in separate messages one by one until you have finished. Then react to the message with :yes:.
Applying has also been changed to have a similar behavior. Appliers input answers as questions show up until all questions have been answered.

---

#### Introducing Application Types!
Wether you're using applications for staff, registration, or report applications, 
![Application Types](https://i.imgur.com/9y2jqjO.png)

#### Editing application questions has never been better.
With AppBot 2.0 comes the popularly requested feature, adding and removing questions.
![Question Configuration](https://i.imgur.com/Ks4Z9sC.png)

#### Editing everything else will still be as good as before.
Edit the app name, introduction, acceptance role, etc.

---

### Reviewing
We have added a whole section of reviewing to make the experience a lot better. The original way to review, `/review @member`, is still existent. One small change has been made. Typing `/review` by itself will bring up a menu to review members in different ways.
![Review](https://i.imgur.com/BcVIN3U.png)
With `/review`, you can now review applications a lot faster than you could before.

---

### Applying
Applying received a few minor changes.
With the update of application types, there are now three main commands:
* `/apply` 
* `/register`
* `/report`

Applications will show up based on the type requested by the command invoked.

Answering questions will be similar to inputting questions. A single message is sent with the question, and an answer and new question is edited in with every message. After all questions have been answered, the user would submit the application like usual.

### Other Minor Changes
* `/app list` has been changed to `/positions`
* This list is short but more may be added over time.

---

And as usual, make sure to upvote the bot on [Discord Bot List](https://discordbots.org/bot/appbot/vote) and [Listcord](https://listcord.com/bot/424817451293736961) if you like it. Also if you have a bit of cash, a [donation](https://patreon.com/AppBot) would be appreciated. Thank you!
