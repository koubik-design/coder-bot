# 🤖 Master Discord.py v2.x Coder AI Reference & Feature Specification

This master reference manual contains 52 complete code patterns, architecture templates, and implementation guides for building modular Discord bots using Python and `discord.py` v2.x.

---

## 📑 Core Cog Architecture & File Layout

Organize your codebase into modular extension Cogs for hot-reloading and clean separation of concerns.

```text
bot_project/
├── main.py                  # Bot entrypoint and extension loader
├── config.json              # Configurations and secrets
└── cogs/                    # Cog Extensions Directory
    ├── moderation.py        # Moderation commands
    ├── utility.py           # General tools & user commands
    └── admin.py             # Developer/owner administration
```

### Main Entry Point (`main.py`)

```python
import asyncio
import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} application command(s)")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")

async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and not filename.startswith('_'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

async def main():
    async with bot:
        await load_extensions()
        await bot.start("YOUR_BOT_TOKEN")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🚀 52 Feature & Implementation Handbook

---

### #1 Prefixed Command
Standard text-triggered commands executed via prefix.

```python
@commands.command(name="ping", help="Measures websocket latency")
async def ping(self, ctx: commands.Context):
    latency = round(self.bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Latency: `{latency}ms`")
```

---

### #2 Slash Command
Native Discord application command with typed inputs.

```python
@app_commands.command(name="greet", description="Send a personalized greeting")
@app_commands.describe(target="User to greet")
async def greet(self, interaction: discord.Interaction, target: discord.User):
    await interaction.response.send_message(f"Hello {target.mention}! 👋")
```

---

### #3 User Context Menu Command
Right-click on any server member to execute custom logic.

```python
@app_commands.context_menu(name="User Statistics")
async def user_stats_context(self, interaction: discord.Interaction, member: discord.Member):
    joined = member.joined_at.strftime("%Y-%m-%d") if member.joined_at else "Unknown"
    await interaction.response.send_message(
        f"👤 **User:** {member.mention}\n🆔 **ID:** `{member.id}`\n📅 **Joined:** `{joined}`"
    )
```

---

### #4 Message Context Menu Command
Right-click on any channel message to trigger custom actions.

```python
@app_commands.context_menu(name="Bookmark Message")
async def bookmark_context(self, interaction: discord.Interaction, message: discord.Message):
    try:
        await interaction.user.send(f"📌 **Bookmarked Message:**\n{message.content}")
        await interaction.response.send_message("Saved to DMs!", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("Unable to DM you.", ephemeral=True)
```

---

### #5 Hybrid Command
Functions as both a traditional prefix command (`!info`) and slash command (`/info`).

```python
@commands.hybrid_command(name="info", description="Display system status")
async def info(self, ctx: commands.Context):
    await ctx.send("⚙️ Core engine operational.")
```

---

### #6 Custom & Animated Emoji Rendering
Format static and animated guild emojis inside message strings.

```python
STATIC_EMOJI = "<:check_mark:123456789012345678>"
ANIMATED_EMOJI = "<a:loading:987654321098765432>"

@commands.command()
async def emojidemo(self, ctx: commands.Context):
    await ctx.send(f"Processing... {ANIMATED_EMOJI}\nStatus: Complete {STATIC_EMOJI}")
```

---

### #7 Rich Embed Construction
Create structured embed cards with thumbnails, fields, images, and footers.

```python
import datetime

embed = discord.Embed(
    title="🌌 System Telemetry",
    description="Live metrics overview.",
    color=discord.Color.blurple(),
    timestamp=datetime.datetime.now(datetime.timezone.utc)
)
embed.add_field(name="CPU Load", value="12%", inline=True)
embed.add_field(name="RAM Usage", value="4.2 GB", inline=True)
embed.set_footer(text="Node-01", icon_url=ctx.author.display_avatar.url)
await ctx.send(embed=embed)
```

---

### #8 Inline Replies & Ephemeral Responses
Send private responses visible only to the command invoker or direct quoted replies.

```python
# Ephemeral response (Slash commands only)
await interaction.response.send_message("🔒 Secret data.", ephemeral=True)

# Quoted inline reply without pinging author
await ctx.reply("Direct response", mention_author=False)
```

---

### #9 Action Buttons (`discord.ui.Button`)
Attach interactive buttons with distinct styles and callback functions.

```python
class ActionButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180.0)

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success, emoji="✅")
    async def confirm_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Confirmed!", ephemeral=True)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, emoji="❌")
    async def cancel_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Cancelled.", ephemeral=True)
```

---

### #10 String Select Menus (`discord.ui.Select`)
Interactive dropdown menus populated with static string choices.

```python
class OSSelectView(discord.ui.View):
    @discord.ui.select(
        placeholder="Select Operating System...",
        options=[
            discord.SelectOption(label="Linux", emoji="🐧", value="linux"),
            discord.SelectOption(label="Windows", emoji="🪟", value="windows"),
            discord.SelectOption(label="macOS", emoji="🍎", value="macos")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        await interaction.response.send_message(f"Selected: **{select.values[0]}**", ephemeral=True)
```

---

### #11 Channel Select Dropdowns (`discord.ui.ChannelSelect`)
UI components auto-populated with text or voice channels from the guild.

```python
class ChannelPickerView(discord.ui.View):
    @discord.ui.select(cls=discord.ui.ChannelSelect, channel_types=[discord.ChannelType.text])
    async def select_channel(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        chosen = select.values[0]
        await interaction.response.send_message(f"Target set to: {chosen.mention}", ephemeral=True)
```

---

### #12 Role Select Dropdowns (`discord.ui.RoleSelect`)
Dynamic dropdowns listing server roles automatically.

```python
class RoleAssignView(discord.ui.View):
    @discord.ui.select(cls=discord.ui.RoleSelect, placeholder="Select a role...")
    async def select_role(self, interaction: discord.Interaction, select: discord.ui.RoleSelect):
        role = select.values[0]
        await interaction.response.send_message(f"Selected Role: `{role.name}`", ephemeral=True)
```

---

### #13 Modal Popup Forms (`discord.ui.Modal`)
Pop-up dialog windows containing text input fields.

```python
class FeedbackModal(discord.ui.Modal, title="Submit Feedback"):
    username = discord.ui.TextInput(label="Name", placeholder="John Doe", required=True)
    details = discord.ui.TextInput(
        label="Feedback",
        style=discord.TextStyle.paragraph,
        placeholder="Describe issues here...",
        max_length=1000
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Thanks {self.username.value}! Feedback logged.", ephemeral=True
        )
```

---

### #14 Real-time Autocomplete
Provide real-time auto-suggestions as users enter slash command parameters.

```python
@app_commands.command(name="search_item", description="Find inventory item")
async def search_item(self, interaction: discord.Interaction, item: str):
    await interaction.response.send_message(f"Searching for: **{item}**")

@search_item.autocomplete('item')
async def item_autocomplete(
    self, interaction: discord.Interaction, current: str
) -> list[app_commands.Choice[str]]:
    items = ["iron_ingot", "iron_sword", "golden_apple", "diamond_pickaxe"]
    return [
        app_commands.Choice(name=i, value=i) for i in items if current.lower() in i.lower()
    ][:25]
```

---

### #15 Command Cooldowns & Rate Limits
Restrict execution frequency per user, channel, or server.

```python
@commands.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def claim(self, ctx: commands.Context):
    await ctx.send("💰 Claimed reward!")

@claim.error
async def claim_error(self, ctx: commands.Context, error: Exception):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Retry in `{error.retry_after:.1f}s`.")
```

---

### #16 Permission Checks
Verify member permission bits prior to execution.

```python
@app_commands.command(name="purge", description="Bulk clear messages")
@app_commands.checks.has_permissions(manage_messages=True)
async def purge(self, interaction: discord.Interaction, amount: int):
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"🧹 Cleared `{len(deleted)}` messages.", ephemeral=True)
```

---

### #17 Custom Error Handlers
Intercept local cog or command failures cleanly.

```python
async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ Missing permissions.", ephemeral=True)
    else:
        await interaction.response.send_message(f"⚠️ Error: `{error}`", ephemeral=True)
```

---

### #18 Background Tasks (`tasks.loop`)
Schedule recurring async functions for automated tasks.

```python
from discord.ext import tasks

class BackgroundCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.status_loop.start()

    def cog_unload(self):
        self.status_loop.cancel()

    @tasks.loop(minutes=15)
    async def status_loop(self):
        await self.bot.change_presence(activity=discord.Game(name="Online"))

    @status_loop.before_loop
    async def before_status_loop(self):
        await self.bot.wait_until_ready()
```

---

### #19 Event Listeners (`Cog.listener`)
Subscribe to gateway socket events within cog modules.

```python
@commands.Cog.listener()
async def on_member_join(self, member: discord.Member):
    channel = member.guild.system_channel
    if channel:
        await channel.send(f"Welcome {member.mention} to {member.guild.name}!")
```

---

### #20 Subcommands & Command Groups
Group slash commands under logical namespaces (`/config logging`).

```python
config_group = app_commands.Group(name="config", description="Configuration settings")

@config_group.command(name="logging", description="Set log channel")
async def set_logging(self, interaction: discord.Interaction, channel: discord.TextChannel):
    await interaction.response.send_message(f"Log channel set to {channel.mention}")
```

---

### #21 File Attachments & In-Memory Buffers
Send files created from string buffers directly to channels.

```python
import io

@commands.command()
async def send_log(self, ctx: commands.Context):
    data = "Log timestamp: 2026-08-22\nStatus: OK"
    file = discord.File(fp=io.StringIO(data), filename="status.log")
    await ctx.send("Logs generated:", file=file)
```

---

### #22 Thread Operations
Create, lock, and archive text threads.

```python
@commands.command()
async def start_thread(self, ctx: commands.Context, *, name: str):
    thread = await ctx.channel.create_thread(
        name=name,
        auto_archive_duration=60,
        type=discord.ChannelType.public_thread
    )
    await thread.send("Thread active.")
```

---

### #23 Reaction Mechanics
Add reactions and listen for responses via reaction logic.

```python
@commands.command()
async def poll(self, ctx: commands.Context, *, question: str):
    msg = await ctx.send(f"📊 **Poll:** {question}")
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")
```

---

### #24 Voice Channel Connections
Connect bot clients to user voice channels.

```python
@commands.command()
async def join(self, ctx: commands.Context):
    if ctx.author.voice and ctx.author.voice.channel:
        await ctx.author.voice.channel.connect()
        await ctx.send("Connected to voice!")
    else:
        await ctx.send("Join a voice channel first.")
```

---

### #25 Webhook Integration
Dispatch messages independently using Discord Webhook URLs.

```python
import aiohttp

@commands.command()
async def send_webhook(self, ctx: commands.Context, url: str, *, content: str):
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(url, session=session)
        await webhook.send(content=content, username="Notifier")
    await ctx.send("Webhook sent.")
```

---

### #26 Member Moderation (Timeout, Kick, Ban)
Apply native moderation enforcement onto guild members.

```python
import datetime

@app_commands.command(name="mute", description="Timeout a member")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(self, interaction: discord.Interaction, member: discord.Member, minutes: int):
    duration = datetime.timedelta(minutes=minutes)
    await member.timeout(duration)
    await interaction.response.send_message(f"Muted {member.mention} for {minutes}m.")
```

---

### #27 Audit Log Querying
Query recent guild administrative action logs.

```python
@commands.command()
@commands.has_permissions(view_audit_log=True)
async def audit_kicks(self, ctx: commands.Context):
    async for entry in ctx.guild.audit_logs(action=discord.AuditLogAction.kick, limit=3):
        await ctx.send(f"Kick: `{entry.target}` by `{entry.user}`")
```

---

### #28 Role Assignment & Removal
Programmatically update server member roles.

```python
@commands.command()
@commands.has_permissions(manage_roles=True)
async def add_role(self, ctx: commands.Context, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send(f"Added **{role.name}** to {member.mention}")
```

---

### #29 Channel & Category Creation
Create private or public categories and channels dynamically.

```python
@commands.command()
@commands.has_permissions(manage_channels=True)
async def create_private(self, ctx: commands.Context, name: str):
    guild = ctx.guild
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True)
    }
    category = await guild.create_category(name, overwrites=overwrites)
    await guild.create_text_channel("lounge", category=category)
    await ctx.send(f"Created category `{category.name}`")
```

---

### #30 Stage Channel Management
Control stage channel topics and active speaking instances.

```python
@commands.command()
async def start_stage(self, ctx: commands.Context, stage: discord.StageChannel, topic: str):
    instance = await stage.create_instance(topic=topic)
    await ctx.send(f"Stage live: **{instance.topic}**")
```

---

### #31 Guild Branding & Asset Retrieval
Inspect server banners, icons, and custom configurations.

```python
@commands.command()
async def guild_info(self, ctx: commands.Context):
    g = ctx.guild
    banner = g.banner.url if g.banner else "None"
    icon = g.icon.url if g.icon else "None"
    await ctx.send(f"**Guild:** {g.name}\nIcon: {icon}\nBanner: {banner}")
```

---

### #32 Invite Tracking
Fetch and inspect active guild invite code metrics.

```python
@commands.command()
@commands.has_permissions(manage_guild=True)
async def list_invites(self, ctx: commands.Context):
    invites = await ctx.guild.invites()
    data = [f"`{i.code}` - Uses: `{i.uses}`" for i in invites[:5]]
    await ctx.send("\n".join(data) if data else "No invites.")
```

---

### #33 Scheduled Events Engine
Schedule official Discord guild events programmatically.

```python
@commands.command()
@commands.has_permissions(manage_events=True)
async def schedule_event(self, ctx: commands.Context, name: str):
    start = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
    event = await ctx.guild.create_scheduled_event(
        name=name,
        start_time=start,
        end_time=start + datetime.timedelta(hours=1),
        entity_type=discord.EntityType.external,
        location="https://discord.gg"
    )
    await ctx.send(f"Event planned: {event.url}")
```

---

### #34 High-Res Avatar Inspector
Retrieve high-resolution display avatars for specified members.

```python
@commands.command()
async def avatar(self, ctx: commands.Context, member: discord.Member = None):
    target = member or ctx.author
    await ctx.send(target.display_avatar.with_size(1024).url)
```

---

### #35 Message Pin Control
Pin or unpin channel messages via commands.

```python
@commands.command()
@commands.has_permissions(manage_messages=True)
async def pin(self, ctx: commands.Context, message_id: int):
    msg = await ctx.channel.fetch_message(message_id)
    await msg.pin()
    await ctx.send("Pinned message.")
```

---

### #36 Embed Pagination Engine
Build multi-page interactive embed browsers using UI components.

```python
class EmbedPaginator(discord.ui.View):
    def __init__(self, pages: list[discord.Embed]):
        super().__init__(timeout=60)
        self.pages = pages
        self.index = 0

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.index > 0:
            self.index -= 1
            await interaction.response.edit_message(embed=self.pages[self.index], view=self)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.index < len(self.pages) - 1:
            self.index += 1
            await interaction.response.edit_message(embed=self.pages[self.index], view=self)
```

---

### #37 Interactive Confirmation Dialogs
Reusable yes/no confirmation views.

```python
class ConfirmView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        self.stop()
        await interaction.response.send_message("Confirmed", ephemeral=True)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        self.stop()
        await interaction.response.send_message("Cancelled", ephemeral=True)
```

---

### #38 Argument Converters
Convert raw string parameters into fully typed API objects automatically.

```python
@commands.command()
async def parse_member(self, ctx: commands.Context, member: discord.MemberConverter):
    await ctx.send(f"Member ID: `{member.id}`")
```

---

### #39 Guild Feature Flag Checking
Inspect enabled guild flags (`COMMUNITY`, `VANITY_URL`, etc.).

```python
@commands.command()
async def check_features(self, ctx: commands.Context):
    flags = ", ".join(ctx.guild.features)
    await ctx.send(f"Features: `{flags}`")
```

---

### #40 Raw Reaction Event Handling
Intercept reactions on uncached messages using raw payloads.

```python
@commands.Cog.listener()
async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
    if payload.emoji.name == "⭐":
        print(f"Star added to message ID {payload.message_id}")
```

---

### #41 Hot-Reloading Cog Extensions
Reload cogs at runtime without stopping bot execution.

```python
@commands.command()
@commands.is_owner()
async def reload(self, ctx: commands.Context, extension: str):
    await self.bot.reload_extension(f"cogs.{extension}")
    await ctx.send(f"Reloaded `cogs.{extension}`")
```

---

### #42 Global Command Check Registration
Enforce security validation across all commands.

```python
def not_blacklisted():
    async def predicate(ctx):
        blacklisted = [111111111]
        return ctx.author.id not in blacklisted
    return commands.check(predicate)
```

---

### #43 Interaction Deferrals
Defer slash responses to prevent standard 3-second timeouts on heavy workloads.

```python
@app_commands.command(name="heavy_task", description="Runs a long operation")
async def heavy_task(self, interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    await asyncio.sleep(5)
    await interaction.followup.send("Operation finished!")
```

---

### #44 Webhook Follow-up Messages
Send secondary followup messages after initial interaction response.

```python
@app_commands.command(name="followup_demo", description="Demonstrate followups")
async def followup_demo(self, interaction: discord.Interaction):
    await interaction.response.send_message("Initial response.")
    await interaction.followup.send("Follow-up response.", ephemeral=True)
```

---

### #45 Auto-Deleting Temporary Messages
Construct temporary status notifications that clean themselves up.

```python
@commands.command()
async def temp_alert(self, ctx: commands.Context):
    msg = await ctx.send("⚠️ Self-destructing in 5s...")
    await asyncio.sleep(5)
    await msg.delete()
```

---

### #46 Time Duration Utility Parser
Convert human-readable time strings into standard numerical seconds.

```python
def parse_duration(duration_str: str) -> int:
    unit = duration_str[-1]
    val = int(duration_str[:-1])
    rates = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
    return val * rates.get(unit, 1)

# Example: parse_duration("10m") -> 600
```

---

### #47 Direct Message Safe Sending
Send private DMs with exception handling for disabled user DMs.

```python
@commands.command()
async def send_dm(self, ctx: commands.Context, user: discord.User, *, text: str):
    try:
        await user.send(f"Message: {text}")
        await ctx.send("DM delivered.")
    except discord.Forbidden:
        await ctx.send("Target user has DMs closed.")
```

---

### #48 System Notification Filtering
Filter out non-default system messages during event handling.

```python
@commands.Cog.listener()
async def on_message(self, message: discord.Message):
    if message.type != discord.MessageType.default:
        return # Ignore pins, joins, boosts
```

---

### #49 Application Metadata Inspection
Access developer portal application configuration flags.

```python
@commands.command()
@commands.is_owner()
async def bot_info(self, ctx: commands.Context):
    app = await self.bot.application_info()
    await ctx.send(f"App Owner: `{app.owner}` | Public Bot: `{app.bot_public}`")
```

---

### #50 Rich Presence Activity Updates
Update bot status presence (Playing, Streaming, Listening, Watching).

```python
@commands.command()
@commands.is_owner()
async def set_presence(self, ctx: commands.Context, *, game_name: str):
    activity = discord.Game(name=game_name)
    await self.bot.change_presence(status=discord.Status.online, activity=activity)
    await ctx.send(f"Presence updated to Playing **{game_name}**")
```

---

### #51 Announcement Auto-Publishing
Auto-crosspost news channel messages to follower channels.

```python
@commands.Cog.listener()
async def on_message(self, message: discord.Message):
    if message.channel.type == discord.ChannelType.news:
        try:
            await message.publish()
        except discord.HTTPException:
            pass
```

---

### #52 AutoSharded Bot Architecture
Configure auto-sharding for large deployments spanning over 2,500 servers.

```python
intents = discord.Intents.default()
intents.message_content = True

bot = commands.AutoShardedBot(
    command_prefix="!",
    intents=intents,
    shard_count=2
)
```
