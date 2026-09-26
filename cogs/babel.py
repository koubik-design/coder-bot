import re
import aiohttp
from bs4 import BeautifulSoup
import discord
from discord.ext import commands
from discord import app_commands
class Babel(commands.Cog):
    """Library of Babel search and coordinate lookup cog."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://libraryofbabel.info/search.html'
        }
    @staticmethod
    def clean_keyword(keyword: str) -> str:
        """Sanitize keyword to the 29 allowed characters in the Library of Babel."""
        return re.sub(r'[^a-z ,\.]', '', keyword.lower())
    async def fetch_babel_search(self, keyword: str) -> list[dict]:
        """Asynchronously queries search.cgi on libraryofbabel.info."""
        url = "https://libraryofbabel.info/search.cgi"
        payload = {"find": keyword}
        results = []
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.post(url, data=payload, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status != 200:
                        return results
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    locations = soup.find_all("div", {"class": "location"})
                    for loc in locations:
                        a_tag = loc.find("a", {"class": "intext"})
                        if a_tag and "onclick" in a_tag.attrs:
                            info = a_tag["onclick"]
                            data_points = re.findall(r"'([\w\-]+)'", info)
                            if len(data_points) >= 5:
                                hex_id, wall, shelf, volume, page = data_points[0:5]
                                vol_str = f"{int(volume):02d}" if volume.isdigit() else volume
                                book_url = f"https://libraryofbabel.info/book.cgi?{hex_id}-w{wall}-s{shelf}-v{vol_str}:{page}"
                                h3_tag = loc.find("h3")
                                match_type = h3_tag.text.strip() if h3_tag else "Match Location"
                                results.append({
                                    "type": match_type,
                                    "url": book_url,
                                    "coords": f"Hex: {hex_id[:8]}... | W:{wall} | S:{shelf} | V:{vol_str} | P:{page}",
                                    "hex": hex_id
                                })
            except Exception as e:
                print(f"[Babel Error]: {e}")
        return results
    @commands.hybrid_group(name="babel", fallback="help", description="Library of Babel search & lookup")
    async def babel(self, ctx: commands.Context):
        """Default help menu for babel command."""
        embed = discord.Embed(
            title="📚 Library of Babel Command Guide",
            description=(
                "**Usage:**\n"
                "• `!babel k:<keyword>` or `!babel search <keyword>` - Search by keyword\n"
                "• `!babel f:<hex_id>:<wall>:<shelf>:<volume>:<page>` or `!babel fetch <hex_id> <wall> <shelf> <volume> [page]` - Fetch coordinates"
            ),
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)
    @babel.command(name="search", description="Search the Library of Babel for a keyword")
    @app_commands.describe(query="Keyword or sentence to search for")
    async def search(self, ctx: commands.Context, *, query: str):
        """Search keyword or parse k:keyword syntax."""
        if query.lower().startswith("k:"):
            query = query[2:]
        cleaned = self.clean_keyword(query)
        if not cleaned.strip():
            await ctx.send(" Invalid query. Only lowercase letters, spaces, commas, and periods are allowed.")
            return
        async with ctx.typing():
            results = await self.fetch_babel_search(cleaned)
        if not results:
            await ctx.send(f"🔍 No matches found in the Library for: `{cleaned}`")
            return
        embed = discord.Embed(
            title=f"📚 Library of Babel Results for '{cleaned}'",
            color=discord.Color.blue()
        )
        for i, res in enumerate(results[:5], 1):
            embed.add_field(
                name=f"{i}. {res['type']}",
                value=f"📍 `{res['coords']}`\n🔗 [Open Book Page]({res['url']})",
                inline=False
            )
        await ctx.send(embed=embed)
    @babel.command(name="fetch", description="Fetch location via Hexagon:Wall:Shelf:Volume:Page")
    @app_commands.describe(
        hex_id="Hexagon ID / Name",
        wall="Wall number (1-4)",
        shelf="Shelf number (1-5)",
        volume="Volume number (1-32)",
        page="Page number (1-410)"
    )
    async def fetch(
        self, 
        ctx: commands.Context, 
        hex_id: str,
        wall: int, 
        shelf: int, 
        volume: int, 
        page: int = 1
    ):
        """Fetch page via hex/wall/shelf/volume/page coordinates."""
        vol_str = f"{volume:02d}"
        book_url = f"https://libraryofbabel.info/book.cgi?{hex_id}-w{wall}-s{shelf}-v{vol_str}:{page}"
        embed = discord.Embed(
            title="📖 Library of Babel Coordinate Location",
            url=book_url,
            color=discord.Color.green()
        )
        embed.add_field(name="Hexagon ID", value=f"`{hex_id}`", inline=False)
        embed.add_field(name="Wall", value=f"`{wall}`", inline=True)
        embed.add_field(name="Shelf", value=f"`{shelf}`", inline=True)
        embed.add_field(name="Volume", value=f"`{vol_str}`", inline=True)
        embed.add_field(name="Page", value=f"`{page}`", inline=True)
        embed.add_field(name="Direct Link", value=f"[Read Page]({book_url})", inline=False)
        await ctx.send(embed=embed)
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Listener to intercept inline k:{keyword} and f:{hex_id}:{wall}:{shelf}:{volume}:{page} syntax."""
        if message.author.bot:
            return
        content = message.content.strip()
        k_match = re.search(r'\bk:([a-zA-Z ,.]+)', content)
        if k_match:
            ctx = await self.bot.get_context(message)
            query = k_match.group(1)
            await self.search(ctx, query=query)
            return
        f_match = re.search(r'\bf:([\w\-]+):(\d+):(\d+):(\d+)(?::(\d+))?', content)
        if f_match:
            ctx = await self.bot.get_context(message)
            hex_id = f_match.group(1)
            wall, shelf, volume = map(int, f_match.groups()[1:4])
            page = int(f_match.group(5)) if f_match.group(5) else 1
            await self.fetch(ctx, hex_id=hex_id, wall=wall, shelf=shelf, volume=volume, page=page)
async def setup(bot: commands.Bot):
    await bot.add_cog(Babel(bot))
