import os, json, datetime, logging
from extensions.quotes import get_random_quote
from extensions.quote_feedback import send_ratable_quote

logger = logging.getLogger('BobBot')


# MORNING QUOTE: Handle the morning quote
async def morning_quote(bot):
    channel_id = os.getenv("DEFAULT_GENERAL_CHANNEL")
    item = get_random_quote()
    num = item['num']
    quote = item['quote']
    author = item['author']
    context = item['context']
    if context:
        base_content = f'Time for the quote of the day: \n{num}: "{quote}" -{author}\n*[Context: {context}]*'
    else:
        base_content = f'Time for the quote of the day: \n{num}: "{quote}" -{author}'
    await send_ratable_quote(bot.get_channel(channel_id), base_content, bot, num)


# BACKUP QUOTE: Backup quotes every morning
async def backup_quotes(bot):
    date = str(datetime.datetime.now())[:10]
    with open('./files/quotes.json', 'r') as f_read:
        json_obj = json.loads(f_read.read())
    with open(f'./files/backup/quotes_{date}.json', 'w') as f_write:
        f_write.write(json.dumps(json_obj))
    logger.info(f"Backing up quotes for {date}")


# CHECK BIRTHDAYS: Check to see if it is someone's birthday
async def check_birthday(bot):
    channel_id = os.getenv("DEFAULT_GENERAL_CHANNEL")
    currentDate = datetime.datetime.now().strftime("%m/%d/%Y")
    with open('./files/Birthdays.txt', 'r', encoding='utf-8') as f:
        count = 0
        text = f.readlines()
        size = len(text)  # Gets amount of lines from Birthdays.txt file
        f.seek(0)  # Places cursor at beginning of file
        while count <= size:  # while current line is smaller than max lines in file
            tempStr = f.readline()  # set a string to the current line
            if currentDate[:5] == tempStr[:5]:  # if current date (MM/DD) matches the current line
                await bot.get_channel(channel_id).send("Today is " + tempStr[11:(len(tempStr) - 1)] + "'s birthday! :birthday:")
            count = count + 1  # Add to count to eventually leave while loop, or check next line
        f.seek(0)  # Paranoid double checking cursor goes back to beginning. Likely unnecessary
