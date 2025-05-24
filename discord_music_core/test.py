import asyncio
# import types
# import discord
from musicbot import MusicBot

class DummyVoiceClient:
    def __init__(self):
        self.is_playing_flag = False
        self._after = None  # store after callback for stop()

    def play(self, source, *, after=None):
        print("DummyVoiceClient: Playing audio source...")
        self.is_playing_flag = True
        self._after = after

        def done():
            print("DummyVoiceClient: Finished playing.")
            self.is_playing_flag = False
            if self._after:
                self._after(None)

        # Schedule 'done' after 2 seconds
        asyncio.get_event_loop().call_later(2, done)

    def stop(self):
        if self.is_playing_flag:
            print("DummyVoiceClient: Stopping playback early.")
            self.is_playing_flag = False
            if self._after:
                self._after(None)

    def is_playing(self):
        return self.is_playing_flag


async def main():
    dummy_vc = DummyVoiceClient()
    bot = MusicBot(dummy_vc)

    # Add two songs to the queue
    await bot.play("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    await bot.play("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    await bot.play("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    await bot.play("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    # Start player loop task
    player_task = asyncio.create_task(bot._player_loop())

    # Wait a moment to let first song start playing
    await asyncio.sleep(1)

    # Print current playing song
    print(f"Currently playing: {bot.get_current()}")

    # Print the queue URLs
    print("Queue contents:")
    for url in bot.get_queue():
        print(f" - {url}")

    # Test skip function to skip current song early
    print("Skipping current song...")
    bot.skip()

    # Wait enough time for second song to play fully (simulate 3 seconds)
    await asyncio.sleep(3)

    # Cancel player loop task cleanly
    player_task.cancel()
    try:
        await player_task
    except asyncio.CancelledError:
        print("Player loop cancelled cleanly.")

if __name__ == "__main__":
    asyncio.run(main())
