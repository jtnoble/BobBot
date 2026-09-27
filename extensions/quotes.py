from interactions import Extension, slash_command, slash_option, OptionType, SlashContext
from interactions import Button, ButtonStyle, ComponentContext, component_callback
from interactions import Modal, ShortText, ParagraphText, ModalContext
from extensions.quote_feedback import send_ratable_quote
import matplotlib.pyplot as plt
import pandas as pd
import json, string, random, logging

logger = logging.getLogger('BobBot')

# Button handler for quote count
quote_count_send_quotes_btn = Button(
    custom_id="view_quotes",
    style=ButtonStyle.BLUE,
    label="View Quotes!",
    disabled=False
)


# Helper functions
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
    # First pass
    for item in json_obj:
        if phraseStr in item['quote']:
            return item
    # Second pass - Not found, maybe because punctuation
    phraseStr_lower_no_punc = value.lower()
    phraseStr_lower_no_punc = phraseStr_lower_no_punc.translate(str.maketrans('', '', string.punctuation))
    for item in json_obj:
        temp_item = item['quote'].lower()
        temp_item = temp_item.translate(str.maketrans('', '', string.punctuation))
        if phraseStr_lower_no_punc in temp_item:
            return item
    return None

def add_quote_function(quote: str, author: str, context: str = None):
    with open('./files/quotes.json', 'r') as f_read:
        json_obj = json.loads(f_read.read())
    new_quote = {
        "num": len(json_obj)+1,
        "quote": quote,
        "author": author.title(),
        "context": context if context else "",
        "ratings": {}
    }
    json_obj.append(new_quote)
    with open('./files/quotes.json', 'w') as f_write:
        f_write.write(json.dumps(json_obj))

async def generate_quote_html():
    with open('./files/quotes.json', 'r', encoding='utf-8') as jsf:
        json_file = json.load(jsf)
    additional_html = []
    for entry in json_file:
        curr = f"<li>{entry['quote']} <i>Context: {entry['context']}</i> -{entry['author']}</li>"
        additional_html.append(curr)

    quotes_html = '\n'.join(additional_html)

    html_template = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BobBot Quotes!</title>
    </head>
    <body>
        <h1>BobBot Quotes!</h1>
        <ol>
            {quotes_html}
        </ol>
    </body>
    </html>
    '''
    with open('./files/BobBotQuotes.html', 'w', encoding='utf-8') as f:
        f.write(html_template)


class Quotes(Extension):

    # BIRTHDAYS: Print Birthdays (ephemeral)
    @slash_command(name="birthdays", description="Print out everyone's birthdays")
    async def birthdays_function(self, ctx: SlashContext):
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
    async def quote_function(self, ctx: SlashContext, value=None, author=None):
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

        if item:
            num = item['num']
            quote = item['quote']
            author = item['author']
            context = item['context']

            if context:
                base_content = f'{num}: "{quote}" -{author}\n*[Context: {context}]*'
            else:
                base_content = f'{num}: "{quote}" -{author}'
            logger.info(f'{ctx.author} asked for quote {num}')
            return await send_ratable_quote(ctx, base_content, self.bot, num)
        return await ctx.send(content="No quote found!")

    # ADD QUOTE: Add a quote to the quote text file
    @slash_command(name="add_quote", description="Add a quote to our quotes list.")
    async def add_quote_modal(self, ctx: SlashContext):
        quote_modal = Modal(
            ShortText(label="Author", custom_id="added_author"),
            ParagraphText(label="Quote", custom_id="added_quote"),
            ParagraphText(label="Context", custom_id="added_context", required=False),
            title="Add A Quote",
            custom_id="quote_modal",
        )
        await ctx.send_modal(modal=quote_modal)
        modal_ctx: ModalContext = await ctx.bot.wait_for_modal(quote_modal)

        # extract the answers from the responses dictionary
        author_text = modal_ctx.responses["added_author"]
        quote_text = modal_ctx.responses["added_quote"]
        context_text = modal_ctx.responses["added_context"]

        if context_text:
            msg = f"Added Quote: \n{quote_text} -{author_text}\nContext: {context_text}"
        else:
            msg = f"Added Quote: \n{quote_text} -{author_text}"

        try:
            add_quote_function(quote_text, author_text, context_text)
            await modal_ctx.send(msg, ephemeral=False)
            logger.info(f'{ctx.author} added the following quote: {quote_text} -{author_text}')
        except:
            await modal_ctx.send("There was an error adding your quote...", ephemeral=True)
            logger.error("Quote add failure")

    # DELETE QUOTE: Delete a quote from the quote text file
    @slash_command(name="delete_quote", description="Delete a quote from our quotes list.")
    @slash_option(
        name="quote_to_delete",
        description="Quote to be deleted. Must match entire quote correctly",
        required=True,
        opt_type=OptionType.STRING
    )
    async def delete_quote_function(self, ctx: SlashContext, quote_to_delete: str):
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
    async def quote_leaderboard_function(self, ctx: SlashContext):
        df = pd.read_json('./files/quotes.json')
        total_quotes = df.iloc[-1]['num']
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

        plt.savefig('./files/BobBotQuotesChart.png', format='png', bbox_inches='tight')

        return await ctx.send(content=f"Total Quotes: {total_quotes}", file='./files/BobBotQuotesChart.png', components=[quote_count_send_quotes_btn])

    @component_callback("view_quotes")
    async def quote_leaderboard_view_quotes_callback(self, ctx: ComponentContext):
        await generate_quote_html()
        return await ctx.send(content="Download and open this html file to view quotes!", file='./files/BobBotQuotes.html', ephemeral=True)


def setup(bot):
    Quotes(bot)
