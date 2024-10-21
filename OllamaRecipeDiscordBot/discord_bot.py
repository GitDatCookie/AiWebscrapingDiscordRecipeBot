#discord_bot.py
import os
from dotenv import load_dotenv

import discord
from discord.ext import commands

import logging
logging.basicConfig(level=logging.INFO)

from web_scraper import scrape_website, split_dom_content, clean_body_content, extract_body_content
from ollama_recipe_parser import parse_with_ollama
from ollama_chat_handler import handle_conversation  

# Load environment variables from a .env file
load_dotenv()
token = os.getenv("DISCORD_BOT_TOKEN")

# Define intents for the bot
intents = discord.Intents.default()
intents.message_content = True  # Ensure the bot can read message content
intents.dm_messages = True  # Ensure the bot can read direct messages

# Define global context
context = ""

# Initialize the bot with a command prefix
bot = commands.Bot(command_prefix="/", intents=intents)

# Recipe command to scrape a website and parse the recipe
@bot.command(name="recipe")
async def recipe(context, url):
    logging.info(f"Received /recipe command with URL: {url}")
    
    async with context.typing():  # Show typing indicator while processing
        try:
            result = scrape_website(url)
            body_content = extract_body_content(result)
            cleaned_content = clean_body_content(body_content)
            dom_chunks = split_dom_content(cleaned_content)
            ollama_result = parse_with_ollama(dom_chunks)
            await context.send(f"Parsed Recipe: \n{ollama_result}")
        except Exception as e:
            logging.error(f"Error processing /recipe command: {e}")
            



# On ready event to confirm bot is online
@bot.event
async def on_ready():
    logging.info(f"{bot.user.name} is ready")



# Direct message handler for ongoing conversations
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    global context # Use global context for chaar history

    # Handle direct messages
    if isinstance(message.channel, discord.DMChannel):
        user_input = message.content
        if user_input.lower() == "exit":
            await message.channel.send("Goodbye!")
            context = "" # Reset context
            return
        
        result = handle_conversation(context, user_input)
        await message.channel.send(result)
        context += f"\nUser:{user_input}\nAI:{result}"

    await bot.process_commands(message)


# Run the bot
bot.run(token)

