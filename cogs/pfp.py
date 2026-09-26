import hashlib
import io
import re
import discord
from discord.ext import commands
from PIL import Image, ImageDraw
DEFAULT_GRID_SIZE = 5
MAX_GRID_SIZE = 128
IMAGE_SIZE = 512                               
def parse_pfp_args(args_str: str):
    """Parses query and optional resolution from input string.
    Examples:
        'user123'         -> ('user123', 5)
        'user123 16x16'   -> ('user123', 16)
        'user123 16'      -> ('user123', 16)
    """
    content = args_str.strip()
    if not content:
        raise ValueError("Usage: `c!pfp <username_or_query> [resolution]`")
    parts = content.rsplit(maxsplit=1)
    grid_size = DEFAULT_GRID_SIZE
    query = content
    if len(parts) == 2:
        res_match = re.match(r"^(\d+)(?:x(\d+))?$", parts[1], re.IGNORECASE)
        if res_match:
            query = parts[0]
            dim1 = int(res_match.group(1))
            dim2 = int(res_match.group(2)) if res_match.group(2) else dim1
            grid_size = max(dim1, dim2)
    grid_size = max(1, min(grid_size, MAX_GRID_SIZE))
    return query, grid_size
def generate_identicon(query: str, grid_size: int = DEFAULT_GRID_SIZE) -> Image.Image:
    """Generates a deterministic identicon Image for a given query."""
    hash_bytes = hashlib.sha256(query.encode("utf-8")).digest()
    fg_color = (hash_bytes[0], hash_bytes[1], hash_bytes[2])
    bg_color = (240, 240, 240)
    img = Image.new("RGB", (IMAGE_SIZE, IMAGE_SIZE), bg_color)
    draw = ImageDraw.Draw(img)
    cell_size = IMAGE_SIZE / grid_size
    half_grid = (grid_size + 1) // 2
    byte_idx = 3
    for x in range(half_grid):
        for y in range(grid_size):
            bit = (hash_bytes[byte_idx % len(hash_bytes)] >> (y % 8)) & 1
            byte_idx += 1
            if bit:
                x0, y0 = int(x * cell_size), int(y * cell_size)
                x1, y1 = int((x + 1) * cell_size), int((y + 1) * cell_size)
                draw.rectangle([x0, y0, x1, y1], fill=fg_color)
                right_x = grid_size - 1 - x
                if right_x != x:
                    rx0, ry0 = int(right_x * cell_size), int(y * cell_size)
                    rx1, ry1 = int((right_x + 1) * cell_size), int((y + 1) * cell_size)
                    draw.rectangle([rx0, ry0, rx1, ry1], fill=fg_color)
    return img
class PfpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command(name="pfp")
    async def pfp_command(self, ctx: commands.Context, *, args: str = ""):
        """Command usage: c!pfp <username/query> [resolution]"""
        if not args:
            query = ctx.author.display_name
            grid_size = DEFAULT_GRID_SIZE
        else:
            try:
                query, grid_size = parse_pfp_args(args)
            except ValueError as e:
                await ctx.send(str(e))
                return
        img = generate_identicon(query, grid_size)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        file = discord.File(buffer, filename=f"pfp_{grid_size}x{grid_size}.png")
        await ctx.send(f" Identicon for **{query}** ({grid_size}x{grid_size}):", file=file)
async def setup(bot: commands.Bot):
    await bot.add_cog(PfpCog(bot))
