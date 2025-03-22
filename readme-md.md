# Discord Trivia Bot

A simple Discord bot that posts trivia questions and keeps track of user scores.

## Features

- Posts trivia questions on a set schedule
- Allows users to submit answers using !answer command
- Provides hints when users are stuck
- Tracks user scores in a CSV file
- Displays a leaderboard of top players

## Commands

- `!answer [your answer]` - Submit an answer to the current question
- `!hint` - Get a hint for the current question
- `!leaderboard` - View the top scoring players

## Setup

1. Install required packages:
```
pip install discord.py requests
```

2. Update the bot token and channel ID in the code
3. Run the bot:
```
python discord_trivia_bot.py
```

## Requirements

- Python 3.6 or higher
- discord.py
- requests
