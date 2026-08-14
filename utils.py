import os
import io
import re
import asyncio
import aiohttp
import discord
from dotenv import load_dotenv

# Load environment variables early
load_dotenv()

# Extract pure 32-character hex ID to prevent URL paste errors
raw_account_id = os.getenv("CF_ACCOUNT_ID", "")
account_id_match = re.search(r"[a-f0-9]{32}", raw_account_id, re.IGNORECASE)
CF_ACCOUNT_ID = account_id_match.group(0) if account_id_match else raw_account_id.strip().strip('"').strip("'")

CF_API_TOKEN = os.getenv("CF_API_TOKEN", "").strip().strip('"').strip("'")
CF_MODEL = "@cf/qwen/qwen2.5-coder-32b-instruct"

# Custom Emojis
EMOJI_LOADER = "<a:loader:1537089274103730206>"
EMOJI_FILES  = "<:files:1537090881901961266>"
EMOJI_WEB    = "<:web:1537090888759509133>"
EMOJI_GITHUB = "<:github:1537090886310297620>"


def repair_codeblocks(text: str) -> str:
    """Detects unclosed markdown code blocks and automatically appends closing backticks."""
    text = text.strip()
    backtick_count = text.count("```")
    # If the count of triple backticks is odd, the block was left unclosed by the AI
    if backtick_count % 2 != 0:
        text += "\n```"
    return text


def clean_codeblock(text: str) -> str:
    """Safely strips markdown code block wrappers when generating raw code files."""
    text = repair_codeblocks(text)
    if text.startswith("```"):
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1:]
        else:
            text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def get_skill(lang: str) -> str | None:
    """Loads markdown skill rulesets from /skills folder."""
    filepath = f"skills/{lang.lower()}.md"
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    return None


async def call_ai(system_prompt: str, user_prompt: str) -> str:
    """Sends prompt to Cloudflare Workers AI with custom max_tokens and timeout."""
    if not CF_ACCOUNT_ID or not CF_API_TOKEN:
        return "❌ **Configuration Error:** `CF_ACCOUNT_ID` or `CF_API_TOKEN` is missing in your `.env` file!"

    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/{CF_MODEL}"
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json"
    }

    full_system_prompt = (
        system_prompt +
        "\n\nCRITICAL: Keep your response complete, structured, and within response limits. Do not truncate code."
    )

    payload = {
        "messages": [
            {"role": "system", "content": full_system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 2048  # Ensures generation does not cut off prematurely
    }

    timeout = aiohttp.ClientTimeout(total=90)  # Extended 90-second timeout

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    raw_response = data["result"]["response"]
                    return repair_codeblocks(raw_response)
                else:
                    err = await resp.text()
                    return f"❌ **AI Connection Error ({resp.status}):** {err}"
    except asyncio.TimeoutError:
        return "⏰ **Request Timed Out:** AI generation took longer than 90 seconds. Please try again."
    except Exception as e:
        return f"❌ **Network Exception:** `{type(e).__name__}: {str(e)}`"


async def send_split_messages(ctx, text: str, max_length: int = 1800):
    """Splits long text into separate Discord messages while preserving code block syntax."""
    lines = text.split("\n")
    current_chunk = ""
    in_codeblock = False
    active_lang = ""

    for line in lines:
        if line.strip().startswith("```"):
            if not in_codeblock:
                in_codeblock = True
                active_lang = line.strip()[3:]
            else:
                in_codeblock = False
                active_lang = ""

        if len(current_chunk) + len(line) + 1 > max_length:
            if current_chunk:
                if in_codeblock:
                    current_chunk += "\n```"
                await ctx.send(current_chunk)

            if in_codeblock:
                current_chunk = f"```{active_lang}\n" + line
            else:
                current_chunk = line
        else:
            if current_chunk:
                current_chunk += "\n" + line
            else:
                current_chunk = line

    if current_chunk:
        await ctx.send(current_chunk)


class ResponseChoiceView(discord.ui.View):
    """Interactive Discord UI View providing action buttons when output > 1500 chars."""
    def __init__(self, text: str, ctx):
        super().__init__(timeout=120)
        self.text = text
        self.ctx = ctx
        self.message = None

    async def on_timeout(self):
        """Automatically disables buttons if user doesn't react within 120 seconds."""
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except Exception:
                pass

    @discord.ui.button(label="Download File", style=discord.ButtonStyle.primary, emoji="📥")
    async def download_file(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("❌ Only the command requester can select this option.", ephemeral=True)
            return

        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)

        buffer = io.BytesIO(self.text.encode("utf-8"))
        file = discord.File(fp=buffer, filename="response.md")
        await interaction.followup.send("📄 **Here is your full AI response:**", file=file)

    @discord.ui.button(label="Separate in Messages", style=discord.ButtonStyle.secondary, emoji="💬")
    async def split_messages(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("❌ Only the command requester can select this option.", ephemeral=True)
            return

        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)

        await send_split_messages(self.ctx, self.text)


async def send_smart(ctx, text: str):
    """
    Checks response character limit:
    - If <= 1500 chars: Sends directly.
    - If > 1500 chars: Prompts user with an Embed and interactive buttons.
    """
    text = repair_codeblocks(text)
    total_chars = len(text)

    # 1. Fits within 1,500 characters -> Send immediately
    if total_chars <= 1500:
        await ctx.send(text)
        return

    # 2. Exceeds 1,500 characters -> Prompt user with choice buttons
    embed = discord.Embed(
        title="⚠️ Response Character Limit Exceeded",
        description=(
            f"The AI generated a large response (**{total_chars:,}** characters), "
            f"which exceeds the **1,500** character limit.\n\n"
            f"How would you like to receive the output?"
        ),
        color=discord.Color.gold()
    )
    embed.set_footer(text="Select an option below to proceed.")

    view = ResponseChoiceView(text=text, ctx=ctx)
    msg = await ctx.send(embed=embed, view=view)
    view.message = msg
