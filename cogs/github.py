import discord
from discord.ext import commands
import aiohttp
import urllib.parse
from utils import EMOJI_GITHUB, send_smart

GITHUB_API = "https://api.github.com"


class GitHubCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "CoderDiscordBot"
        }

    async def fetch_json(self, url: str):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
                return None

    # ==========================================
    # 1. USER & PROFILE COMMANDS
    # ==========================================

    @commands.command(name="ghuser")
    async def gh_user(self, ctx, username: str):
        data = await self.fetch_json(GITHUB_API + "/users/" + username)
        if not data:
            return await ctx.send("❌ User not found.")

        embed = discord.Embed(
            title=EMOJI_GITHUB + " " + (data.get('name') or username) + " (@" + data['login'] + ")",
            url=data['html_url'],
            description=data.get('bio') or "No bio provided.",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=data['avatar_url'])
        embed.add_field(name="Public Repos", value=str(data['public_repos']), inline=True)
        embed.add_field(name="Followers", value=str(data['followers']), inline=True)
        embed.add_field(name="Following", value=str(data['following']), inline=True)
        embed.add_field(name="Location", value=data.get('location') or "N/A", inline=True)
        embed.add_field(name="Company", value=data.get('company') or "N/A", inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="searchuser")
    async def search_user(self, ctx, *, query: str):
        encoded = urllib.parse.quote(query)
        data = await self.fetch_json(GITHUB_API + "/search/users?q=" + encoded + "&per_page=5")
        if not data or not data.get("items"):
            return await ctx.send("❌ No users found.")

        users = ["• [" + u['login'] + "](" + u['html_url'] + ")" for u in data["items"]]
        embed = discord.Embed(
            title=EMOJI_GITHUB + " User Search: '" + query + "'",
            description="\n".join(users),
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    # ==========================================
    # 2. REPOSITORY COMMANDS
    # ==========================================

    @commands.command(name="repo")
    async def repo_info(self, ctx, repo: str):
        data = await self.fetch_json(GITHUB_API + "/repos/" + repo)
        if not data:
            return await ctx.send("❌ Repository not found. Format: owner/repo")

        embed = discord.Embed(
            title=EMOJI_GITHUB + " " + data['full_name'],
            url=data['html_url'],
            description=data.get('description') or "No description provided.",
            color=discord.Color.green()
        )
        embed.add_field(name="⭐ Stars", value=str(data['stargazers_count']), inline=True)
        embed.add_field(name="🍴 Forks", value=str(data['forks_count']), inline=True)
        embed.add_field(name="❗ Open Issues", value=str(data['open_issues_count']), inline=True)
        embed.add_field(name="💻 Language", value=data.get('language') or "N/A", inline=True)
        
        lic = data.get('license')
        embed.add_field(name="📜 License", value=lic.get('spdx_id') if lic else "None", inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="searchrepo")
    async def search_repo(self, ctx, *, query: str):
        encoded = urllib.parse.quote(query)
        data = await self.fetch_json(GITHUB_API + "/search/repositories?q=" + encoded + "&per_page=5")
        if not data or not data.get("items"):
            return await ctx.send("❌ No repositories found.")

        repos = []
        for r in data["items"]:
            desc = r.get('description') or 'No description'
            repos.append("• [" + r['full_name'] + "](" + r['html_url'] + ") - ⭐ " + str(r['stargazers_count']) + "\n  *" + desc + "*")
            
        embed = discord.Embed(
            title=EMOJI_GITHUB + " Repository Search: '" + query + "'",
            description="\n\n".join(repos),
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command(name="readme")
    async def repo_readme(self, ctx, repo: str):
        headers = {**self.headers, "Accept": "application/vnd.github.raw+json"}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(GITHUB_API + "/repos/" + repo + "/readme") as resp:
                if resp.status == 200:
                    text = await resp.text()
                    t = chr(96)
                    await send_smart(ctx, "### 📄 README for " + t + repo + t + "\n\n" + text[:1400])
                else:
                    await ctx.send("❌ README not found for this repository.")

    @commands.command(name="license")
    async def repo_license(self, ctx, repo: str):
        data = await self.fetch_json(GITHUB_API + "/repos/" + repo + "/license")
        if not data or "license" not in data:
            return await ctx.send("❌ No license file detected.")

        lic = data["license"]
        t = chr(96)
        embed = discord.Embed(
            title="📜 License: " + lic['name'],
            url=data.get("html_url", ""),
            description="**SPDX Identifier:** " + t + lic.get('spdx_id', 'None') + t,
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)

    @commands.command(name="topics")
    async def repo_topics(self, ctx, repo: str):
        headers = {**self.headers, "Accept": "application/vnd.github.mercury-preview+json"}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(GITHUB_API + "/repos/" + repo + "/topics") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    topics = data.get("names", [])
                    t = chr(96)
                    if not topics:
                        return await ctx.send("No topics found for " + t + repo + t + ".")
                    formatted = ", ".join([t + top + t for top in topics])
                    await ctx.send("🏷️ **Topics for " + t + repo + t + ":**\n" + formatted)
                else:
                    await ctx.send("❌ Could not fetch topics.")

    @commands.command(name="languages")
    async def repo_languages(self, ctx, repo: str):
        data = await self.fetch_json(GITHUB_API + "/repos/" + repo + "/languages")
        if not data:
            return await ctx.send("❌ Could not fetch language stats.")

        total_bytes = sum(data.values())
        if total_bytes == 0:
            return await ctx.send("No language statistics available.")

        stats = []
        for lang, bytes_cnt in data.items():
            pct = round(bytes_cnt / total_bytes * 100, 1)
            stats.append("• **" + lang + "**: " + str(pct) + "% (" + str(bytes_cnt) + " bytes)")
            
        t = chr(96)
        embed = discord.Embed(
            title="💻 Language Statistics for " + t + repo + t,
            description="\n".join(stats[:10]),
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed)

    # ==========================================
    # 3. CODE & BRANCH MANAGEMENT COMMANDS
    # ==========================================

    @commands.command(name="commits")
    async def repo_commits(self, ctx, repo: str):
        data = await self.fetch_json(GITHUB_API + "/repos/" + repo + "/commits?per_page=5")
        if not data or not isinstance(data, list):
            return await ctx.send("❌ Could not fetch commits.")

        commits = []
        t = chr(96)
        for c in data:
            sha = c['sha'][:7]
            msg = c['commit']['message'].split('\n')[0]
            author = c['commit']['author']['name']
            url = c['html_url']
            commits.append("• [" + t + sha + t + "](" + url + ") **" + msg + "** - *" + author + "*")

        embed = discord.Embed(
            title="📝 Recent Commits: " + t + repo + t,
            description="\n".join(commits),
            color=discord.Color.dark_gray()
        )
        await ctx.send(embed=embed)

    @commands.command(name="branches")
    async def repo_branches(self, ctx, repo: str):
        data = await self.fetch_json(GITHUB_API + "/repos/" + repo + "/branches?per_page=10")
        if not data or not isinstance(data, list):
            return await ctx.send("❌ Could not fetch branches.")

        t = chr(96)
        branches = ["• " + t + b['name'] + t for b in data]
        await ctx.send("🌿 **Branches in " + t + repo + t + ":**\n" + "\n".join(branches))

    @commands.command(name="tags")
    async def repo_tags(self, ctx, repo: str):
        data = await self.fetch_json(GITHUB_API + "/repos/" + repo + "/tags?per_page=10")
        if not data or not isinstance(data, list):
            return await ctx.send("❌ Could not fetch tags.")

        t = chr(96)
        tags = ["• " + t + tag['name'] + t + " (commit: " + t + tag['commit']['sha'][:7] + t + ")" for tag in data]
        await ctx.send("🏷️ **Recent Tags for " + t + repo + t + ":**\n" + "\n".join(tags))

    @commands.command(name="rawfile")
    async def raw_file(self, ctx, repo: str, *, file_path: str):
        base = "https://raw.githubusercontent.com/"
        url = base + repo + "/HEAD/" + file_path
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    t = chr(96)
                    msg1 = "📄 **File:** " + t + file_path + t
                    msg2 = " in " + t + repo + t + "\n"
                    code = t + t + t + "\n" + text[:1800] + "\n" + t + t + t
                    await send_smart(ctx, msg1 + msg2 + code)
                else:
                    t = chr(96)
                    err = "❌ File " + t + file_path + t + " not found."
                    await ctx.send(err)

    # ==========================================
    # 4. ISSUES, PRS & RELEASES
    # ==========================================

    @commands.command(name="issues")
    async def repo_issues(self, ctx, repo: str):
        data = await self.fetch_json(GITHUB_API + "/repos/" + repo + "/issues?state=open&per_page=5")
        if not data or not isinstance(data, list):
            return await ctx.send("❌ Could not fetch issues.")

        issues = ["• [#" + str(i['number']) + " " + i['title'] + "](" + i['html_url'] + ") by *" + i['user']['login'] + "*" for i in data if "pull_request" not in i]
        if not issues:
            return await ctx.send("🎉 No open issues found!")

        t = chr(96)
        embed = discord.Embed(
            title="❗ Open Issues: " + t + repo + t,
            description="\n".join(issues),
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    @commands.command(name="prs")
    async def repo_prs(self, ctx, repo: str):
        data = await self.fetch_json(GITHUB_API + "/repos/" + repo + "/pulls?state=open&per_page=5")
        if not data or not isinstance(data, list):
            return await ctx.send("❌ Could not fetch Pull Requests.")

        prs = ["• [#" + str(p['number']) + " " + p['title'] + "](" + p['html_url'] + ") by *" + p['user']['login'] + "*" for p in data]
        if not prs:
            return await ctx.send("🎉 No open Pull Requests found!")

        t = chr(96)
        embed = discord.Embed(
            title="🔀 Open Pull Requests: " + t + repo + t,
            description="\n".join(prs),
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)

    @commands.command(name="releases")
    async def repo_releases(self, ctx, repo: str):
        data = await self.fetch_json(GITHUB_API + "/repos/" + repo + "/releases/latest")
        if not data:
            return await ctx.send("❌ No official releases found.")

        t = chr(96)
        embed = discord.Embed(
            title="🚀 Latest Release: " + (data.get('name') or data['tag_name']),
            url=data['html_url'],
            description=data.get('body', '')[:1000] or "No release notes provided.",
            color=discord.Color.teal()
        )
        embed.add_field(name="Tag", value=t + data['tag_name'] + t, inline=True)
        embed.add_field(name="Author", value=data['author']['login'], inline=True)
        await ctx.send(embed=embed)

    # ==========================================
    # 5. COMMUNITY & WORKFLOWS
    # ==========================================

    @commands.command(name="contributors")
    async def repo_contributors(self, ctx, repo: str):
        data = await self.fetch_json(GITHUB_API + "/repos/" + repo + "/contributors?per_page=5")
        if not data or not isinstance(data, list):
            return await ctx.send("❌ Could not fetch contributors.")

        contribs = ["• [" + c['login'] + "](" + c['html_url'] + ") - **" + str(c['contributions']) + "** commits" for c in data]
        t = chr(96)
        embed = discord.Embed(
            title="👥 Top Contributors: " + t + repo + t,
            description="\n".join(contribs),
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    @commands.command(name="stargazers")
    async def repo_stargazers(self, ctx, repo: str):
        data = await self.fetch_json(GITHUB_API + "/repos/" + repo + "/stargazers?per_page=10")
        if not data or not isinstance(data, list):
            return await ctx.send("❌ Could not fetch stargazers.")

        stars = ["• [" + s['login'] + "](" + s['html_url'] + ")" for s in data]
        t = chr(96)
        await ctx.send("⭐ **Recent Stargazers for " + t + repo + t + ":**\n" + "\n".join(stars))

    @commands.command(name="forks")
    async def repo_forks(self, ctx, repo: str):
        data = await self.fetch_json(GITHUB_API + "/repos/" + repo + "/forks?per_page=5")
        if not data or not isinstance(data, list):
            return await ctx.send("❌ Could not fetch forks.")

        forks = ["• [" + f['full_name'] + "](" + f['html_url'] + ") by *" + f['owner']['login'] + "*" for f in data]
        t = chr(96)
        embed = discord.Embed(
            title="🍴 Recent Forks: " + t + repo + t,
            description="\n".join(forks),
            color=discord.Color.dark_teal()
        )
        await ctx.send(embed=embed)

    @commands.command(name="workflows")
    async def repo_workflows(self, ctx, repo: str):
        data = await self.fetch_json(GITHUB_API + "/repos/" + repo + "/actions/workflows")
        if not data or "workflows" not in data or not data["workflows"]:
            return await ctx.send("❌ No GitHub Actions workflows found.")

        t = chr(96)
        flows = ["• **" + w['name'] + "** (" + t + w['state'] + t + ") - [" + t + w['path'] + t + "](" + w['html_url'] + ")" for w in data["workflows"]]
        embed = discord.Embed(
            title="⚡ GitHub Workflows: " + t + repo + t,
            description="\n".join(flows),
            color=discord.Color.magenta()
        )
        await ctx.send(embed=embed)

    @commands.command(name="gist")
    async def get_gist(self, ctx, gist_id: str):
        data = await self.fetch_json(GITHUB_API + "/gists/" + gist_id)
        if not data:
            return await ctx.send("❌ Gist not found.")

        files = list(data.get("files", {}).keys())
        first_file_content = ""
        if files:
            first_file_content = data["files"][files[0]].get("content", "")[:1000]

        embed = discord.Embed(
            title="📌 Gist: " + (data.get('description') or 'Untitled Gist'),
            url=data['html_url'],
            description="**Owner:** " + data['owner']['login'] + "\n**Files:** " + ', '.join(files),
            color=discord.Color.light_grey()
        )
        await ctx.send(embed=embed)
        if first_file_content:
            t = chr(96)
            msg1 = "📄 **Content Preview (" + t + files[0] + t + "):**\n"
            msg2 = t + t + t + "\n" + first_file_content + "\n" + t + t + t
            await ctx.send(msg1 + msg2)


async def setup(bot):
    await bot.add_cog(GitHubCog(bot))
