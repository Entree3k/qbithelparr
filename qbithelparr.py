import discord
from discord.ext import commands
import qbittorrentapi
import configparser
import asyncio

# Load config
config = configparser.ConfigParser()
config.read("config.ini")

# Constants
STATUS_LIST = ["Completed", "Downloading", "Files missing", "Stalled", "Attempting to start", "Queued", "Paused", "Unknown status"]
LIST_SEPARATOR = ",    "
NOTHING_DOWNLOADING = "Nothing is downloading! Why not request something?"
DOWNLOADING_STATUS = "downloading"
COMPLETE_STATUS = "completed"

# Configuration
bot_channel = int(config['DISCORD']['botChannel'])
tv_category = config['SONARR']['tvCategory']
movie_category = config['RADARR']['movieCategory']
qbt_client = qbittorrentapi.Client(
    host=config['QBITTORRENT']['host'],
    port=int(config['QBITTORRENT']['port']),
    username=config['QBITTORRENT']['username'],
    password=config['QBITTORRENT']['password']
)
TOKEN = config['DISCORD']['token']

# Authenticate with qBittorrent
try:
    qbt_client.auth_log_in()
except qbittorrentapi.LoginFailed as e:
    print(e)

# Helper Functions
def filter_torrents(torrent_info, filter_type):
    return torrent_info[1] == filter_type or filter_type == "all"

def filter_and_sort_torrents(full_list, filter_type):
    filtered_list = [torrent for torrent in full_list if filter_torrents(torrent, filter_type)]
    sorted_list = sorted(
        [torrent for torrent in filtered_list if torrent[2] != "100%"],
        key=lambda x: float(x[2][:-1]),
        reverse=True
    )
    sorted_list.extend([torrent for torrent in filtered_list if torrent[2] == "100%"])
    return sorted_list

def rename_states(full_list):
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

def find_downloading_torrents(full_list):
    downloading_states = {STATUS_LIST[1], STATUS_LIST[3], STATUS_LIST[4], STATUS_LIST[5], STATUS_LIST[6]}
    return [torrent for torrent in full_list if torrent[3] in downloading_states]

def convert_to_discord_message(info_list):
    if not info_list:
        return [NOTHING_DOWNLOADING]

    max_chars_discord = 1700
    final_list = [[torrent[i] for i in [2, 3, 4, 0]] for torrent in info_list if torrent[4] != "inf"]
    string_list = convert_list_to_string(final_list)
    current_length = len(string_list)
    current_msgs = []

    while current_length > 0:
        max_length = string_list[:max_chars_discord].count('\n')
        num_chars = find_nth_occurrence(string_list, '\n', max_length)
        if string_list[num_chars + 1:].count('\n') == 0:
            current_msgs.append(string_list)
            break
        else:
            current_msgs.append(string_list[:num_chars])
            string_list = string_list[num_chars + 1:]
            current_length -= max_chars_discord

    return current_msgs

def find_nth_occurrence(string, substring, occurrence):
    val = -1
    for _ in range(occurrence):
        val = string.find(substring, val + 1)
    return val

def convert_list_to_string(non_str_list):
    string_list = str(non_str_list)
    if LIST_SEPARATOR not in string_list:
        string_list = string_list.replace("'], ['", "\n\n").replace("']]", "").replace("[['", "").replace("', '", LIST_SEPARATOR)
    else:
        string_list = string_list.replace("', '", "\n\n").replace("']", "").replace("['", "")
    return string_list

def update_torrent_list():
    return [
        [torrent.name, torrent.category, f"{round(torrent.progress * 100, 2)}%", torrent.state, convert_time(torrent.eta)]
        for torrent in qbt_client.torrents_info()
    ]

def convert_time(seconds):
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
    return 'ETA: ' + ', '.join(result)

def update_all_torrents(category, status="all"):
    torrent_list = update_torrent_list()
    filtered_list = filter_and_sort_torrents(torrent_list, category)
    renamed_list = rename_states(filtered_list)
    
    if status == DOWNLOADING_STATUS:
        renamed_list = find_downloading_torrents(renamed_list)
    elif status == COMPLETE_STATUS:
        renamed_list = find_completed_torrents(renamed_list)

    return convert_to_discord_message(renamed_list)

def find_completed_torrents(full_list):
    return [torrent for torrent in full_list if torrent[3] == STATUS_LIST[0]]

# Discord Bot Initialization
print("------------------------------------------------")
print("Starting Discord bot...")

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print("------------------------------------------------")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

@bot.command(
    help=(
        "Use this to see the status of what's currently downloading.\n"
        "If you want to get fancy, you can search for movies/tv shows specifically by typing /status movies or /status tv.\n"
        "You can also see what's completed by typing /status completed, or /status all to see everything.\n"
        "You can combine these (like /status tv completed) to only see completed tv shows.\n"
        "(tip: you can see everything by typing /status all)"
    ),
    brief="Use this to see what's currently downloading"
)
async def status(ctx, *args):
    if ctx.message.channel.id == bot_channel:
        await ctx.message.channel.purge(check=lambda m: not m.pinned)
        
        category = "all"
        update_status = "all"
        
        if "movies" in args:
            category = movie_category
        elif "tv" in args:
            category = tv_category
        
        if "completed" in args:
            update_status = COMPLETE_STATUS
        elif "downloading" in args or "paused" in args or "stalled" in args:
            update_status = DOWNLOADING_STATUS

        sent_message = None
        for _ in range(6):  # Update 6 times (every 5 seconds for 30 seconds)
            discord_list = update_all_torrents(category, update_status)
            message_content = "\n\n".join(discord_list)

            if sent_message is None:
                sent_message = await ctx.send(message_content)
            else:
                await sent_message.edit(content=message_content)

            await asyncio.sleep(5)

        await sent_message.delete(delay=30)  # Auto-delete after 30 seconds

bot.run(TOKEN)
