import discord
from discord.ext import commands
from utils import EMOJI_LOADER, get_skill, call_ai, send_smart

class AICog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def code(self, ctx, language: str, *, prompt: str):
        """Generates code taking the FIRST word as language and the REST as prompt."""
        sk = get_skill(language)
        sys_p = f"You are Coder, an expert {language} developer."
        if sk:
            sys_p += f"\nFollow rules strictly:\n{sk}"

        msg = await ctx.send(f"{EMOJI_LOADER} Generating `{language}` code...")
        res = await call_ai(sys_p, prompt)

        try:
            await msg.delete()
        except Exception:
            pass

        await send_smart(ctx, res)

    @commands.command()
    async def plan(self, ctx, *, prompt: str):
        """Generates software architecture and implementation plan."""
        msg = await ctx.send(f"{EMOJI_LOADER} Planning system architecture...")
        sys_p = "You are an expert system architect. Provide a structured step-by-step roadmap and file outline."
        res = await call_ai(sys_p, prompt)

        try:
            await msg.delete()
        except Exception:
            pass

        await send_smart(ctx, res)

    @commands.command()
    async def ask(self, ctx, *, question: str):
        """Answers technical programming questions directly."""
        msg = await ctx.send(f"{EMOJI_LOADER} Thinking...")
        sys_p = "You are Coder, an expert technical consultant. Answer clearly and concisely."
        res = await call_ai(sys_p, question)

        try:
            await msg.delete()
        except Exception:
            pass

        await send_smart(ctx, res)

    @commands.command()
    async def debug(self, ctx, language: str, *, raw_code: str):
        """Debugs broken code snippets."""
        msg = await ctx.send(f"{EMOJI_LOADER} Analyzing code for bugs...")
        sys_p = f"Find errors and provide fixed {language} code."
        res = await call_ai(sys_p, raw_code)

        try:
            await msg.delete()
        except Exception:
            pass

        await send_smart(ctx, res)

async def setup(bot):
    await bot.add_cog(AICog(bot))
