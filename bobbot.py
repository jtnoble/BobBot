from interactions import *
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os, logging, datetime

DEBUG = False

# Logging configured before any extensions load
logging.basicConfig(filename="./files/bob_logs",
                filemode='a',
                format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                datefmt='%H:%M:%S',
                level=logging.INFO)
logger = logging.getLogger('BobBot')

load_dotenv()

intents = Intents.DEFAULT | Intents.GUILD_VOICE_STATES
bot = Client(intents=intents)

bot.scheduler_running = False   # For if the program reconnects without restarting, no duplicate schedules.
bot.rate_limited = False        # For if we're in a rate limit specifically with HTTP Requests
bot.voice_channel_timers = {}   # Keeps track of timers
bot.active_voice_channels = {}  # Keeps track of voice channel activity
bot.DEFAULT_VOICE_CHANNEL = os.getenv("DEFAULT_VOICE_CHANNEL")
bot.DEFAULT_VOICE_NOTIF_CHANNEL = os.getenv("DEFAULT_VOICE_NOTIF_CHANNEL")

# Import scheduled jobs directly instead of as an extension; they aren't slash commands
from extensions.scheduled_tasks import morning_quote, backup_quotes, check_birthday

bot.load_extension("extensions.quotes")
bot.load_extension("extensions.fun")
bot.load_extension("extensions.gamenight")
bot.load_extension("extensions.voice_notify")


# ON READY, Print when ready
@listen()
async def on_ready():
    logger.info("Ready")
    logger.info(f"This bot is owned by {bot.owner}")

    logger.info('Sending Message to testing chat')
    channel_id = os.getenv("DEFAULT_DEBUG_CHANNEL")

    print(f"Connected to channel at {datetime.datetime.now()}")
    if not bot.scheduler_running:
        scheduler = AsyncIOScheduler()
        scheduler.add_job(morning_quote, trigger='cron', hour=10, minute=0, args=[bot])
        scheduler.add_job(backup_quotes, trigger='cron', hour=10, minute=1, args=[bot])
        scheduler.add_job(check_birthday, trigger='cron', hour=0, minute=0, second=5, args=[bot])
        scheduler.start()
        logger.info("Scheduler Started!")
        await bot.get_channel(channel_id).send(f'''
                        Time (CDT): {datetime.datetime.now()}
                        BobBot successfully connected to the channel!
                        ''')
        bot.scheduler_running = True
    else:
        logger.warning("BobBot reconnected to the channel!")
        await bot.get_channel(channel_id).send(f'''
                        Time (CDT): {datetime.datetime.now()}
                        BobBot reconnected to the channel!
                        ''')

    logger.info('Successfully connected!')

    if DEBUG:
        await bot.synchronise_interactions(delete_commands=True)


if __name__ == '__main__':
    bot.start(os.getenv("DISCORD_TOKEN"))
