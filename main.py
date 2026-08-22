import asyncio
import os
from pathlib import Path
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging

# Setup logging to print everything to the console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Load environment variables explicitly from script's directory
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

TOKEN = os.getenv("DISCORD_TOKEN")

# Setup bot intents
intents = discord.Intents.default()
intents.message_content = True

# Disable default help command to use our custom paginated help cog
bot = commands.Bot(command_prefix="c!", intents=intents, help_command=None)

async def load_extensions():
    print("\n⚙️ Scanning & loading all cogs...")
    cogs_dir = Path(__file__).resolve().parent / "cogs"
    
    if cogs_dir.exists():
        for file in cogs_dir.glob("*.py"):
            if not file.name.startswith("__"):
                cog_name = f"cogs.{file.stem}"
                try:
                    await bot.load_extension(cog_name)
                    print(f"📦 Loaded extension: {cog_name}")
                except Exception as e:
                    print(f"❌ Failed to load extension {cog_name}: {e}")
    else:
        print("❌ 'cogs' directory not found!")

@bot.event
async def on_ready():
    print("\n" + "=" * 45)
    print(f"🚀 Bot Status  : ONLINE")
    print(f"🤖 Bot Identity: {bot.user.name}#{bot.user.discriminator} (ID: {bot.user.id})")
    print(f"🌐 Guilds      : Connected to {len(bot.guilds)} server(s)")
    print(f"⚡ Prefix      : '{bot.command_prefix}'")
    print("=" * 45 + "\n")

@bot.event
async def on_command(ctx):
    logging.info(f"[COMMAND USED] Author: {ctx.author} | Channel: {ctx.channel} | Command: {ctx.message.content}")

@bot.event
async def on_command_error(ctx, error):
    logging.error(f"[COMMAND ERROR] Command '{ctx.message.content}' raised an error: {error}")

async def main():
    if not TOKEN:
        print("\n❌ CRITICAL ERROR: DISCORD_TOKEN is missing or empty in .env!")
        print("   Make sure your .env file contains: DISCORD_TOKEN=your_token_here\n")
        return

    async with bot:
        await load_extensions()
        print("\n📡 Connecting to Discord Gateway...")
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot shutting down gracefully. Catch ya later!")
