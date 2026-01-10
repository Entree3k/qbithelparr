#!/bin/sh
set -e

# Create config.ini from environment variables if it doesn't exist
if [ ! -f "/usr/src/app/config.ini" ]; then
    echo "Creating config.ini from environment variables..."
    cat > /usr/src/app/config.ini <<EOF
# qbithelparr Configuration File
#
# This file was auto-generated from Docker environment variables.
# You can edit this file directly and restart the container.

[DISCORD]
# Your Discord bot token (from https://discord.com/developers/applications)
token = ${token:-your_discord_bot_token}

# The Discord channel ID where the bot will respond to commands
# Right-click channel -> Copy ID (requires Developer Mode enabled)
botChannel = ${botChannel:-your_discord_channel_id}

[SONARR]
# Category name for TV shows in qBittorrent (must match Sonarr's category)
tvCategory = ${TV_CATEGORY:-tv}

[RADARR]
# Category name for movies in qBittorrent (must match Radarr's category)
movieCategory = ${MOVIE_CATEGORY:-movies}

[QBITTORRENT]
# qBittorrent Web UI connection details
host = ${QBIT_HOST:-localhost}
port = ${QBIT_PORT:-8080}

# qBittorrent Web UI credentials
username = ${QBIT_USER:-admin}
password = ${QBIT_PASS:-adminpass}
EOF
    echo "config.ini created successfully"
else
    echo "config.ini already exists, skipping creation"
fi

# Execute the main command
exec python -u qbithelparr.py
