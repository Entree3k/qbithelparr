# qbithelparr

qbithelparr is a Discord bot that provides torrent status updates from qBittorrent. It can send notifications to both Discord channels.

## Features

- **Discord Integration**: Provides status updates on torrents directly in your Discord server.
- **Torrent Status Updates**: Shows the status of torrents, including downloading, completed, stalled, and more.
- **Customizable**: Configure categories and status types through a configuration file.

## Prerequisites

- Python 3.9+
- qBittorrent with Web UI enabled
- Discord Bot Token (with proper intents enabled)
- Discord Developer Mode enabled (to get channel IDs)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/Entree3k/qbithelparr
    cd qbithelparr
    ```

2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Create your Discord bot:
    - Go to [Discord Developer Portal](https://discord.com/developers/applications)
    - Create a new application
    - Go to "Bot" section and create a bot
    - Enable these intents: Message Content Intent, Server Members Intent
    - Copy your bot token
    - Invite the bot to your server with these permissions: Send Messages, Manage Messages, Read Message History

4. Configure `config.ini`:
    - Edit the provided `config.ini` file
    - Add your Discord bot token
    - Add your Discord channel ID (right-click channel → Copy ID)
    - Configure qBittorrent connection details
    - Set category names to match your Sonarr/Radarr setup

## Usage

1. Run the bot:
    ```bash
    python qbithelparr.py
    ```

2. Interact with the bot on Discord using the `/status` slash command to get the status of torrents.

## Docker

### Using Docker Run

```bash
docker run -d \
  --name qbithelparr \
  --restart unless-stopped \
  -e token="your_discord_bot_token" \
  -e botChannel="your_discord_channel_id" \
  -e QBIT_HOST="localhost" \
  -e QBIT_PORT="8080" \
  -e QBIT_USER="admin" \
  -e QBIT_PASS="your_password" \
  -e TV_CATEGORY="tv" \
  -e MOVIE_CATEGORY="movies" \
  -v /path/to/config:/usr/src/app \
  entree3000/qbithelparr:latest
```

### Using Docker Compose

Create a `docker-compose.yml` file (see included example) and run:

```bash
docker-compose up -d
```

### Building from Source

```bash
docker build -t qbithelparr .
docker run -d --name qbithelparr-container qbithelparr
```

### Unraid Installation

1. Go to the **Apps** tab in Unraid
2. Search for **qbithelparr**
3. Fill in the configuration fields:
   - Discord Bot Token
   - Discord Channel ID
   - qBittorrent host, port, username, password
   - TV and Movie categories
4. Click **Apply**

The container will automatically create a `config.ini` file at `/mnt/user/appdata/qbithelparr/config.ini` which you can edit and then restart the container.

## Commands

- **/status [filter]**: Modern slash command to see the status of torrents.
    - `/status` or `/status all`: See all torrents
    - `/status movies`: See movie torrents only
    - `/status tv`: See TV show torrents only
    - `/status completed`: See completed torrents only
    - `/status downloading`: See actively downloading torrents only
    - `/status tv completed`: Combine filters to see completed TV shows
    - `/status movies downloading`: See movies currently downloading

**Note:** The status message updates every 5 seconds for 30 seconds, then auto-deletes. Non-pinned messages in the channel are cleared when the command is used.

## What's New

### Version 2.0 Improvements

- **Modern Discord.py 2.x**: Updated from deprecated 1.7.3 to latest discord.py with slash commands
- **Slash Commands**: Native Discord slash command integration
- **Comprehensive Error Handling**: Graceful error handling throughout with user-friendly error messages
- **Type Hints**: Added type annotations for better code maintainability
- **Better Documentation**: Improved docstrings and inline comments
- **Enhanced Configuration**: Better documented config.ini with instructions
- **Channel Validation**: Bot now validates it's being used in the correct channel
- **Improved Message Formatting**: Better error handling for edge cases in message formatting
- **Docker Support**: Updated Dockerfile with proper volume mounting and output buffering

## Contributing

Feel free to submit issues or pull requests if you have suggestions or improvements.
