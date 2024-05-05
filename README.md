# BobBot

BobBot Version 3, now in a real repository for once!

### Why did you make this?

It all starts with the /birthdays command. We have two friends in our friend group who share birthdays one day after the other. One year, we all wished the one a happy birthday, but completely forgot it was the other's birthday the previous day. I decided to make a bot that would check every day and notify us if it was someone's birthday, so we never forgot again. The rest were ideas thrown at me by other people in my discord group!

### What does it do?

This uses a mixture of auto-scheduling and slash commands to create a fun experience for your server

#### Slash Commands

List of slash commands usable

##### Quotes

Print out a random quote, or one based on a value/author

- /quote: Prints out an entirely random quote based on `quotes.json`
- /quote value: Prints out the FIRST quote that contains a specific value
- /quote author: Prints out a RANDOM quote by that author
- /quote value author: Prints out the FIRST quote by a specific author
- `quotes.json` follows this format:
- [{"num": 1, "author": "John", "quote": "Lorem Ipsum"}, {"num": 2, "author": "Jane", "quote": "Another Lorem Ipsum"}]

##### Birthdays

Show you everyone's birthdays so you don't forget!

- Utilize Birthdays.txt file to print out the list of birthdays
- Birthdays.txt must follow the format:
  - MM/DD/YYYY Person's_Name
  - MM/DD/YYYY Person's_Name_2

##### Coin Flip

Heads or Tails, or any other 50/50 decision making

- Posts a button to flip a coin.
- Coin can be flipped multiple times. Use wisely.

##### Magic 8 Ball

The Magic 8 Ball knows all!

- Posts a button to roll the magic 8 ball.
- Stats: 50% Yes, 25% No, 25% Try Again.

##### "Hey"

Annoyingly @ your friend.

- Instead of a normal @ for a friend, "hey" just sends a specialized image when you @ your friend, making tagging them just a little more fun and interesting.
- `hey.json` is setup as such:
- {"users": [{"Name":[{"id": "discord_user_id_as_string" },{ "image": "link_to_image.gif" }]},{"Name2": [{"id": "discord_user_id_as_string" },{ "image": "link_to_image.png" }]},]}

##### "Monday Gamenight"

Ask the group if they're coming to game night.

- Automatically creates a poll via HTTP API (because slash commands don't support it yet).
- Poll is set for 48 hours default, and asks simply if anyone is coming to monday gamenight.

##### joel

Spinning fish

- Joel is a meme of a fish spinning... That's really it
- _Note, you may need to remove this command as I will not be uploading the joel-spin files to this repo_

#### Scheduled Commands

Commands that are scheduled to run every so often

##### Check Birthdays

Checks the Birthdays.txt file at midnight to see if it's someone's birthday

- If at 12:00:05AM, it is someone's birthday, send a message stating this

##### Morning Quote

Start your day out with a quote of the day!

- At 10:00:00AM every day, run the same function as /quote above to get a random quote

##### Backup Quotes

Backup your quotes data!

- Every day, backup the `quotes.json` file. Accidents happen, and we don't want to lose our precious quotes.

### Discord Interactions API

API Version 5.10: https://interactions-py.github.io/interactions.py/

### Installation

- Create a `.env` file with the following parameters
  - DISCORD_TOKEN=<your_api_token>
  - DEFAULT_GENERAL_CHANNEL=<general_channel>
    - Quote of the day will go to this channel
  - DEFAULT_DEBUG_CHANNEL=<debug_channel>
    - The on_ready message goes to this channel
- Create a "files" folder, and fill it with the following files:
  - `hey.json`
  - `quotes.json`
  - `Birthdays.txt`
- Install dependencies via pip (will try to have a requirements.txt file)
  - Python3.10+
  - `pip install -r requirements.txt`
- _Other Notes_
  - I made the decision to not upload any files within the files folder, so things like "joel-spin" do not exist. You are free to delete these slash commands in your own usecase.

### Running

- Run locally on machine with `python3 main.py`

### Credits

- Jtnoble
