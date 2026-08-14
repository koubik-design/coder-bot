import discord
from discord.ext import commands
import database

class APICog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="api", aliases=["key"])
    async def get_api_key(self, ctx):
        """Generates or fetches your personal API key."""
        # Generate or fetch existing key from SQLite database
        api_key = database.generate_api_key(
            discord_id=str(ctx.author.id),
            username=str(ctx.author)
        )

        embed = discord.Embed(
            title="🔑 Your Coder-Bot API Key",
            description="Keep this key private! Do not share it with anyone.",
            color=discord.Color.blue()
        )
        embed.add_field(name="API Key", value=f"`{api_key}`", inline=False)
        embed.add_field(
            name="🌐 GitHub Pages Portal Usage",
            value="Paste this key into the API key box on your web dashboard to authenticate.",
            inline=False
        )

        # Send DM for privacy
        try:
            await ctx.author.send(embed=embed)
            if ctx.guild:
                await ctx.send(f"📬 {ctx.author.mention}, sent your API key via Direct Message!", delete_after=10)
        except discord.Forbidden:
            await ctx.send("❌ I couldn't send you a DM! Please enable Direct Messages from server members in your Privacy Settings.")

async def setup(bot):
    await bot.add_cog(APICog(bot))
