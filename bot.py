import os
import discord
from discord.ext import commands
import asyncio
from dotenv import load_dotenv
from datetime import datetime, timedelta
# from other files
from scrapping import scrape_garden_stock  # make sure this function returns inventory list



# token/apis
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))


# Set up bot with command prefix
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


# check every irl 5 min interval
async def wait_until_next_5_minute_mark():
    # find current time stamp
    now = datetime.now()
    minutes_to_wait = 5 - (now.minute % 5) # irl 5 min interval
    next_time = now + timedelta(minutes=minutes_to_wait)
    next_time = next_time.replace(second=30, microsecond=0)
    await asyncio.sleep((next_time - now).total_seconds())


# Action sends update to discord channel
async def send_stock_update(channel):
    #await asyncio.sleep(30)  # hardcode wait 30s for website to update
    stock = await scrape_garden_stock() # scrape
    #error handle
    if not stock:
        await channel.send("⚠️ Failed to fetch stock data.")
        return

    msg = "**🌱 GrowAGarden Stock Update 🌱**\n"

    # add to msg
    for category, items in stock.items():
        msg += f"\n__**{category}**__\n"
        for name, qty in items:
            msg += f"{name}: {qty}\n"

    #send to chan
    await channel.send(msg)


# Loop every 5 min
async def periodic_stock_task():
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)
    while True:
        await send_stock_update(channel)
        await wait_until_next_5_minute_mark()


# Manual command: !update
@bot.command(name="update")
async def force_update(ctx):
    if ctx.channel.id != CHANNEL_ID:
        return
    await ctx.send("🔄 Forcing a stock update...")
    await send_stock_update(ctx.channel)

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")
    bot.loop.create_task(periodic_stock_task())

bot.run(TOKEN)
