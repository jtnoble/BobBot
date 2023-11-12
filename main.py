from interactions import *
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import matplotlib.pyplot as plt
import pandas as pd
import os, random, json, datetime


bot = Client(intents=Intents.DEFAULT)

# ON READY, Print when ready
@listen()
async def on_ready():
    print("Ready")
    print(f"This bot is owned by {bot.owner}")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(morning_quote, trigger='cron', hour=10, minute=0)
    scheduler.add_job(backup_quotes, trigger='cron', hour=10, minute=1)
    scheduler.add_job(check_birthday, trigger='cron', hour=0, minute=0, second=5)
    scheduler.start()

    print('Sending Message to testing chat')
    channel_id = os.getenv("DEFAULT_DEBUG_CHANNEL")
    await bot.get_channel(channel_id).send(f'''
                        Time (CDT): {datetime.datetime.now()}
                        BobBot successfully connected to the channel!
                        ''')
    print('Successfully connected!')
    print('    Time of login: ' + str(datetime.datetime.now()))

# ON CREATE, Send message when a message is received
@listen()
async def on_message_create(event):
    print(event.message.content)

# MORNING QUOTE: Handle the morning quote
async def morning_quote():
    channel_id = os.getenv("DEFAULT_GENERAL_CHANNEL")
    item = get_random_quote()
    num = item['num']
    quote = item['quote']
    author = item['author']
    response = f'{num}: "{quote}" -{author}'
    await bot.get_channel(channel_id).send(response)

# BACKUP QUOTE: Backup quotes every morning
async def backup_quotes():
    date = str(datetime.datetime.now())[:10]
    with open('./files/quotes.json', 'r') as f_read:
        json_obj = json.loads(f_read.read())
    with open(f'./files/backup/quotes_{date}.json', 'w') as f_write:
        f_write.write(json.dumps(json_obj))
    print(f"Backing up quotes for {date}")

# CHECK BIRTHDAYS: Check to see if it is someone's birthday
async def check_birthday():
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

# BIRTHDAYS: Print Birthdays (ephermeral)
@slash_command(name="birthdays", description="Print out everyone's birthdays")
async def birthdays_function(ctx: SlashContext):
    with open("./files/Birthdays.txt") as f:
        data = f.read()
    await ctx.send(data, ephemeral=True)

# QUOTE: Grab a random quote from a quotes.txt
@slash_command(name="quote", description="Print out a random quote!")
@slash_option(
    name="value",
    description="Prints out a quote based on numbers or words.",
    required=False,
    opt_type=OptionType.STRING
)
@slash_option(
    name="author",
    description="Prints out a quote based on author",
    required=False,
    opt_type=OptionType.STRING
)
async def quote_function(ctx: SlashContext, value=None, author=None):
    if author and value:
        items = get_author_quotes(author)
        item = quote_by_value(value, items)
    elif author:
        items = get_author_quotes(author)
        item = get_random_quote(items)
    elif value:
        item = quote_by_value(value)
    else:
        item = get_random_quote()

    print(item)
    if item:
        num = item['num']
        quote = item['quote']
        author = item['author']
        response = f'{num}: "{quote}" -{author}'
        return await ctx.send(content=response)
    return await ctx.send(content="No quote found!")

def get_random_quote(json_obj=None):
    if not json_obj:
        with open('./files/quotes.json', 'r', encoding="utf-8") as f:
            json_obj = json.loads(f.read())
    rng = random.randint(0, len(json_obj)-1)
    return json_obj[rng]
    
def get_author_quotes(author):
    with open('./files/quotes.json', 'r', encoding="utf-8") as f:
        _list = []
        json_obj = json.loads(f.read())
        for item in json_obj:
            if author.lower() == item['author'].lower():
                _list.append(item)
        if _list:
            return _list
        return None

def quote_by_value(value, json_obj=None):
    if not json_obj:
        with open('./files/quotes.json', 'r', encoding="utf-8") as f:
            json_obj = json.loads(f.read())

    if value.isnumeric():
        phraseNum = int(value)
        for item in json_obj:
            if item['num'] == phraseNum:
                return item
    phraseStr = value
    for item in json_obj:
        if phraseStr in item['quote']:
            return item
    return None

# ADD QUOTE: Add a quote to the quote text file
@slash_command(name="add_quote", description="Add a quote to our quotes list.")
@slash_option(
    name="quote",
    description="Quote to be added. No quotations.",
    required=True,
    opt_type=OptionType.STRING
)
@slash_option(
    name="author",
    description="Author for the quote to be added",
    required=True,
    opt_type=OptionType.STRING
)
async def add_quote_function(ctx: SlashContext, quote: str, author: str):
    with open('./files/quotes.json', 'r') as f_read:
        json_obj = json.loads(f_read.read())
    new_quote = {
        "num": len(json_obj)+1,
        "quote": quote,
        "author": author.title()
    }
    json_obj.append(new_quote)
    with open('./files/quotes.json', 'w') as f_write:
        f_write.write(json.dumps(json_obj))
    await ctx.send("Quote added!")

# DELETE QUOTE: Delete a quote from the quote text file
@slash_command(name="delete_quote", description="Delete a quote from our quotes list.")
@slash_option(
    name="quote_to_delete",
    description="Quote to be deleted. Must match entire quote correctly",
    required=True,
    opt_type=OptionType.STRING
)
async def delete_quote_function(ctx: SlashContext, quote_to_delete: str):
    if len(quote_to_delete) >= 3:
        with open('./files/quotes.json', 'r') as f_read:
            json_obj = json.loads(f_read.read())
        beforelines = len(json_obj)
        for i, item in enumerate(json_obj):
            if quote_to_delete == item['quote']:
                json_obj.pop(i)
                break
        afterlines = len(json_obj)
        if afterlines < beforelines:
            with open('./files/quotes.json', 'w') as f_write:
                f_write.write(json.dumps(json_obj))
            return await ctx.send(content="Quote deleted!", ephemeral=True)
    return await ctx.send(content="Quote not found!", ephemeral=True)

# QUOTE COUNT: Get the count of quotes!
@slash_command(name='quote_leaderboard', description="Leaderboard for quotes!")
async def quote_leaderboard_function(ctx: SlashContext):
    df = pd.read_json('./files/quotes.json')
    author_counts = df['author'].value_counts().reset_index()
    author_counts.columns = ['author', 'count']
    df = df.merge(author_counts, on='author')
    df.rename(columns={'num': 'quotes'}, inplace=True)
    df['quotes'] = df['count']
    df = df.drop(columns=['count', 'quote'])
    df = df.drop_duplicates(subset='author', keep='first')
    df = df[df['quotes'] >= 5]
    df = df.sort_values(by='quotes', ascending=False)
    df = df[['author', 'quotes']]

    plt.figure(figsize=(10, 6))
    plt.bar(df['author'], df['quotes'])
    plt.xlabel('Author')
    plt.ylabel('Number of Quotes')
    plt.title('Number of Quotes by Author')
    plt.xticks(rotation=90)

    for index, value in enumerate(df['quotes']):
        plt.text(index, value, str(value), ha='center', va='bottom')

    plt.savefig('./files/chart.png', format='png', bbox_inches='tight')

    return await ctx.send(file='./files/chart.png')

# HEADS OR TAILS: Click a button for heads or tails
heads_tails_btn = Button(
    custom_id="heads_tails_btn",
    style=ButtonStyle.BLUE,
    label="Flip Coin",
    disabled=False
)
@slash_command(name="coin_toss", description="Toss a coin, heads or tails?")
async def coin_toss_function(ctx: SlashContext):
    await ctx.send("Heads or tails?", components=heads_tails_btn)
@component_callback("heads_tails_btn")
async def coin_toss_callback(ctx: ComponentContext):
    result = ""
    if random.randint(0,1) == 0:
        result = "Heads"
    else:
        result = "Tails"
    heads_tails_btn.disabled = True
    heads_tails_btn.label = result
    await ctx.edit_origin(components=heads_tails_btn)

# POLL: Create a poll based on a question and defined choices
@slash_command(name="poll", description="create a poll")
@slash_option(
    name="question",
    description="What is the poll question?",
    required=True,
    opt_type=OptionType.STRING,
)
@slash_option(
    name="choices",
    description="Separate options by commas with NO spaces (e.g., Cosmic Encounter,Nemesis,Clank)",
    required=True,
    opt_type=OptionType.STRING,
)
async def poll_function(ctx: SlashContext, question: str, choices: str):
    options = choices.split(",")
    poll_component = StringSelectMenu(
        options,
        custom_id="poll_id",
        min_values=1,
    )
    msg = question
    for option in options:
        msg += f'\n{option}:'
    await ctx.send(content=msg, components=poll_component)
@component_callback("poll_id")
async def poll_callback(ctx: ComponentContext):
    msg = ctx.message.content
    if not str(ctx.member) in msg:
        selected = ctx.values[0]
        msg = msg.split("\n")
        for i, line in enumerate(msg):
            if i == 0:
                continue
            if line.startswith(selected+":"):
                msg[i] += (f" {ctx.member}")
                break
        msg = "\n".join(msg)
        await ctx.edit_origin(content=msg)
    else:
        await ctx.send("You can't vote twice dummy!", ephemeral=True)

# GAME NIGHT: Yes or No for Game Night
yes_button = Button(
    label="Yes",
    custom_id="yes_button",
    style=ButtonStyle.SUCCESS
)
no_button = Button(
    label="No",
    custom_id="no_button",
    style=ButtonStyle.DANGER
)
@slash_command(name="gamenight", description="Who's coming to game night?")
async def gamenight_function(ctx: SlashContext):
    await ctx.send(content="Are you coming to game night?\nGoing:\nNot Going:", components=[yes_button, no_button])
@component_callback("yes_button")
async def yes_callback(ctx: ComponentContext):
    msg = await gamenight_function_handler(True, ctx)
    await ctx.edit_origin(content=msg)
@component_callback("no_button")
async def no_callback(ctx: ComponentContext):
    msg = await gamenight_function_handler(False, ctx)
    await ctx.edit_origin(content=msg)
async def gamenight_function_handler(yes_no, ctx: ComponentContext):
    msg = ctx.message.content
    if ctx.author.display_name in msg:
        msg = msg.replace(f"\n- {ctx.author.display_name}", "")
    if yes_no:
        msg = msg.replace("\nGoing:", f"\nGoing:\n- {ctx.author.display_name}")
    elif not yes_no:
        msg = msg.replace("\nNot Going:", f"\nNot Going:\n- {ctx.author.display_name}")
    return msg

# JOEL: The spinning fish
@slash_command(name="joel", description="fish_spin.gif")
@slash_option(
    name="speed",
    description="[0-3] Is he fast? is he slow? I don't know...",
    required=False,
    opt_type=OptionType.INTEGER,
)
async def joel_function(ctx: SlashContext, speed: int = 1):
    file = "./files/joel-spin-1.gif"
    if speed == 2:
        file = "./files/joel-spin-2.gif"
    elif speed == 3 :
        file = "./files/joel-spin-3.gif"
    elif speed == 0 :
        file = "./files/joel-spin-0.gif"
    await ctx.send(file=file)

# MAGIC 8 BALL: Just a magic 8 ball
eight_ball_button = Button(
    style=ButtonStyle.PRIMARY,
    label="8 Ball",
    custom_id="8ballbutton"
)
@slash_command(name="magic_8_ball", description="Ask the magic 8 ball")
async def magic_8_ball_function(ctx: SlashContext):
    await ctx.send(content="Click the button!", components=eight_ball_button)
@component_callback("8ballbutton")
async def eight_ball_button_response(ctx: ComponentContext):
    ballChoices = ["It is certain.", "It is decidedly so.", "Without a doubt.", "Yes - definitely!",
        "You may rely on it.",
        "As I see it, yes.", "Most likely.", "Outlook good.", "Signs point to yes.", "Reply hazy, try again",
        "Ask again later.", "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.",
        "Don't count on it.", "My reply is no.", "My sources say no.", "Outlook not so good.",
        "Very doubtful."]
    randChoice = random.choice(ballChoices)
    await ctx.edit_origin(content=randChoice, components=eight_ball_button)

# HEY: Annoyingly @ a friend with their custom gif based on the hey.json file
@slash_command(name="hey", description="Phone a friend")
@slash_option(
    name="friend",
    description="@ a friend",
    required=True,
    opt_type=OptionType.USER
)
async def hey_function(ctx: SlashContext, friend: User):
    with open("./files/hey.json", "r") as jsf:
        _json = json.load(jsf)
        for user in _json["users"]:
            for name in user:
                if str(friend.id) == user.get(name)[0]["id"]:
                    try:
                        return await ctx.send(content=friend.mention, file="./files/"+user.get(name)[1]["image"])
                    except:
                        return await(ctx.send("There was an issue...", ephemeral=True))
    return await ctx.send("User not found D:", ephemeral=True)

# Start bot
load_dotenv()
bot.start(os.getenv("DISCORD_TOKEN"))