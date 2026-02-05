# ═══════════════════════════════════════════════════════════════════════════════
#  ⚙️ PREMIUM BOT CONFIGURATION
#  All colors and emojis in one place - easy to customize!
# ═══════════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════════
#  🎨 EMBED COLORS
#  Use hex format: 0xRRGGBB
# ═══════════════════════════════════════════════════════════════════════════════

class Colors:
    """All embed colors used throughout the bot"""

    # ─────────────────────────────────────────────────────────────
    # 🎨 MAIN BOT COLOR - Used for ALL embeds
    # ─────────────────────────────────────────────────────────────
    MAIN = 0x5DBB63               # Your brand color - Green

    # ─────────────────────────────────────────────────────────────
    # 🎯 GENERAL COLORS (for errors, warnings, etc.)
    # ─────────────────────────────────────────────────────────────
    SUCCESS = 0x5DBB63            # Green (same as main)
    ERROR = 0xFF4444              # Red
    WARNING = 0xFFAA00            # Orange


# ═══════════════════════════════════════════════════════════════════════════════
#  ✨ CUSTOM EMOJIS
#  Replace default emojis with your server's custom emojis!
#  
#  HOW TO GET EMOJI ID:
#  1. Type \:emoji_name: in Discord and send it
#  2. Copy the result: <:name:123456789> or  (animated)
#  3. Replace the emoji below with your custom one
#  
#  FORMAT:
#  • Static emoji:   "<:name:ID>"
#  • Animated emoji: ""
# ═══════════════════════════════════════════════════════════════════════════════

class Emojis:
    """All emojis used throughout the bot - customize these!"""

    # ─────────────────────────────────────────────────────────────
    # 🏓 PING COMMAND EMOJIS
    # ─────────────────────────────────────────────────────────────
    PING = "🏓"              # Replace: ""
    SIGNAL = "📶"            # Replace: "<:signal:YOUR_ID>"
    GAUGE = "🎯"             # Replace: "<:gauge:YOUR_ID>"

    # ─────────────────────────────────────────────────────────────
    # ⏱️ UPTIME COMMAND EMOJIS
    # ─────────────────────────────────────────────────────────────
    UPTIME = "⏱️"            # Replace: ""
    ROCKET = "🚀"            # Replace: ""
    TROPHY = "🏆"            # Replace: "<:trophy:YOUR_ID>"
    FIRE = "🔥"              # Replace: ""
    DIAMOND = "💎"           # Replace: ""
    TARGET = "🎯"            # Replace: "<:target:YOUR_ID>"
    HOURGLASS = "⏳"         # Replace: ""
    CPU = "💻"               # Replace: "<:cpu:YOUR_ID>"
    RAM = "🧠"               # Replace: "<:ram:YOUR_ID>"

    # ─────────────────────────────────────────────────────────────
    # ℹ️ INFO COMMAND EMOJIS
    # ─────────────────────────────────────────────────────────────
    INFO = "ℹ️"              # Replace: "<:info:YOUR_ID>"
    BOT = "🤖"               # Replace: "<:bot:YOUR_ID>"
    DEV = "👨‍💻"              # Replace: "<:developer:YOUR_ID>"
    STATS = "📊"             # Replace: "<:stats:YOUR_ID>"
    VERSION = "🏷️"           # Replace: "<:version:YOUR_ID>"
    SHARD = "🔷"             # Replace: "<:shard:YOUR_ID>"
    PYTHON = "🐍"            # Replace: "<:python:YOUR_ID>"
    DISCORD_EMOJI = "💬"     # Replace: "<:discord:YOUR_ID>"
    GITHUB = "📂"            # Replace: "<:github:YOUR_ID>"
    CHANNEL = "📢"           # Replace: "<:channel:YOUR_ID>"
    COMMAND = "⌨️"           # Replace: "<:command:YOUR_ID>"

    # ─────────────────────────────────────────────────────────────
    # 🌟 GENERAL/SHARED EMOJIS
    # ─────────────────────────────────────────────────────────────
    # Status
    ONLINE = "🟢"            # Replace: "<:online:YOUR_ID>"
    LOADING = "⏳"           # Replace: ""
    LIGHTNING = "⚡"         # Replace: ""
    SPARKLE = "✨"           # Replace: ""

    # Feedback
    CHECK = "✅"             # Replace: "<:check:YOUR_ID>"
    CROSS = "❌"             # Replace: "<:cross:YOUR_ID>"
    STAR = "⭐"              # Replace: "<:star:YOUR_ID>"
    CROWN = "👑"             # Replace: "<:crown:YOUR_ID>"
    HEART = "💖"             # Replace: ""

    # UI Elements
    GLOBE = "🌐"             # Replace: "<:globe:YOUR_ID>"
    CHART = "📊"             # Replace: "<:chart:YOUR_ID>"
    CLOCK = "🕐"             # Replace: "<:clock:YOUR_ID>"
    CALENDAR = "📅"          # Replace: "<:calendar:YOUR_ID>"
    TOOLS = "🛠️"             # Replace: "<:tools:YOUR_ID>"
    LINK = "🔗"              # Replace: "<:link:YOUR_ID>"
    SERVER = "🖥️"            # Replace: "<:server:YOUR_ID>"
    USERS = "👥"             # Replace: "<:users:YOUR_ID>"


# ═══════════════════════════════════════════════════════════════════════════════
#  📝 EXAMPLE: How to use custom emojis
# ═══════════════════════════════════════════════════════════════════════════════
#
#  Before (default emoji):
#      PING = "🏓"
#
#  After (your custom emoji):
#      PING = ""
#
#  To get the ID:
#  1. Go to your Discord server
#  2. Type: \:your_emoji_name:
#  3. Send the message
#  4. Copy the result (it will look like <:name:123456789>)
#  5. Paste it here!
#
# ═══════════════════════════════════════════════════════════════════════════════