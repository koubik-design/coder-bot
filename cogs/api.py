import discord
from discord.ext import commands
import database
import traceback

class APICog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="api")
    async def generate_api(self, ctx):
        """Generates a personal API key for the Coder-Bot CLI/Backend."""
        msg = await ctx.send("⏳ Generating your secure API key...")
        
        try:
            # Attempt to generate and store the key
            key = database.generate_key(str(ctx.author.id), str(ctx.author))
            
            try:
                # Send key via DM for security
                await ctx.author.send(
                    f"🔑 **Your Coder-Bot API Key:**\n`{key}`\n\n"
                    f"*Keep this secret! Use it for the CLI like this:*\n"
                    f"`coder-cli {key}`"
                )
                await msg.edit(content="✅ API key generated and sent to your DMs! Please check your private messages.")
            except discord.Forbidden:
                # Fallback if the user has DMs disabled
                await msg.edit(content=f"❌ I couldn't DM you! Please enable DMs from server members.")
                
        except Exception as e:
            # If the database or anything else crashes, print it to Discord!
            error_msg = str(e)
            print(f"API ERROR:\n{traceback.format_exc()}")
            await msg.edit(content=f"❌ **CRASHED:** Failed to generate key. Error:\n```python\n{error_msg}\n```")

async def setup(bot):
    await bot.add_cog(APICog(bot))
