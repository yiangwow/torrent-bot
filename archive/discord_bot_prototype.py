import discord
from discord.ext import commands
from anthropic import Anthropic

# Initialize bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize Anthropic client
client = Anthropic()

# Store conversation history per user (for context)
conversation_history = {}

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")

@bot.event
async def on_message(message):
    # Ignore bot's own messages
    if message.author == bot.user:
        return

    # Only respond to mentions or replies
    if bot.user not in message.mentions and message.reference is None:
        return

    # Show typing indicator
    async with message.channel.typing():
        try:
            # Get or create conversation history for this user
            user_id = message.author.id
            if user_id not in conversation_history:
                conversation_history[user_id] = []

            # Add user message to history
            conversation_history[user_id].append({
                "role": "user",
                "content": message.content
            })

            # Get response from Claude
            response = client.messages.create(
                model="claude-opus-4-6",
                max_tokens=1000,
                system="You are a helpful Discord bot. Keep responses concise (under 2000 characters for Discord). Be friendly and conversational.",
                messages=conversation_history[user_id]
            )

            # Extract response text
            reply_text = response.content[0].text

            # Add assistant response to history
            conversation_history[user_id].append({
                "role": "assistant",
                "content": reply_text
            })

            # Keep history manageable (last 10 messages)
            if len(conversation_history[user_id]) > 20:
                conversation_history[user_id] = conversation_history[user_id][-20:]

            # Send response (split if too long for Discord's 2000 char limit)
            if len(reply_text) > 2000:
                # Split into chunks
                chunks = [reply_text[i:i+2000] for i in range(0, len(reply_text), 2000)]
                for chunk in chunks:
                    await message.reply(chunk, mention_author=False)
            else:
                await message.reply(reply_text, mention_author=False)

        except Exception as e:
            await message.reply(f"Error: {str(e)}", mention_author=False)

if __name__ == "__main__":
    # Load tokens from environment or ask for them
    import os

    discord_token = os.getenv("DISCORD_TOKEN")
    if not discord_token:
        discord_token = input("Enter your Discord bot token: ")

    bot.run(discord_token)
