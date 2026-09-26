import discord
from discord.ext import commands
from pathlib import Path
class StatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.laws_file = Path(__file__).resolve().parent.parent / "3AL.md"
    @commands.command(name="status")
    async def show_status(self, ctx):
        """Shows status, ping, bot name, and AI laws summary."""
        latency = round(self.bot.latency * 1000)
        guild_count = len(self.bot.guilds)
        laws_summary = "3AL.md not found."
        if self.laws_file.exists():
            laws_summary = self.laws_file.read_text(encoding="utf-8")
        embed = discord.Embed(
            title=f" Bot Status: {self.bot.user.name}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.add_field(name=" Ping Latency", value=f"`{latency}ms`", inline=True)
        embed.add_field(name="🟢 System Status", value="`ONLINE / OPERATIONAL`", inline=True)
        embed.add_field(name=" Connected Servers", value=f"`{guild_count} server(s)`", inline=True)
        server_names = "\n".join([f"• {g.name}" for g in self.bot.guilds[:5]])
        if len(self.bot.guilds) > 5:
            server_names += f"\n...and {len(self.bot.guilds) - 5} more."
        embed.add_field(name="📋 Guild List", value=server_names or "None", inline=False)
        embed.add_field(name="📜 Core Directives (3AL)", value=laws_summary, inline=False)
        embed.set_footer(text=f"Prefix: {self.bot.command_prefix} • Coder-Bot System")
        await ctx.send(embed=embed)
async def setup(bot):
    await bot.add_cog(StatusCog(bot))
