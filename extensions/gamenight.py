from interactions import Extension, slash_command, SlashContext
import os, time, asyncio, logging, requests

logger = logging.getLogger('BobBot')

# Specifically catered to the creator's gamenights, likely normal users would remove this.
class Gamenight(Extension):

    # GAMENIGHT: A poll specifically created for monday gamenight!
    @slash_command(name="monday_gamenight", description="Create a poll for Monday Game Night")
    async def monday_gamenight_function(self, ctx: SlashContext):
        url = f"https://discord.com/api/v10/channels/{ctx.channel_id}/messages"
        headers = {
            "Authorization": "Bot " + os.getenv("DISCORD_TOKEN"),
            "content-type": "application/json"
        }
        data = {
            "poll": {
                "question": {"text": "Are you coming to Monday Gamenight?"},
                "answers": [
                    {
                        "answer_id": 1,
                        "poll_media": {
                            "text": "Yes",
                            "emoji": None
                        }
                    },
                    {
                        "answer_id": 2,
                        "poll_media": {
                            "text": "No",
                            "emoji": None
                        }
                    },
                ],
                "duration": 48,
                "allow_multiselect": False,
                "layout_type": 1
            },
        }

        match await self.send_request_with_rate_limit(url=url, headers=headers, data=data):
            case 0:
                return await ctx.send(content="Poll created!", ephemeral=True)
            case -1:
                return await ctx.send(content="Rate limit exceeded... Try again later.", ephemeral=True)
            case -2:
                return await ctx.send(content="An unexpected error occurred. Please reach out to the owner of BobBot", ephemeral=True)

    async def send_request_with_rate_limit(self, url, headers, data) -> int:
        # bot.rate_limited replaces the old module-level `rate_limited` global
        if self.bot.rate_limited:
            return -1

        response = requests.post(url=url, headers=headers, json=data)

        # Check if request was successful
        if response.status_code in [200, 201]:
            return 0

        # Handle rate limit response
        if response.status_code == 429:  # HTTP 429 indicates rate limiting
            self.bot.rate_limited = True
            rate_limit_reset = int(response.headers.get("X-RateLimit-Reset", 0))
            current_time = int(time.time())
            wait_time = max(0, rate_limit_reset - current_time)

            logger.warning(f"Rate limited. Waiting {wait_time} seconds...")
            await asyncio.sleep(wait_time)  # Wait for the rate limit reset time
            self.bot.rate_limited = False
            return -1
        else:
            logger.error(f"Request failed with status code:{response.status_code}\n{response.text}")
            return -2


def setup(bot):
    Gamenight(bot)
