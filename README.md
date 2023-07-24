# AppBot Documentation
This is a list of commands and what they do. Make sure to join [the support server](https://bit.ly/appbot-help) if you ever need any help.

## Things to Note
The commands in the documentation don't have a prefix shown because you can customize the prefix(es). The default prefixes are `/` and mentioning the bot `@AppBot`
## Administrator Commands
The following commands are for users with either the Administrator permission, or for people who have the application reviewing/editing role (if set).

|  Command | Description  |
| -------------------- | ------------ |
| `configuration`(alias `config`)  | If no applications have been created, this command will create your first one. Otherwise, it's used to create another application, edit the questions of an application, or to reset the bot. |
| `application`  (alias `app`) |  The master command for application configuration. Subcommands are shown below (using the alias).  |
| `app edit <app>`  |  Edit an application's contents, including introduction, questions, acceptance message, and autorole. |
| `app create <numofqns> <app>`  |  Create a new application with the given name and number of questions (e.g. `/app create 3 moderator` for a moderator application with three questions) |
| `app delete <app>`  | Deletes an application |
| `app close <app>`  | Closes an application to prevent applying temporarily |
| `app open <app>`  | Opens a closed application |
| `app list`  | Views a list of applications (aka positions for appliers to apply for). Members also have access to this command.  |
| `review <member> `(alias `view`)  | Review a member's application - if they applied for more than one position, you can pick which application to review. Reviewers can choose to accept, ignore, or deny applications.  |
| `applications` (alias `apps`)  |  A list of unreviewed applications in the server. Use the `review` command to review applications. |
| `setrole <role>`  | Sets a role that gives anyone with the role permission to edit/review applications |
| `setlog <channel>`  | Sets a log for all application-related actions to be sent (including applications accepted, denied, created, deleted, etc.) |
| `prefix `  |  Prefix configuration master command. Subcommand functions are shown below. |
| `prefix set <prefix>`  | Sets a single custom prefix (excluding bot mention) for use in all commands  |
| `prefix add <prefix>`  | Adds a prefix to the list of usable prefixes  |
| `prefix remove <prefix> `  | Removes a prefix from the prefix list  |
| `prefix list` | Views the list of prefixes that are usable in the server. Members also have permission to view this command. |
| `settheme <hex>` | Sets a color for all the embeds in the messages sent by the bot. The hex provided must be a valid 6 digit hex key. (e.g. `/settheme 29B6F6`) |
| `reset` | Resets the bot as if you just added it. This command can done in `config`. |

## Member Commands
All users without either the Administrator permission, or without the application-reviewing role (if set) are considered members.

| Commands | Description |
|----|--|
| `apply` | Apply for a position. If there is more than one position, the bot will prompt the user for what position to apply for. |
| `format` | View the format (questions) of an application. If there is more than one position, the bot will prompt the user for what application format to view. |
| `application list` (alias `app list`) | Sends a list of positions to apply for |
| `prefix list` | Sends a list of prefixes that are usable in the server |

## Extra Commands
These commands are not shown in the regular help command provided the bot.

| Commands  | Description |
| ------------ | ------------ |
| `about` (aliases `info`, `information`)  | Gives some information about the bot  |
| `invite` | Retrieve an invite to send to others |
| `ping`  | Retrieve the bot's response time in milliseconds |
