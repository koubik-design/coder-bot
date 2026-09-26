import os
import glob
from discord.ext import commands
from utils import EMOJI_FILES, get_skill, send_smart
class SkillsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    async def addskill(self, ctx, language: str, *, rules: str):
        """Creates or updates a custom skill file."""
        lang = language.lower()
        path = f"skills/{lang}.md"
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# {lang.capitalize()} Rules\n\n{rules}")
        await ctx.send(f" {EMOJI_FILES} Saved custom skill: `skills/{lang}.md`!")
    @commands.command()
    async def listskills(self, ctx):
        """Lists all active skill .md files."""
        files = glob.glob("skills/*.md")
        if not files:
            await ctx.send(f"{EMOJI_FILES} No `.md` skills found in `/skills` folder.")
            return
        names = [os.path.basename(x).replace(".md", "") for x in files]
        await ctx.send(f"{EMOJI_FILES} **Loaded Skill Rulesets:**\n" + "\n".join([f"• `{n}`" for n in names]))
async def setup(bot):
    await bot.add_cog(SkillsCog(bot))
