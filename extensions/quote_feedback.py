from interactions import Extension, StringSelectMenu, StringSelectOption, ComponentContext, component_callback
import json

QUOTES_PATH = './files/quotes.json'

# 1-5 star rating for quotes
rating_select = StringSelectMenu(
    StringSelectOption(label="⭐ 1", value="1"),
    StringSelectOption(label="⭐⭐ 2", value="2"),
    StringSelectOption(label="⭐⭐⭐ 3", value="3"),
    StringSelectOption(label="⭐⭐⭐⭐ 4", value="4"),
    StringSelectOption(label="⭐⭐⭐⭐⭐ 5", value="5"),
    custom_id="quote_rating_select",
    placeholder="Rate this quote!"
)


def format_rating_line(ratings: dict) -> str:
    if not ratings:
        return "Rating: No ratings yet"
    values = list(ratings.values())
    average = sum(values) / len(values)
    rounded = round(average, 2)
    display = f"{rounded:g}"  # trims trailing zeros so e.g. 4.0 shows as "4"
    vote_count = len(values)
    return f"Rating: {display}⭐ ({vote_count} vote{'s' if vote_count != 1 else ''})"


def _load_quotes():
    with open(QUOTES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def _save_quotes(json_obj):
    with open(QUOTES_PATH, 'w', encoding='utf-8') as f:
        f.write(json.dumps(json_obj))


def _find_quote(json_obj, num):
    return next((q for q in json_obj if q['num'] == num), None)


async def send_ratable_quote(destination, base_content: str, bot, num: int):
    json_obj = _load_quotes()
    item = _find_quote(json_obj, num)
    ratings = item.get('ratings', {}) if item else {}

    content = f"{base_content}\n{format_rating_line(ratings)}"
    message = await destination.send(content=content, components=rating_select)
    bot.quote_ratings[message.id] = {"base_content": base_content, "num": num}
    return message


class QuoteFeedback(Extension):

    @component_callback("quote_rating_select")
    async def quote_rating_select_callback(self, ctx: ComponentContext):
        record = self.bot.quote_ratings.get(ctx.message.id)

        if record is None:
            # Bot restarted since this message was sent, no longer tracked
            return await ctx.send(
                "This quote is unable to be voted on at this time. Try voting next time it shows up!",
                ephemeral=True
            )

        json_obj = _load_quotes()
        item = _find_quote(json_obj, record['num'])
        if item is None:
            return await ctx.send("Couldn't find that quote in quotes.json anymore.", ephemeral=True)

        ratings = item.setdefault('ratings', {})
        ratings[str(ctx.author.id)] = int(ctx.values[0])  # overwrites a prior vote, letting users change their rating
        _save_quotes(json_obj)

        new_content = f"{record['base_content']}\n{format_rating_line(ratings)}"
        await ctx.edit_origin(content=new_content, components=rating_select)


def setup(bot):
    QuoteFeedback(bot)
