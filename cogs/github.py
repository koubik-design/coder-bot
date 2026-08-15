import aiohttp
import discord
from discord.ext import commands

class GitHubCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.default_repo = "koubik-design/coder-bot"
        self.headers = {"User-Agent": "Coder-Bot"}

    async def fetch(self, ctx, endpoint):
        url = f"https://api.github.com/{endpoint}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                if resp.status != 200:
                    await ctx.send(f"❌ API Error or Not Found (Status: {resp.status}).")
                    return None
                return await resp.json()

    def format_list(self, title, items, key, fallback="None"):
        if not items: return f"**{title}**: {fallback}"
        return f"**{title}**:\n" + "\n".join([f"• {i.get(key, 'Unknown')}" for i in items[:5]])

    # --- REPOSITORY COMMANDS ---
    
    @commands.command(name="repo")
    async def repo(self, ctx, repo=None):
        data = await self.fetch(ctx, f"repos/{repo or self.default_repo}")
        if data: await ctx.send(f"📦 **{data['full_name']}** - ⭐ {data['stargazers_count']} | 🍴 {data['forks_count']}\n<{data['html_url']}>")

    @commands.command(name="commits")
    async def commits(self, ctx, repo=None):
        data = await self.fetch(ctx, f"repos/{repo or self.default_repo}/commits?per_page=5")
        if data: await ctx.send(self.format_list("Recent Commits", data, "sha"))

    @commands.command(name="issues")
    async def issues(self, ctx, repo=None):
        data = await self.fetch(ctx, f"repos/{repo or self.default_repo}/issues?per_page=5")
        if data: await ctx.send(self.format_list("Open Issues", data, "title"))

    @commands.command(name="pulls")
    async def pulls(self, ctx, repo=None):
        data = await self.fetch(ctx, f"repos/{repo or self.default_repo}/pulls?per_page=5")
        if data: await ctx.send(self.format_list("Open Pull Requests", data, "title"))

    @commands.command(name="branches")
    async def branches(self, ctx, repo=None):
        data = await self.fetch(ctx, f"repos/{repo or self.default_repo}/branches")
        if data: await ctx.send(self.format_list("Branches", data, "name"))

    @commands.command(name="releases")
    async def releases(self, ctx, repo=None):
        data = await self.fetch(ctx, f"repos/{repo or self.default_repo}/releases?per_page=5")
        if data: await ctx.send(self.format_list("Recent Releases", data, "name", "No releases"))

    @commands.command(name="tags")
    async def tags(self, ctx, repo=None):
        data = await self.fetch(ctx, f"repos/{repo or self.default_repo}/tags")
        if data: await ctx.send(self.format_list("Tags", data, "name", "No tags"))

    @commands.command(name="contributors")
    async def contributors(self, ctx, repo=None):
        data = await self.fetch(ctx, f"repos/{repo or self.default_repo}/contributors?per_page=5")
        if data: await ctx.send(self.format_list("Top Contributors", data, "login"))

    @commands.command(name="languages")
    async def languages(self, ctx, repo=None):
        data = await self.fetch(ctx, f"repos/{repo or self.default_repo}/languages")
        if data:
            langs = "\n".join([f"• {k}" for k in list(data.keys())[:5]])
            await ctx.send(f"**Languages**:\n{langs}")

    @commands.command(name="forks")
    async def forks(self, ctx, repo=None):
        data = await self.fetch(ctx, f"repos/{repo or self.default_repo}/forks?per_page=5")
        if data: await ctx.send(self.format_list("Recent Forks", data, "full_name", "No forks yet"))

    @commands.command(name="stargazers")
    async def stargazers(self, ctx, repo=None):
        data = await self.fetch(ctx, f"repos/{repo or self.default_repo}/stargazers?per_page=5")
        if data: await ctx.send(self.format_list("Recent Stargazers", data, "login", "No stars yet"))

    @commands.command(name="license")
    async def license(self, ctx, repo=None):
        data = await self.fetch(ctx, f"repos/{repo or self.default_repo}")
        if data:
            lic = data.get("license")
            await ctx.send(f"⚖️ License for {data['full_name']}: **{lic['name'] if lic else 'None'}**")

    # --- USER COMMANDS ---

    @commands.command(name="user")
    async def user(self, ctx, username: str):
        data = await self.fetch(ctx, f"users/{username}")
        if data: await ctx.send(f"👤 **{data.get('name') or data['login']}**\nBio: {data.get('bio')}\nRepos: {data['public_repos']} | Followers: {data['followers']}\n<{data['html_url']}>")

    @commands.command(name="gists")
    async def gists(self, ctx, username: str):
        data = await self.fetch(ctx, f"users/{username}/gists?per_page=5")
        if data: await ctx.send(self.format_list(f"{username}'s Gists", data, "description", "No gists"))

    @commands.command(name="followers")
    async def followers(self, ctx, username: str):
        data = await self.fetch(ctx, f"users/{username}/followers?per_page=5")
        if data: await ctx.send(self.format_list(f"{username}'s Followers", data, "login", "No followers"))

    @commands.command(name="following")
    async def following(self, ctx, username: str):
        data = await self.fetch(ctx, f"users/{username}/following?per_page=5")
        if data: await ctx.send(self.format_list(f"{username} is Following", data, "login", "Not following anyone"))

    @commands.command(name="stars")
    async def stars(self, ctx, username: str):
        data = await self.fetch(ctx, f"users/{username}/starred?per_page=5")
        if data: await ctx.send(self.format_list(f"{username}'s Starred Repos", data, "full_name", "No starred repos"))

    @commands.command(name="orgs")
    async def orgs(self, ctx, username: str):
        data = await self.fetch(ctx, f"users/{username}/orgs")
        if data: await ctx.send(self.format_list(f"{username}'s Organizations", data, "login", "No orgs"))

    # --- SEARCH COMMANDS ---

    @commands.command(name="searchrepo")
    async def searchrepo(self, ctx, *, query: str):
        data = await self.fetch(ctx, f"search/repositories?q={query}&per_page=5")
        if data and data.get("items"): await ctx.send(self.format_list(f"Repo Search: {query}", data["items"], "full_name"))
        else: await ctx.send("No repositories found.")

    @commands.command(name="searchuser")
    async def searchuser(self, ctx, *, query: str):
        data = await self.fetch(ctx, f"search/users?q={query}&per_page=5")
        if data and data.get("items"): await ctx.send(self.format_list(f"User Search: {query}", data["items"], "login"))
        else: await ctx.send("No users found.")

async def setup(bot):
    await bot.add_cog(GitHubCog(bot))
