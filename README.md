# qbithelparr

qbithelparr is a Discord bot that provides torrent status updates from qBittorrent. It can send notifications to both Discord channels.

## Features

- **Discord Integration**: Provides status updates on torrents directly in your Discord server.
- **Torrent Status Updates**: Shows the status of torrents, including downloading, completed, stalled, and more.
- **Customizable**: Configure categories and status types through a configuration file.

## Prerequisites

- Python 3.9+
- qBittorrent
- Discord Bot Token

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

3. Create and configure `config.ini`:

    ```ini
    [DISCORD]
    token = your_discord_bot_token
    botChannel = your_discord_channel_id

    [SONARR]
    tvCategory = tv

    [RADARR]
    movieCategory = movies

    [QBITTORRENT]
    host = localhost
    port = 8080
    username = your_qbittorrent_username
    password = your_qbittorrent_password
    ```

## Usage

1. Run the bot:
    ```bash
    python qbithelparr.py
    ```

2. Interact with the bot on Discord using the `/status` command to get the status of torrents.

## Docker

To run the bot in a Docker container:

1. Build the Docker image:
    ```bash
    docker build -t qbithelparr .
    ```

2. Run the Docker container:
    ```bash
    docker run -d --name qbithelparr-container qbithelparr
    ```

## Commands

- **/status**: Use this to see the status of what's currently downloading.
    - `/status movies`: See the status of movie torrents.
    - `/status tv`: See the status of TV torrents.
    - `/status completed`: See the completed torrents.
    - `/status all`: See all torrents.
    - Combine commands, like `/status tv completed`, to see completed TV shows.

## Contributing

Feel free to submit issues or pull requests if you have suggestions or improvements.
