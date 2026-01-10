# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY qbithelparr.py ./
COPY docker-entrypoint.sh ./

# Make entrypoint script executable
RUN chmod +x docker-entrypoint.sh

# Set environment variable to ensure Python output is sent straight to terminal
ENV PYTHONUNBUFFERED=1

# Default environment variables (can be overridden)
ENV token="your_discord_bot_token" \
    botChannel="your_discord_channel_id" \
    QBIT_HOST="localhost" \
    QBIT_PORT="8080" \
    QBIT_USER="admin" \
    QBIT_PASS="" \
    TV_CATEGORY="tv" \
    MOVIE_CATEGORY="movies"

# Use the entrypoint script
ENTRYPOINT ["./docker-entrypoint.sh"]
