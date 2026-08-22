import os
import discord
from discord.ext import commands, tasks
import itertools

class AvatarCycleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Define the paths to your logos
        # Assuming this file is inside /cogs/, we go up one directory if needed, 
        # or use a relative path from where the bot is launched.
        # Adjust the base_path to match your bot's root directory.
        base_path = os.path.join(os.path.dirname(__file__), "logos")
        self.logos = [
            os.path.join(base_path, "logo_1.png"),
            os.path.join(base_path, "logo_2.png")
        ]
        
        # Create an infinite iterator to cycle through the logos array
        self.logo_cycle = itertools.cycle(self.logos)

    @commands.Cog.listener()
    async def on_ready(self):
        """Start the loop once the bot is ready and logged in."""
        if not self.change_avatar_loop.is_running():
            self.change_avatar_loop.start()
            print("🔄 Avatar cycle loop started.")

    def cog_unload(self):
        """Ensure the loop stops if the cog is unloaded."""
        self.change_avatar_loop.cancel()

    # Discord heavily rate-limits avatar changes. 
    # 10 minutes is a safe interval to prevent 429 errors or token bans.
    @tasks.loop(minutes=10)
    async def change_avatar_loop(self):
        # Wait until bot's internal cache is ready before making API calls
        await self.bot.wait_until_ready()
        
        next_logo_path = next(self.logo_cycle)
        
        if not os.path.exists(next_logo_path):
            print(f"⚠️ Cannot find avatar image at {next_logo_path}")
            return

        try:
            with open(next_logo_path, "rb") as image_file:
                avatar_bytes = image_file.read()
                
            await self.bot.user.edit(avatar=avatar_bytes)
            print(f"✅ Successfully updated bot avatar to {os.path.basename(next_logo_path)}")
            
        except discord.HTTPException as e:
            # This catches rate limits (429) or other API errors
            print(f"❌ Failed to change avatar: {e}")
        except Exception as e:
            print(f"❌ Unexpected error changing avatar: {e}")

# REQUIRED ENTRY POINT
async def setup(bot: commands.Bot):
    await bot.add_cog(AvatarCycleCog(bot))
