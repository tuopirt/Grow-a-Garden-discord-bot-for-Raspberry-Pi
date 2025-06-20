import os
import discord
from discord.ext import commands
import asyncio
from dotenv import load_dotenv
from datetime import datetime, timedelta
# from other files
from scrapping import scrape_garden_stock  # make sure this function returns inventory list

import json
from collections import defaultdict

last_stock_snapshot = {}  # category -> list of (name, qty)

SUBS_FILE = "subscriptions.json"

# Load subscriptions from file
def load_subs():
    if not os.path.exists(SUBS_FILE):
        return {}
    with open(SUBS_FILE, "r") as f:
        return json.load(f)

# Save subscriptions to file
def save_subs(subs):
    with open(SUBS_FILE, "w") as f:
        json.dump(subs, f, indent=2)

subscriptions = load_subs()


# token/apis
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_IDS = [int(cid.strip()) for cid in os.getenv("CHANNEL_IDS", "").split(",") if cid.strip()]
#print("Parsed list:", CHANNEL_IDS)


# Set up bot with command prefix for discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


# check every irl 5 min interval
async def wait_until_next_5_minute_mark():
    # find current time stamp
    now = datetime.now()
    minutes_to_wait = 5 - (now.minute % 5) # irl 5 min interval
    next_time = now + timedelta(minutes=minutes_to_wait)
    next_time = next_time.replace(second=30, microsecond=0) # hardcoded 30s for the site to refresh
    await asyncio.sleep((next_time - now).total_seconds())


# Sends the actual message to all the different channels
async def send_message(msg):
    for channel_id in CHANNEL_IDS:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(msg)


# Action sends update to discord channel
async def create_message(stock):
    global last_stock_snapshot # last seen

    msg = "**🌱 GrowAGarden Stock Update 🌱**\n"

    # dict to keep track of who needs what
    mentions = defaultdict(list)
    has_alerts = False

    # add to msg
    for category, items in stock.items():
        msg += f"\n__**{category}**__\n"
        for name, qty in items:
            msg += f"{name}: {qty}\n"

        previous = last_stock_snapshot.get(category, [])
        if category in ["GEAR STOCK", "SEEDS STOCK"] or previous != items:
            for name, qty in items:
                # loop to add to dict if its item user wants
                for user_id, user_items in subscriptions.items():
                    # can add here in the future to check to see if that user is in the current server or not
                    if name.lower() in map(str.lower, user_items):
                        mentions[name].append(f"<@{user_id}>")
                        has_alerts = True
        
        last_stock_snapshot[category] = items
    
    # dict part 2
    if has_alerts:
        msg += "\n\n🔔 **Alerts:**\n"
        for item, users in mentions.items():
            msg += f"{item}: {' '.join(users)}\n"
    
    await send_message(msg)


# Main func
async def main():
    await bot.wait_until_ready()
    while True:
        stock = await scrape_garden_stock()  # scrape

        # error handle
        if not stock:
            for channel_id in CHANNEL_IDS:
                channel = bot.get_channel(channel_id)
                if channel:
                    await channel.send("⚠️ Failed to fetch stock data.")
            await wait_until_next_5_minute_mark()
            continue
        
        # create the discord msg (it will send within it)
        await create_message(stock)
        await wait_until_next_5_minute_mark()


# Manual command: !update
@bot.command(name="update")
async def force_update(ctx):
    await ctx.send("🔄 Forcing a stock update...")
    #if ctx.channel.id != CHANNEL_ID:
    stock = await scrape_garden_stock() # scrape
    if not stock:
        await ctx.send("⚠️ Failed to fetch stock data.")
        return
    
    if ctx.channel.id not in CHANNEL_IDS:
        return
    
    await create_message(ctx.channel, stock)

# Command: turn on alert for specific item
@bot.command(name="sub")
async def subscribe(ctx, *, item: str):
    user_id = str(ctx.author.id)
    item = item.lower()

    subscriptions.setdefault(user_id, [])
    if item in map(str.lower, subscriptions[user_id]):
        await ctx.send(f"⚠️ You’re already subscribed to **{item}**.")
        return
    
    subscriptions[user_id].append(item)
    save_subs(subscriptions)
    await ctx.send(f"✅ Subscribed to **{item}**.")

# Command: turn off alert for specific item
@bot.command(name="unsub")
async def unsubscribe(ctx, *, item: str):
    user_id = str(ctx.author.id)
    item = item.lower()

    if user_id in subscriptions:
        # Find actual item in list that matches, ignoring case
        for existing_item in subscriptions[user_id]:
            if existing_item.lower() == item:
                subscriptions[user_id].remove(existing_item)
                save_subs(subscriptions)
                await ctx.send(f"❌ Unsubscribed from **{existing_item}**.")
                return

    await ctx.send(f"⚠️ You weren’t subscribed to **{item}**.")

# Command: check what you are subscribed to
@bot.command(name="mylist")
async def list_subs(ctx):
    user_id = str(ctx.author.id)
    items = subscriptions.get(user_id, [])
    if items:
        await ctx.send(f"📦 Your List: {', '.join(items)}")
    else:
        await ctx.send("📭 You’re not subscribed to any items.")

# Command: list of commands
# @bot.command(name="commands")
# async def commandslist(ctx):
#     ctx.send("List of Valid Commands:"
#              "!commands: List of valid commands",
#              "!sub [item name]: Nofity me this item",
#              "!unsub [item name]: Remove notification for this item",
#              "!mylist: List of items you set notification to",
#              "!update: force an update of the current stock")

# Catches invalid commands
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        valid_commands = [command.name for command in bot.commands]
        cmd_list = ", ".join(f"`!{cmd}`" for cmd in valid_commands)
        await ctx.send(f"❌ Invalid command.\n✅ Available commands: {cmd_list}")
    else:
        raise error  # Re-raise other errors so they can be handled normally

# Alerts connections
@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")
    bot.loop.create_task(main())

bot.run(TOKEN)
