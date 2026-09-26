# 🤖 Coder Bot

An advanced, asynchronous Python-based Discord bot designed for developer utilities, dynamic interaction handling, AutoSharded scalability, and specialized integrations such as the **Library of Babel** index and automated codebase sanitization.

---

## 📌 Table of Contents

* [Features](https://www.google.com/search?q=%2523-features&utm_source=gemini)
* [Architecture & Tech Stack](https://www.google.com/search?q=%2523-architecture--tech-stack&utm_source=gemini)
* [Repository Structure](https://www.google.com/search?q=%2523-repository-structure&utm_source=gemini)
* [Installation & Setup](https://www.google.com/search?q=%2523-installation--setup&utm_source=gemini)
* [Configuration](https://www.google.com/search?q=%2523-configuration&utm_source=gemini)
* [Commands & Modules](https://www.google.com/search?q=%2523-commands--modules&utm_source=gemini)
* [Core Utilities](https://www.google.com/search?q=%2523core-utilities&utm_source=gemini)
* [Library of Babel Cog (`cogs/babel.py`)](https://www.google.com/search?q=%2523library-of-babel-cog&utm_source=gemini)


* [Codebase Sanitization (`clean.py`)](https://www.google.com/search?q=%2523-codebase-sanitization&utm_source=gemini)
* [Deployment & Production](https://www.google.com/search?q=%2523-deployment--production&utm_source=gemini)
* [Contributing](https://www.google.com/search?q=%2523-contributing&utm_source=gemini)
* [License](https://www.google.com/search?q=%2523-license&utm_source=gemini)

---

## ✨ Features

* **⚡ High Performance & Scalability**: Built with `discord.ext.commands.AutoShardedBot` for handling 2,500+ servers smoothly.
* **📚 Library of Babel Integration**: Deep search and precise hex coordinate lookups via hybrid commands (`!babel`, `/babel`) and inline message listeners (`k:keyword`, `f:hex:wall:shelf:vol:page`).
* **🧹 Built-in Code Sanitizer**: Dedicated script for recursively stripping Python comments (`#`) and Unicode/Discord emojis across the codebase while preserving strings.
* **🛡️ Advanced Security & Checks**: Global command blacklist filters, owner-restricted operations, and secure DM handling.
* **⏳ Interaction Deferrals & Webhooks**: Prevents standard 3-second Discord timeouts on high-latency operations with `interaction.response.defer()`.
* **📢 Auto-Publishing**: Automatically crossposts news and announcement channel updates to follower guilds.
* **🎭 Dynamic Rich Presence**: Real-time status update commands for activity monitoring.

---

## 🛠️ Architecture & Tech Stack

| Component | Technology | Purpose |
| --- | --- | --- |
| **Language** | Python 3.10+ | Core language runtime |
| **Framework** | `discord.py` v2.x | Discord API interaction & slash commands |
| **HTTP Client** | `aiohttp` | Non-blocking asynchronous network requests |
| **HTML Parser** | `BeautifulSoup4` | Web scraping search results from external services |
| **Tokenization** | `tokenize` (Standard Lib) | Safe AST/Token-based comment removal |

---

## 📂 Repository Structure

```text
coder-bot/
├── cogs/
│   └── babel.py           # Library of Babel search and lookup cog
├── clean.py               # Standalone Python comment & emoji stripper
├── main.py                # Main bot entry point and initialization
├── requirements.txt       # Dependencies
└── README.md              # Project documentation

```

---

## 🚀 Installation & Setup

### Prerequisites

* Python **3.10** or higher
* A Discord Developer Account & Bot Token ([Discord Developer Portal](https://www.google.com/search?q=https://discord.com/developers/applications&utm_source=gemini))

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/coder-bot.git
cd coder-bot

```

### 2. Set Up Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

```

### 3. Install Dependencies

```bash
pip install -r requirements.txt

```

> **Required Packages**:
> ```text
> discord.py>=2.3.0
> aiohttp>=3.8.0
> beautifulsoup4>=4.12.0
> 
> ```
> 
> 

---

## ⚙️ Configuration

Create a `.env` or standard configuration file in the project root:

```env
DISCORD_TOKEN=your_bot_token_here
COMMAND_PREFIX=!
OWNER_ID=your_discord_user_id

```

Make sure the following **Privileged Gateway Intents** are enabled in the Discord Developer Portal under your Application settings:

* `MESSAGE_CONTENT`
* `GUILD_MESSAGES`

---

## 📖 Commands & Modules

### Core Utilities

| Command / Event | Description | Access |
| --- | --- | --- |
| `!set_presence <game>` | Updates the bot's status and rich presence activity. | Owner |
| `!bot_info` | Displays developer application metadata and flag statuses. | Owner |
| `!temp_alert` | Sends an alert message that automatically deletes after 5 seconds. | Everyone |
| `!send_dm <user> <text>` | Delivers a direct message to a user with exception safety. | Everyone |
| `on_message` | Automatic cross-publishing for News channels. | Automatic |

---

### Library of Babel Cog

The Babel cog connects your Discord server directly to `libraryofbabel.info`.

#### 1. Command Invocation

* **Search by Keyword:**
```text
!babel search universal library
/babel search query:universal library

```


* **Fetch Exact Coordinates:**
```text
!babel fetch hex_id:410 wall:1 shelf:2 volume:3 page:12

```



#### 2. Inline Triggers (Message Listener)

You can trigger the Babel search or coordinate fetch inline within any channel message without using explicit command prefixes:

* **Keyword Trigger**: Type `k:<keyword>` anywhere in your message.
```text
Hey check this out k:truth and wisdom

```


* **Coordinate Trigger**: Type `f:<hex_id>:<wall>:<shelf>:<volume>:<page>` anywhere in your message.
```text
Look at page f:0:1:2:3:15

```



---

## 🧹 Codebase Sanitization

The project includes `clean.py`, a script designed to clean Python code by removing all `#` comments (while preserving `#` inside strings) and stripping Unicode & custom Discord emojis.

### Running the Cleaner

To clean all `.py` files inside `~/coder-bot/`:

```bash
python3 ~/clean.py

```

### Features of the Cleaner:

* Uses Python's native `tokenize` module to distinguish between code comments and string literals containing `#`.
* Uses regular expressions to strip Unicode emojis and Discord custom emojis (`<:name:id>`).
* Automatically cleans empty lines left behind by deleted comment blocks.

---

## 🚢 Deployment & Production

### AutoSharding Configuration

For bots deployed across thousands of servers, AutoSharding is enabled natively in `main.py`:

```python
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.AutoShardedBot(
    command_prefix="!",
    intents=intents
)

```

### Running with Systemd (Raspberry Pi / Linux)

Create a systemd service file at `/etc/systemd/system/coderbot.service`:

```ini
[Unit]
Description=Coder Discord Bot
After=network.target

[Service]
Type=simple
User=server
WorkingDirectory=/home/server/coder-bot
ExecStart=/home/server/coder-bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable coderbot
sudo systemctl start coderbot

```

---

## 🤝 Contributing

1. **Fork** the repository.
2. **Create** a feature branch (`git checkout -b feature/NewFeature`).
3. **Run** `python3 ~/clean.py` prior to committing to ensure uniform formatting.
4. **Commit** your changes (`git commit -m 'Add NewFeature'`).
5. **Push** to the branch (`git push origin feature/NewFeature`).
6. **Open** a Pull Request.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
