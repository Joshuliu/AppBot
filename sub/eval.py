import io
import textwrap
import traceback
from contextlib import redirect_stdout

import discord
from discord.ext import commands


class Eval:
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    def cleanup_code(self, content):
        if content.startswith('```') and content.endswith('```'):
            content = content[3:-3]
            if content.startswith('py'):
                content = content[3:]
        return content

    @commands.is_owner()
    @commands.command(pass_context=True, hidden=True, name='eval')
    async def _eval(self, ctx, *, body: str):
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.message.channel,
            'author': ctx.message.author,
            'guild': ctx.message.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            send = f'```py\n{value}{traceback.format_exc()}\n```'
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction(':yes:426190071473897502')
            except:
                pass

            if ret is None:
                if value:
                    send = f'```py\n{value}\n```'
            else:
                self._last_result = ret
                send = f'```py\n{value}{ret}\n```'
        try:
            await ctx.send(embed=discord.Embed(title='AppBot Console',description=send,color=0x29b6f6))
        except: pass
def setup(bot):
    bot.add_cog(Eval(bot))