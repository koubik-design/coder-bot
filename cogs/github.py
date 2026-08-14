import aiohttp
import discord
from discord.ext import commands

class GitHubCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.default_repo = "koubik-design/coder-bot"
        self.headers = {"User-Agent": "Coder-Bot-Discord"}

    @commands.command(name="repo")
    async def repo_info(self, ctx, repo_name: str = None):
        """Get repository stats. Usage: c!repo owner/repo"""
        target = repo_name or self.default_repo
        url = f"https://api.github.com/repos/{target}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                if resp.status != 200:
                    return await ctx.send(f"❌ Repository `{target}` not found or API rate limit reached.")
                data = await resp.json()

        embed = discord.Embed(
            title=f"📦 {data.get('full_name')}",
            url=data.get('html_url'),
            description=data.get('description') or "No description provided.",
            color=discord.Color.dark_theme()
        )
        embed.add_field(name="⭐ Stars", value=str(data.get("stargazers_count", 0)), inline=True)
        embed.add_field(name="🍴 Forks", value=str(data.get("forks_count", 0)), inline=True)
        embed.add_field(name="🐛 Open Issues", value=str(data.get("open_issues_count", 0)), inline=True)
        embed.add_field(
            name="📜 License", 
            value=data.get("license", {}).get("name") if data.get("license") else "None", 
            inline=True
        )
        embed.add_field(name="🌐 Language", value=str(data.get("language", "Unknown")), inline=True)
        embed.set_thumbnail(url=data.get("owner", {}).get("avatar_url", ""))
        
        await ctx.send(embed=embed)

    @commands.command(name="user", aliases=["ghuser"])
    async def user_info(self, ctx, username: str):
        """Get profile details for a GitHub user. Usage: c!user username"""
        url = f"https://api.github.com/users/{username}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                if resp.status != 200:
                    return await ctx.send(f"❌ GitHub user `{username}` not found.")
                data = await resp.json()

        embed = discord.Embed(
            title=f"👤 {data.get('name') or data.get('login')}",
            url=data.get('html_url'),
            description=data.get('bio') or "No bio available.",
            color=discord.Color.blue()
        )
        embed.add_field(name="📂 Public Repos", value=str(data.get("public_repos", 0)), inline=True)
        embed.add_field(name="👥 Followers", value=str(data.get("followers", 0)), inline=True)
        embed.add_field(name="➡️ Following", value=str(data.get("following", 0)), inline=True)
        embed.set_thumbnail(url=data.get("avatar_url", ""))

        await ctx.send(embed=embed)

    @commands.command(name="commits")
    async def recent_commits(self, ctx, repo_name: str = None):
        """Get recent commits for a repo. Usage: c!commits owner/repo"""
        target = repo_name or self.default_repo
        url = f"https://api.github.com/repos/{target}/commits?per_page=5"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                if resp.status != 200:
                    return await ctx.send(f"❌ Could not fetch commits for `{target}`.")
                commits = await resp.json()

        embed = discord.Embed(
            title=f"📜 Recent Commits: {target}",
            color=discord.Color.green()
        )

        for commit in commits[:5]:
            sha = commit.get("sha", "")[:7]
            msg = commit.get("commit", {}).get("message", "").split("\n")[0]
            author = commit.get("commit", {}).get("author", {}).get("name", "Unknown")
            commit_url = commit.get("html_url", "")
            embed.add_field(
                name=f"`{sha}` — {author}",
                value=f"[{msg}]({commit_url})",
                inline=False
            )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(GitHubCog(bot))
