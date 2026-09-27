from interactions import Extension, listen, Embed, Timestamp
from interactions.api.events.discord import VoiceStateUpdate
import datetime

# Below is for voice channel join notifications.

class VoiceNotify(Extension):

    async def send_join_notification(self, member):
        """Sends a notification when a user joins."""
        embed = Embed(
            title="Voice Chat Started!",
            description=f"{member} has started a voice chat!",
            timestamp=Timestamp.now(),
            color=0x00FF00,  # Green color
        )
        await self.bot.get_channel(self.bot.DEFAULT_VOICE_NOTIF_CHANNEL).send(embeds=embed)

    async def clear_channel_timer(self, channel_id):
        """Clears the timer for a voice channel."""
        if channel_id in self.bot.voice_channel_timers:
            del self.bot.voice_channel_timers[channel_id]

    @listen(VoiceStateUpdate)
    async def on_voice_state_update(self, event: VoiceStateUpdate):
        """
        Listens for voice state updates and sends a notification when a user joins the target voice channel,
        with a 5-minute buffer.
        """
        before: "VoiceState" = event.before
        after: "VoiceState" = event.after

        if after and str(after.channel.id) == self.bot.DEFAULT_VOICE_CHANNEL:
            if not before or (before.channel and len(before.channel.voice_members) == 0):
                if len(after.channel.voice_members) == 1:
                    # Channel was empty and now has one user
                    last_vc_time = self.bot.voice_channel_timers.get(after.channel.id)
                    if last_vc_time:
                        now = datetime.datetime.now()
                        diff = now - last_vc_time
                        if diff.seconds > 300:
                            await self.send_join_notification(after.member)  # 5 minutes
                    else:
                        await self.send_join_notification(after.member)  # Should always alert if VC never existed, new VC entry
                    self.bot.voice_channel_timers[after.channel.id] = datetime.datetime.now()  # Always update time in dict

        # Reset timer when all users have left
        if before and str(before.channel.id) == self.bot.DEFAULT_VOICE_CHANNEL:
            if len(before.channel.voice_members) == 1:
                if self.bot.voice_channel_timers.get(before.channel.id):
                    self.bot.voice_channel_timers[before.channel.id] = datetime.datetime.now()


def setup(bot):
    VoiceNotify(bot)
