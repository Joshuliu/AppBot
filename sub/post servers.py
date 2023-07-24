import json
import logging

log = logging.getLogger()

TERMINAL = 'https://ls.terminal.ink/api/v1/'
BOTS_API = 'https://bots.discord.pw/api'

lists = {
    "bots": "https://discordbots.org/api",
    "listcord": "https://listcord.com/api",
    "dbotpw": 'https://bots.discord.pw/api',
    "space": 'https://botlist.space/api',
    "bfd": 'https://botsfordiscord.com/api/v1/'
}

authkey = {
    "bots":
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjQyNDgxNzQ1MTI5MzczNjk2MSIsImJvdCI6dHJ1ZSwiaWF0IjoxNTIxMzg4ODcxfQ.Szd_pIk-yegIz_HUoAT5T5JU5dXfcU5nlmIPXWL7-7E",
    "space":
        "461e931716abd89ced7783b5e366ee160d71e7a8c21212e8437814cbbf9027de3369c0b0ddec61215d9af50de120c959e427ec1fb75ba09fe7e8348aaa2549b5",
    "botpw": 
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySUQiOiIzOTQ0MDIyNTI0OTgwMTAxMTMiLCJyYW5kIjo1ODYsImlhdCI6MTUyNDg5NTQ0MX0.kI5m0VJ0pj2igZpRejZswvZlO_oYCZb2FB65jnLBrLA",
    "bfd":
        "574cce3c29d709de0ecb79d6ef8747caab3fce972d6da962fb94100bbf69f587e4f53d35a6450b65bfdcbf6da8c148f591cfd726432f4411e9ab0321b4f30890"
}


class lsapi:
    """Cog for updating bots.discord.pw bot information."""

    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session

    def __unload(self):
        # pray it closes
        self.bot.loop.create_task(self.session.close())

    async def terminal(self):
        if self.bot.is_ready():
            payload = json.dumps({
                'server_count': len(self.bot.guilds),
                'shard_count': self.bot.shard_count
            })

            headers = {
                'authorization': self.bot.ls_key,
                'content-type': 'application/json'
            }

            url = '{0}/bots/{1.user.id}'.format(TERMINAL, self.bot)
            async with self.session.post(url, data=payload, headers=headers) as resp:
                print('ls statistics returned {0.status} for {1}'.format(resp, payload))

    async def dbots(self):
        payload = json.dumps({
            'server_count': len(self.bot.guilds)
        })

        headers = {
            'authorization': authkey['bots'],
            'content-type': 'application/json'
        }

        url = '{0}/bots/{1.user.id}/stats'.format(lists['bots'], self.bot)
        async with self.session.post(url, data=payload, headers=headers) as resp:
            print('DBots statistics returned {0.status} for {1}'.format(resp, payload))

    async def listcord(self):
        payload = {
            'guilds': str(len(self.bot.guilds))
        }

        headers = {
            'token': authkey['listcord'],
            'content-type': 'application/json'
        }

        url = '{0}/bot/{1.user.id}/guilds'.format(lists['listcord'], self.bot)
        async with self.session.post(url, json=payload, headers=headers) as resp:
            print('Listcord statistics returned {0.status} for {1}'.format(resp, payload))

    async def bfd(self):
        payload = json.dumps({
            'server_count': len(self.bot.guilds)
        })

        headers = {
            'Authorization': authkey['bfd'],
            'content-type': 'application/json'
        }

        url = '{0}/bots/{1.user.id}'.format(lists['bfd'], self.bot)
        async with self.session.post(url, data=payload, headers=headers) as resp:
            print('Bots For Discord statistics returned {0.status} for {1}'.format(resp, payload))

    async def botspace(self):
        payload = json.dumps({
            'server_count': len(self.bot.guilds)
        })

        headers = {
            'authorization': authkey['space'],
            'content-type': 'application/json'
        }

        url = '{0}/bots/{1.user.id}/'.format(lists['space'], self.bot)
        async with self.session.post(url, data=payload, headers=headers) as resp:
            print('botlist.space statistics returned {0.status} for {1}'.format(resp, payload))

    async def dbotpw(self):
        payload = json.dumps({
            'server_count': len(self.bot.guilds)
        })

        headers = {
            'authorization': authkey['botpw'],
            'content-type': 'application/json'
        }

        url = '{0}/bots/{1.user.id}/stats'.format(lists['dbotpw'], self.bot)
        async with self.session.post(url, data=payload, headers=headers) as resp:
            print('Dbotspw statistics returned {0.status} for {1}'.format(resp, payload))

    async def on_guild_join(self, guild):
        # await self.terminal()
        await self.botspace()
        await self.dbots()
        # await self.listcord()
        await self.dbotpw()
        await self.bfd()

    async def on_guild_remove(self, guild):
        # await self.terminal()
        await self.botspace()
        await self.dbots()
        # await self.listcord()
        await self.dbotpw()
        await self.bfd()

    async def on_ready(self):
        await self.botspace()
        await self.dbots()
        # await self.listcord()
        await self.dbotpw()
        await self.bfd()


def setup(bot):
    bot.add_cog(lsapi(bot))
