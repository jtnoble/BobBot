from interactions import Extension, slash_command, slash_option, OptionType, SlashContext
from interactions import Button, ButtonStyle, ComponentContext, component_callback, User
import random, json

# HEADS OR TAILS: Click a button for heads or tails
heads_tails_btn = Button(
    custom_id="heads_tails_btn",
    style=ButtonStyle.BLUE,
    label="Flip Coin",
    disabled=False
)

# MAGIC 8 BALL: Just a magic 8 ball
eight_ball_button = Button(
    style=ButtonStyle.PRIMARY,
    label="8 Ball",
    custom_id="8ballbutton"
)


class Fun(Extension):

    @slash_command(name="coin_toss", description="Toss a coin, heads or tails?")
    async def coin_toss_function(self, ctx: SlashContext):
        await ctx.send("Heads or tails?", components=heads_tails_btn)

    @component_callback("heads_tails_btn")
    async def coin_toss_callback(self, ctx: ComponentContext):
        result = ""
        if random.randint(0, 1) == 0:
            result = "Heads"
        else:
            result = "Tails"
        heads_tails_btn.disabled = True
        heads_tails_btn.label = result
        await ctx.edit_origin(components=heads_tails_btn)

    # JOEL: The spinning fish
    @slash_command(name="joel", description="fish_spin.gif")
    @slash_option(
        name="speed",
        description="[0-3] Is he fast? is he slow? I don't know...",
        required=False,
        opt_type=OptionType.INTEGER,
    )
    async def joel_function(self, ctx: SlashContext, speed: int = 1):
        file = "./files/joel-spin-1.gif"
        if speed == 2:
            file = "./files/joel-spin-2.gif"
        elif speed == 3:
            file = "./files/joel-spin-3.gif"
        elif speed == 0:
            file = "./files/joel-spin-0.gif"
        await ctx.send(file=file)

    @slash_command(name="magic_8_ball", description="Ask the magic 8 ball")
    async def magic_8_ball_function(self, ctx: SlashContext):
        await ctx.send(content="Click the button!", components=eight_ball_button)

    @component_callback("8ballbutton")
    async def eight_ball_button_response(self, ctx: ComponentContext):
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
    async def hey_function(self, ctx: SlashContext, friend: User):
        with open("./files/hey.json", "r") as jsf:
            _json = json.load(jsf)
            for user in _json["users"]:
                for name in user:
                    if str(friend.id) == user.get(name)[0]["id"]:
                        try:
                            return await ctx.send(content=friend.mention, file="./files/"+user.get(name)[1]["image"])
                        except:
                            return await ctx.send("There was an issue...", ephemeral=True)
        return await ctx.send("User not found D:", ephemeral=True)


def setup(bot):
    Fun(bot)
