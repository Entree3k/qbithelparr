import discord
from discord import app_commands
from discord.ext import commands
import qbittorrentapi
import configparser
import asyncio
import sys
from typing import List, Optional

# Load config
config = configparser.ConfigParser()
try:
    config.read("config.ini")
    print("Configuration file loaded successfully")
except Exception as e:
    print(f"Failed to load configuration file: {e}")
    sys.exit(1)

# Constants
STATUS_LIST = [
    "Completed",
    "Downloading",
    "Files missing",
    "Stalled",
    "Attempting to start",
    "Queued",
    "Paused",
    "Unknown status"
]
LIST_SEPARATOR = ",    "
NOTHING_DOWNLOADING = "Nothing is downloading! Why not request something?"
DOWNLOADING_STATUS = "downloading"
COMPLETE_STATUS = "completed"
MAX_CHARS_DISCORD = 1700
UPDATE_INTERVAL = 5  # seconds
UPDATE_COUNT = 6  # number of updates
AUTO_DELETE_DELAY = 30  # seconds

# Configuration
try:
    bot_channel = int(config['DISCORD']['botChannel'])
    tv_category = config['SONARR']['tvCategory']
    movie_category = config['RADARR']['movieCategory']
    TOKEN = config['DISCORD']['token']

    qbt_client = qbittorrentapi.Client(
        host=config['QBITTORRENT']['host'],
        port=int(config['QBITTORRENT']['port']),
        username=config['QBITTORRENT']['username'],
        password=config['QBITTORRENT']['password']
    )
    print("Configuration parsed successfully")
except KeyError as e:
    print(f"ERROR: Missing required configuration key: {e}")
    sys.exit(1)
except ValueError as e:
    print(f"ERROR: Invalid configuration value: {e}")
    sys.exit(1)

# Authenticate with qBittorrent
try:
    qbt_client.auth_log_in()
    print("Successfully authenticated with qBittorrent")
except qbittorrentapi.LoginFailed as e:
    print(f"ERROR: qBittorrent authentication failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: Failed to connect to qBittorrent: {e}")
    sys.exit(1)

# Helper Functions
def filter_torrents(torrent_info: List, filter_type: str) -> bool:
    """Filter torrents by category type."""
    return torrent_info[1] == filter_type or filter_type == "all"

def filter_and_sort_torrents(full_list: List, filter_type: str) -> List:
    """Filter and sort torrents by progress percentage."""
    try:
        filtered_list = [torrent for torrent in full_list if filter_torrents(torrent, filter_type)]

        # Sort by progress (incomplete first, sorted descending, then completed)
        sorted_list = sorted(
            [torrent for torrent in filtered_list if torrent[2] != "100%"],
            key=lambda x: float(x[2][:-1]),
            reverse=True
        )
        sorted_list.extend([torrent for torrent in filtered_list if torrent[2] == "100%"])

        return sorted_list
    except Exception as e:
        print(f"ERROR: Error filtering and sorting torrents: {e}")
        return []

def rename_states(full_list: List) -> List:
    """Map qBittorrent states to readable status labels."""
    state_mapping = {
        "uploading": STATUS_LIST[0],
        "pausedUP": STATUS_LIST[0],
        "checkingUP": STATUS_LIST[0],
        "stalledUP": STATUS_LIST[0],
        "forcedUP": STATUS_LIST[0],
        "downloading": STATUS_LIST[1],
        "missingFiles": STATUS_LIST[2],
        "stalledDL": STATUS_LIST[3],
        "metaDL": STATUS_LIST[4],
        "queuedDL": STATUS_LIST[5],
        "pausedDL": STATUS_LIST[6]
    }

    for torrent in full_list:
        torrent[3] = state_mapping.get(torrent[3], STATUS_LIST[7])

    return full_list

def find_downloading_torrents(full_list: List) -> List:
    """Filter torrents that are actively downloading or queued."""
    downloading_states = {
        STATUS_LIST[1],  # Downloading
        STATUS_LIST[3],  # Stalled
        STATUS_LIST[4],  # Attempting to start
        STATUS_LIST[5],  # Queued
        STATUS_LIST[6]   # Paused
    }
    return [torrent for torrent in full_list if torrent[3] in downloading_states]

def find_completed_torrents(full_list: List) -> List:
    """Filter torrents that are completed."""
    return [torrent for torrent in full_list if torrent[3] == STATUS_LIST[0]]

def convert_to_discord_message(info_list: List) -> List[str]:
    """Convert torrent info list to Discord-formatted messages."""
    if not info_list:
        return [NOTHING_DOWNLOADING]

    try:
        # Reorder fields: [progress, status, eta, name] and filter out infinite ETAs
        final_list = [
            [torrent[i] for i in [2, 3, 4, 0]]
            for torrent in info_list
            if torrent[4] != "inf"
        ]

        string_list = convert_list_to_string(final_list)
        current_length = len(string_list)
        current_msgs = []

        # Split into chunks that fit Discord's character limit
        while current_length > 0:
            max_length = string_list[:MAX_CHARS_DISCORD].count('\n')
            num_chars = find_nth_occurrence(string_list, '\n', max_length)

            if string_list[num_chars + 1:].count('\n') == 0:
                current_msgs.append(string_list)
                break
            else:
                current_msgs.append(string_list[:num_chars])
                string_list = string_list[num_chars + 1:]
                current_length -= MAX_CHARS_DISCORD

        return current_msgs
    except Exception as e:
        print(f"ERROR: Error converting to Discord message: {e}")
        return ["Error formatting torrent information"]

def find_nth_occurrence(string: str, substring: str, occurrence: int) -> int:
    """Find the nth occurrence of a substring in a string."""
    val = -1
    for _ in range(occurrence):
        val = string.find(substring, val + 1)
    return val

def convert_list_to_string(non_str_list: List) -> str:
    """Convert nested list to formatted string."""
    string_list = str(non_str_list)

    if LIST_SEPARATOR not in string_list:
        string_list = (string_list
                      .replace("'], ['", "\n\n")
                      .replace("']]", "")
                      .replace("[['", "")
                      .replace("', '", LIST_SEPARATOR))
    else:
        string_list = (string_list
                      .replace("', '", "\n\n")
                      .replace("']", "")
                      .replace("['", ""))

    return string_list

def update_torrent_list() -> List:
    """Fetch current torrent list from qBittorrent."""
    try:
        torrents = qbt_client.torrents_info()
        return [
            [
                torrent.name,
                torrent.category,
                f"{round(torrent.progress * 100, 2)}%",
                torrent.state,
                convert_time(torrent.eta)
            ]
            for torrent in torrents
        ]
    except Exception as e:
        print(f"ERROR: Error fetching torrent list from qBittorrent: {e}")
        return []

def convert_time(seconds: int) -> str:
    """Convert seconds to human-readable ETA format."""
    if seconds == 8640000:
        return "inf"

    intervals = (
        ('weeks', 604800),
        ('days', 86400),
        ('hours', 3600),
        ('minutes', 60),
        ('seconds', 1),
    )

    result = []
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append(f"{value} {name}")

    return 'ETA: ' + ', '.join(result) if result else 'ETA: 0 seconds'

def update_all_torrents(category: str, status: str = "all") -> List[str]:
    """Update and format all torrents based on category and status filters."""
    try:
        torrent_list = update_torrent_list()

        if not torrent_list:
            return [NOTHING_DOWNLOADING]

        filtered_list = filter_and_sort_torrents(torrent_list, category)
        renamed_list = rename_states(filtered_list)

        if status == DOWNLOADING_STATUS:
            renamed_list = find_downloading_torrents(renamed_list)
        elif status == COMPLETE_STATUS:
            renamed_list = find_completed_torrents(renamed_list)

        return convert_to_discord_message(renamed_list)
    except Exception as e:
        print(f"ERROR: Error updating torrents: {e}")
        return ["Error fetching torrent information"]

# Discord Bot Initialization
print("Initializing Discord bot...")

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    """Event handler for bot ready state."""
    print(f'Bot logged in as {bot.user} (ID: {bot.user.id})')

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"ERROR: Failed to sync commands: {e}")

    print("Bot is ready and operational")
    print("------------------------------------------------")
    print(f"Bot logged in as {bot.user}")
    print(f"Monitoring channel ID: {bot_channel}")
    print("------------------------------------------------")

@bot.event
async def on_error(event: str, *args, **kwargs):
    """Global error handler for bot events."""
    print(f"ERROR in event {event}")

@bot.tree.command(
    name="status",
    description="Check the status of torrents in qBittorrent"
)
@app_commands.describe(
    filter="Filter by category (movies/tv) or status (completed/downloading/all)"
)
async def status(interaction: discord.Interaction, filter: Optional[str] = "all"):
    """
    Slash command to display torrent status.

    Usage:
    /status - Show all torrents
    /status movies - Show movie torrents
    /status tv - Show TV show torrents
    /status completed - Show completed torrents
    /status tv completed - Show completed TV shows
    """
    try:
        # Check if command is used in the correct channel
        if interaction.channel_id != bot_channel:
            await interaction.response.send_message(
                f"This command can only be used in <#{bot_channel}>",
                ephemeral=True
            )
            return

        print(f"Status command invoked by {interaction.user} with filter: {filter}")

        # Defer the response since we'll be updating it multiple times
        await interaction.response.defer()

        # Parse filter arguments
        args = filter.lower().split() if filter else []

        category = "all"
        update_status = "all"

        if "movies" in args or "movie" in args:
            category = movie_category
        elif "tv" in args:
            category = tv_category

        if "completed" in args:
            update_status = COMPLETE_STATUS
        elif any(x in args for x in ["downloading", "paused", "stalled"]):
            update_status = DOWNLOADING_STATUS

        # Purge non-pinned messages in the channel
        try:
            await interaction.channel.purge(
                limit=100,
                check=lambda m: not m.pinned and m.id != interaction.id
            )
        except discord.Forbidden:
            print("WARNING: Bot lacks permission to purge messages")
        except Exception as e:
            print(f"ERROR: Error purging messages: {e}")

        # Send initial message
        discord_list = update_all_torrents(category, update_status)
        message_content = "\n\n".join(discord_list)
        sent_message = await interaction.followup.send(message_content)

        # Update the message periodically
        for i in range(UPDATE_COUNT - 1):
            await asyncio.sleep(UPDATE_INTERVAL)

            try:
                discord_list = update_all_torrents(category, update_status)
                message_content = "\n\n".join(discord_list)
                await sent_message.edit(content=message_content)
            except discord.NotFound:
                print("WARNING: Message was deleted before update could complete")
                break
            except Exception as e:
                print(f"ERROR: Error updating message: {e}")
                break

        # Auto-delete after delay
        await asyncio.sleep(AUTO_DELETE_DELAY)
        try:
            await sent_message.delete()
        except discord.NotFound:
            pass  # Message already deleted
        except Exception as e:
            print(f"ERROR: Error deleting message: {e}")

    except Exception as e:
        print(f"ERROR in status command: {e}")
        try:
            await interaction.followup.send(
                "An error occurred while fetching torrent status.",
                ephemeral=True
            )
        except:
            pass

# Run the bot
if __name__ == "__main__":
    try:
        print("Starting bot...")
        print("------------------------------------------------")
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("ERROR: Invalid Discord token")
        sys.exit(1)
    except Exception as e:
        print(f"FATAL ERROR running bot: {e}")
        sys.exit(1)
