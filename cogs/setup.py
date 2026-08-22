import aiohttp
import discord
from discord.ext import commands
import database

class CreateRepoView(discord.ui.View):
    def __init__(self, ctx, repo_name, token):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.repo_name = repo_name
        self.token = token

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.success)
    async def confirm_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("❌ This confirmation is not for you.", ephemeral=True)

        parts = self.repo_name.split("/")
        repo_short_name = parts[1] if len(parts) > 2 or "/" in self.repo_name else self.repo_name.split("/")[-1]

        url = "https://api.github.com/user/repos"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "Coder-Bot"
        }
        payload = {
            "name": repo_short_name,
            "private": False,
            "description": "Created via Coder-Bot Discord Integration"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status == 201:
                    data = await resp.json()
                    full_name = data["full_name"]
                    database.set_guild_repo(str(self.ctx.guild.id), full_name)
                    
                    embed = discord.Embed(
                        title="✅ Repository Created Successfully!",
                        description=f"Created and set working repo to **`{full_name}`**\n<{data['html_url']}>",
                        color=discord.Color.green()
                    )
                    await interaction.response.edit_message(embed=embed, view=None)
                else:
                    err_data = await resp.json()
                    await interaction.response.edit_message(content=f"❌ Failed to create repo: {err_data.get('message', 'Unknown error')}", embed=None, view=None)

    @discord.ui.button(label="No", style=discord.ButtonStyle.danger)
    async def confirm_no(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("❌ This confirmation is not for you.", ephemeral=True)

        embed = discord.Embed(
            title="❌ Operation Cancelled",
            description="Repository creation was cancelled.",
            color=discord.Color.red()
        )
        await interaction.response.edit_message(embed=embed, view=None)

class SetupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setup")
    async def setup_account(self, ctx, token: str = None):
        """Connect your GitHub account token so you don't have to re-enter it. Usage: c!setup ghp_XXX"""
        if not token:
            has_token = database.get_user_token(str(ctx.author.id)) is not None
            status = "Connected ✅" if has_token else "Not Connected ❌"
            return await ctx.send(f"⚙️ Your GitHub Account Token Status: **{status}**\nUse `c!setup <your_github_token>` to save/update it.")

        # Save token to database
        database.set_user_token(str(ctx.author.id), token)

        if ctx.guild:
            try:
                await ctx.message.delete()  # Delete message in server for security
            except discord.Forbidden:
                pass
            await ctx.author.send("🔒 Your GitHub token has been securely saved to your account!")
            await ctx.send(f"📬 {ctx.author.mention}, I have saved your GitHub token via Direct Message for security.", delete_after=10)
        else:
            await ctx.send("🔒 Your GitHub token has been securely saved!")

    @commands.command(name="change_repo")
    @commands.has_permissions(administrator=True)
    async def change_repo(self, ctx, repo_name: str = None):
        """Change working repo. Usage: c!change_repo owner/repo"""
        if not repo_name:
            current = database.get_guild_repo(str(ctx.guild.id))
            return await ctx.send(f"⚙️ Current working repo for this server is: `{current}`\nUse `c!change_repo owner/repo` to change it.")

        token = database.get_user_token(str(ctx.author.id))
        if not token:
            return await ctx.send("❌ You haven't linked your GitHub token yet! Run `c!setup <your_github_token>` first (preferably in DMs).")

        # Check if repository exists using GitHub API
        url = f"https://api.github.com/repos/{repo_name}"
        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "Coder-Bot"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    database.set_guild_repo(str(ctx.guild.id), repo_name)
                    await ctx.send(f"✅ Working repository changed and verified as **`{repo_name}`**!")
                elif resp.status == 404:
                    # Repo doesn't exist, prompt with Embed and Buttons
                    embed = discord.Embed(
                        title="⚠️ Repository Not Found",
                        description=f"Repo does not exist, Want to create new repo called **`{repo_name}`**?",
                        color=discord.Color.orange()
                    )
                    view = CreateRepoView(ctx, repo_name, token)
                    await ctx.send(embed=embed, view=view)
                else:
                    await ctx.send(f"⚠️ Error checking repository status (GitHub API status: {resp.status}).")

    @change_repo.error
    async def setup_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You need **Administrator** permissions to use `c!change_repo`.")

async def setup(bot):
    await bot.add_cog(SetupCog(bot))
