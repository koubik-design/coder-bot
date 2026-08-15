import discord
from discord.ext import commands
import database

class AICog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def process_ai_request(self, ctx, prompt, task_type):
        # 1. Ban Check
        if database.is_user_banned(str(ctx.author.id)):
            return await ctx.send("❌ You are restricted from using this bot's AI capabilities.")

        async with ctx.typing():
            context_prompt = prompt

            # 2. Thread History Reading
            if isinstance(ctx.channel, discord.Thread):
                history_messages = []
                async for msg in ctx.channel.history(limit=10, oldest_first=True):
                    if msg.content:
                        author_label = "Bot" if msg.author.bot else msg.author.name
                        history_messages.append(f"{author_label}: {msg.content}")

                if history_messages:
                    conversation_history = "\n".join(history_messages)
                    context_prompt = f"Previous Conversation:\n{conversation_history}\n\n{task_type} Request: {prompt}"

            # Simulated AI Response Engine (Replace with your real AI API call)
            if task_type == "Code":
                ai_response = f"Here is the code you requested for:\n> {prompt}\n\n```python\n# Generated code goes here\nprint('Hello World')\n```"
            elif task_type == "Plan":
                ai_response = f"Here is your step-by-step plan for:\n> {prompt}\n\n1. First step\n2. Second step\n3. Execute"
            else:
                ai_response = f"I processed your query with context awareness!\n> {prompt}"

            # 3. Log Prompt to Database
            server_name = ctx.guild.name if ctx.guild else "Direct Message"
            database.log_prompt(
                discord_id=str(ctx.author.id),
                username=str(ctx.author),
                server_name=server_name,
                prompt=f"[{task_type}] {prompt}",
                response=ai_response
            )

            await ctx.send(ai_response)

    @commands.command(name="ask")
    async def ask(self, ctx, *, prompt: str):
        """Ask a general question."""
        await self.process_ai_request(ctx, prompt, "Question")

    @commands.command(name="code")
    async def code(self, ctx, *, prompt: str):
        """Generate code based on a prompt."""
        await self.process_ai_request(ctx, prompt, "Code")

    @commands.command(name="plan")
    async def plan(self, ctx, *, prompt: str):
        """Generate a step-by-step plan."""
        await self.process_ai_request(ctx, prompt, "Plan")

async def setup(bot):
    await bot.add_cog(AICog(bot))
