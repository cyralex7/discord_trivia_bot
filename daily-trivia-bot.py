import discord
from discord.ext import commands, tasks
import csv
import requests
import os
from datetime import datetime

# Bot setup - replace with your bot token
TOKEN = 'MTM1MzAwOTYwNjcxNjI5NzI2Ng.GQZL2G.Hm_6UAVnEfolf6J0Zc3AFZhY65XjLlJXDXvsn8'
TRIVIA_CHANNEL_ID = 1353016373043007519  # Replace with your channel ID

# Setup bot with command prefix
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Global variables to track current question
current_question = None
current_answer = None
has_active_question = False

# Feature 4: Keep track of user scores in a CSV file
def load_scores():
    scores = {}
    
    # Create the file if it doesn't exist
    if not os.path.exists('scores.csv'):
        with open('scores.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['user_id', 'username', 'score'])
        return scores
    
    # Read the scores from the CSV file
    with open('scores.csv', 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            user_id, username, score = row
            scores[user_id] = int(score)
    
    return scores

def save_scores(scores, usernames):
    with open('scores.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['user_id', 'username', 'score'])
        
        for user_id, score in scores.items():
            username = usernames.get(user_id, "Unknown User")
            writer.writerow([user_id, username, score])

# Feature 1: Post Trivia question at a set interval
def get_trivia_question():
    # Get trivia from Open Trivia DB API
    response = requests.get("https://opentdb.com/api.php?amount=1&type=multiple")
    data = response.json()
    
    if data['response_code'] == 0:
        result = data['results'][0]
        return {
            'question': result['question'],
            'answer': result['correct_answer'],
            'hint': f"First letter: {result['correct_answer'][0]}"
        }
    else:
        # Backup question if API fails
        return {
            'question': "What language is this bot written in?",
            'answer': "Python",
            'hint': "It's named after a snake"
        }

@bot.event
async def on_ready():
    print(f"Bot is ready! Logged in as {bot.user}")
    post_question.start()

# Feature 1: Post trivia question daily
@tasks.loop(seconds=30)
async def post_question():
    global current_question, current_answer, has_active_question
    
    channel = bot.get_channel(TRIVIA_CHANNEL_ID)
    if channel:
        question_data = get_trivia_question()
        
        current_question = question_data['question']
        current_answer = question_data['answer']
        has_active_question = True
        
        await channel.send(f"🧠 **TRIVIA TIME!** 🎯\n\n{current_question}\n\n✍️ Reply with **!answer** to submit your response\n🤔 Need help? Type **!hint** for a clue\n🏆 Check the **!leaderboard** to see top players")

@post_question.before_loop
async def before_post_question():
    await bot.wait_until_ready()

# Feature 2: Allow users to submit answers
@bot.command(name="answer")
async def answer(ctx, *, user_answer):
    global has_active_question
    
    if not has_active_question:
        await ctx.send("There's no active question right now!")
        return
    
    # Feature 3: Check if answer is correct
    if user_answer.lower() == current_answer.lower():
        # Get scores 
        scores = load_scores()
        usernames = {}
        
        user_id = str(ctx.author.id)
        usernames[user_id] = ctx.author.name
        
        # Update score
        if user_id not in scores:
            scores[user_id] = 0
        scores[user_id] += 1
        
        # Save updated scores
        save_scores(scores, usernames)
        
        await ctx.send(f"Correct, {ctx.author.mention}! The answer is {current_answer}. You now have {scores[user_id]} points!")
        has_active_question = False
    else:
        await ctx.send(f"Sorry {ctx.author.mention}, that's not correct. Try again!")

# Feature 5: Display leaderboard when requested
@bot.command(name="leaderboard")
async def leaderboard(ctx):
    scores = {}
    usernames = {}
    
    # Read scores and usernames from CSV
    if not os.path.exists('scores.csv'):
        await ctx.send("No scores yet!")
        return
    
    with open('scores.csv', 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            if len(row) >= 3:  # Make sure row has enough elements
                user_id, username, score = row
                scores[user_id] = int(score)
                usernames[user_id] = username
    
    if not scores:
        await ctx.send("No scores yet!")
        return
    
    # Sort users by score
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # Create leaderboard message
    leaderboard_msg = "**🏆 TRIVIA LEADERBOARD 🏆**\n\n"
    
    for i, (user_id, score) in enumerate(sorted_scores[:10], 1):
        username = usernames.get(user_id, "Unknown User")
        leaderboard_msg += f"{i}. {username}: {score} points\n"
    
    await ctx.send(leaderboard_msg)

# Feature 6: Provide a hint
@bot.command(name="hint")
async def hint(ctx):
    if not has_active_question:
        await ctx.send("There's no active question right now!")
        return
    
    # Very simple hint - just first letter and length
    hint_text = f"Hint: The answer starts with '{current_answer[0]}' and has {len(current_answer)} characters."
    await ctx.send(hint_text)

# Run the bot
bot.run(TOKEN)