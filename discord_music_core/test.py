import asyncio
# import types
# import discord
from musicbot import MusicBot

class DummyVoiceClient:
    def __init__(self):
        self.is_playing_flag = False

    def play(self, source, *, after=None):
        print("DummyVoiceClient: Playing audio source...")
        self.is_playing_flag = True

        # Simulate playback finishing after 2 seconds
        def done():
            print("DummyVoiceClient: Finished playing.")
            self.is_playing_flag = False
            if after:
                after(None)

        # Schedule 'done' after 2 seconds
        asyncio.get_event_loop().call_later(2, done)

    def is_playing(self):
        return self.is_playing_flag

async def main():
    # Create dummy voice client instance
    dummy_vc = DummyVoiceClient()

    # Create your MusicBot with the dummy voice client
    bot = MusicBot(dummy_vc)

    # Add a song to the queue
    await bot.play("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    await bot.play("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    # Run the player loop for just one song then cancel
    player_task = asyncio.create_task(bot._player_loop())

    # Wait enough time for the song to "play" and finish (simulate 3 seconds)
    await asyncio.sleep(3)

    # Cancel the player loop task to exit cleanly
    player_task.cancel()
    try:
        await player_task
    except asyncio.CancelledError:
        print("Player loop cancelled cleanly.")

if __name__ == "__main__":
    asyncio.run(main())
