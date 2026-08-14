import discord
from discord.ext import commands
from pathlib import Path

class ThreeLawsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Path to 3AL.md in the root directory
        self.md_path = Path(__file__).resolve().parent.parent / "3AL.md"

    @commands.command(name="3al", aliases=["laws", "threelaws"])
    async def show_laws(self, ctx):
        """Displays the 3 Main AI Laws read from 3AL.md."""
        if not self.md_path.exists():
            await ctx.send("❌ `3AL.md` file was not found in the root directory!")
            return

        try:
            content = self.md_path.read_text(encoding="utf-8")
            
            embed = discord.Embed(
                title="📜 The 3 Main AI Laws",
                description=content,
                color=discord.Color.gold()
            )
            embed.set_footer(text="Source: 3AL.md")
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Error reading `3AL.md`: {e}")

async def setup(bot):
    await bot.add_cog(ThreeLawsCog(bot))
