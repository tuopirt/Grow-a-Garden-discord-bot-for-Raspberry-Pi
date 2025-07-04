# Agrobot 🌱 - Discord Stock Monitor Bot for Grow-a-Garden

Agrobot is a lightweight Discord bot that scrapes live stock data from the *Grow-a-Garden* game on [VulcanValues](https://www.vulcanvalues.com/grow-a-garden/stock) and posts it to a designated Discord channel at regular intervals.

Built for Raspberry Pi using Python and Playwright-compatible tools.

---

## Project Structure

discord-bot/
│
├── bot.py # Main bot logic and Discord client
├── scrapping.py # Scrapes stock data from the website
├── requirements.txt # Python dependencies
├── venv/ # Python virtual environment
└── README.md # You're reading it


---

## Dependencies

Install via `pip install -r requirements.txt` inside the virtual environment.

| Library         | Purpose                                                                 |
|----------------|-------------------------------------------------------------------------|
| `discord.py`   | Interacts with the Discord API. Sends messages to channels.             |
| `pyppeteer`    | Controls a headless browser (Chromium) to scrape dynamic web content.   |
| `beautifulsoup4` | Parses the HTML content returned by Pyppeteer.                         |
| `asyncio`      | Enables concurrent tasks (like periodic scraping) with async functions. |
| `collections`  | `defaultdict` used to group and organize scraped data.                  |

---

## Setup (First Time Only)

1. **Install Chromium on your Raspberry Pi**  
   ```bash
   sudo apt update
   sudo apt install chromium-browser
Clone your bot and set up Python virtual environment

Then,
Create a .env file or hardcode your Discord bot token inside bot.py:

TOKEN = 'your-token-here'

For your discord bot api and discord channel ID


Then run:

source venv/bin/activate
python bot.py

To test/Run the bot,
You should see the bot come online and post stock data.



HOW TO: Running Continuously in Background (Recommended)
Use systemd to run the bot on startup:

Create the service file:

sudo nano /etc/systemd/system/discordbot.service

Paste the following (update /home/pi/discord-bot if needed):

[Unit]
Description=Discord Stock Bot
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/discord-bot
ExecStart=/home/pi/discord-bot/venv/bin/python /home/pi/discord-bot/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
Enable and start:

sudo systemctl daemon-reload
sudo systemctl enable discordbot
sudo systemctl start discordbot

View logs:

journalctl -u discordbot -f



Bot Behavior
Scrapes https://www.vulcanvalues.com/grow-a-garden/stock

Groups stock items under categories (e.g. seeds, tools, etc.)

Sends formatted message to your Discord channel

Automatically repeats every X minutes (configured in bot.py)



Notes
Make sure the Pi is connected to the internet

Chromium may use more memory than usual on a Pi; ensure you’re not overloaded

The site must remain available and unchanged in structure for scraping to work

UPDATES:
- added command feature to ping for certain items
- !sub [item name]: Nofity me this item,
  !unsub [item name]: Remove notification for this item,
  !mylist: List of items you set notification to,
  !update: force an update of the current stock

- Keep track of prev update list so it doesn't ping user if item on list every 5 min



by Harrison "tuopirt" Zhou
contact: harryzhou.ca@gmail.com
---
