import yt_dlp
import discord
import asyncio

class MusicBot:
    def __init__(self, voice_client: discord.VoiceClient, loop: asyncio.AbstractEventLoop):
        self.voice_client = voice_client  # Must be set by the Discord bot when joining voice
        self.loop = loop
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'default_search': 'auto',
            'noplaylist': True,
        }
        self.queue = asyncio.Queue()
        self.play_next_song = asyncio.Event()
        self.current = None
        self.player_task = None

    async def _create_source(self, url: str):
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
            title = info.get('title', 'Unknown Title')

        source = await discord.FFmpegOpusAudio.from_probe(audio_url, method='fallback')
        return source, title

    async def _player_loop(self):
        while True:
            self.play_next_song.clear()
            url, title = await self.queue.get()

            try:
                source, _ = await self._create_source(url)
            except Exception as e:
                print(f"Failed to get source for {url}: {e}")
                self.queue.task_done()
                continue

            def after_playing(error):
                if error:
                    print(f"Player error: {error}")
                self.loop.call_soon_threadsafe(self.play_next_song.set)

            self.voice_client.play(source, after=after_playing)
            self.current = title
            print(f"Now playing: {title}")

            await self.play_next_song.wait()
            self.queue.task_done()
            self.current = None

    async def play(self, url: str):
        try:
            _, title = await self._create_source(url)
        except Exception as e:
            print(f"Failed to extract info for {url}: {e}")
            return

        await self.queue.put((url, title))

        if self.player_task is None or self.player_task.done():
            self.player_task = asyncio.create_task(self._player_loop())

    def skip(self):
        """Skip current song and start next in queue."""
        if self.voice_client.is_playing():
            self.voice_client.stop()  # This triggers after_playing callback, so next song plays

    def get_queue(self):
        """Return a list of URLs currently in queue."""
        return list(self.queue._queue)

    def get_current(self):
        """Return the title of the currently playing song or None."""
        return self.current
