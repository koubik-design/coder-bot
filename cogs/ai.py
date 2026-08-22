import discord
from discord.ext import commands
from utils import EMOJI_LOADER, get_skill, call_ai, send_smart

class AICog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_thread_context(self, message_or_ctx):
        """Reads the previous 20 messages and authors if inside a thread."""
        channel = message_or_ctx.channel
        context_history = []

        if isinstance(channel, discord.Thread):
            async for msg in channel.history(limit=21):
                if msg.id != message_or_ctx.message.id:
                    context_history.append({
                        "author": str(msg.author),
                        "content": msg.content
                    })
            context_history.reverse()

        return context_history

    async def format_prompt_with_history(self, ctx, current_prompt):
        """Appends thread context history to the prompt if available."""
        history = await self.get_thread_context(ctx)
        if not history:
            return current_prompt
        
        history_str = "\n".join([f"{item['author']}: {item['content']}" for item in history])
        return f"Thread History:\n{history_str}\n\nCurrent Request: {current_prompt}"

    @commands.command()
    async def code(self, ctx, language: str, *, prompt: str):
        """Generates code taking the FIRST word as language and the REST as prompt."""
        sk = get_skill(language)
        sys_p = f"You are Coder, an expert {language} developer."
        if sk:
            sys_p += f"\nFollow rules strictly:\n{sk}"

        full_prompt = await self.format_prompt_with_history(ctx, prompt)

        msg = await ctx.send(f"{EMOJI_LOADER} Generating `{language}` code...")
        res = await call_ai(sys_p, full_prompt)

        try:
            await msg.delete()
        except Exception:
            pass

        await send_smart(ctx, res)

    @commands.command()
    async def plan(self, ctx, *, prompt: str):
        """Generates software architecture and implementation plan."""
        full_prompt = await self.format_prompt_with_history(ctx, prompt)

        msg = await ctx.send(f"{EMOJI_LOADER} Planning system architecture...")
        sys_p = "You are an expert system architect. Provide a structured step-by-step roadmap and file outline."
        res = await call_ai(sys_p, full_prompt)

        try:
            await msg.delete()
        except Exception:
            pass

        await send_smart(ctx, res)

    @commands.command()
    async def ask(self, ctx, *, question: str):
        """Answers technical programming questions directly."""
        full_prompt = await self.format_prompt_with_history(ctx, question)

        msg = await ctx.send(f"{EMOJI_LOADER} Thinking...")
        sys_p = "You are Coder, an expert technical consultant. Answer clearly and concisely."
        res = await call_ai(sys_p, full_prompt)

        try:
            await msg.delete()
        except Exception:
            pass

        await send_smart(ctx, res)

    @commands.command()
    async def debug(self, ctx, language: str, *, raw_code: str):
        """Debugs broken code snippets."""
        full_prompt = await self.format_prompt_with_history(ctx, raw_code)

        msg = await ctx.send(f"{EMOJI_LOADER} Analyzing code for bugs...")
        sys_p = f"Find errors and provide fixed {language} code."
        res = await call_ai(sys_p, full_prompt)

        try:
            await msg.delete()
        except Exception:
            pass

        await send_smart(ctx, res)

async def setup(bot):
    await bot.add_cog(AICog(bot))
