from asyncio import tasks
import yt_dlp
import discord
import asyncio
from datetime import timedelta, datetime

class MusicBot:
    def __init__(self, voice_client: discord.VoiceClient, loop: asyncio.AbstractEventLoop, afk_timeout=5):
        self.voice_client = voice_client
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

        self.afk_timeout = afk_timeout
        self.last_played = None
        self.voice_check_loop.start()

    def cog_unload(self):
        self.voice_check_loop.cancel()

    @tasks.loop(seconds=30)
    async def voice_check_loop(self):
        now = datetime.now(datetime.timezone.utc)
        for vc in self.bot.voice_clients:
            if not vc.is_playing() and not vc.is_paused():
                if self.last_played and (now - self.last_played) > timedelta(minutes=self.afk_timeout):
                    await vc.disconnect()
                    print(f"Disconnected due to inactivity: {vc.channel}")
            else:
                self.last_played = now


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

    async def _get_url_from_query(self, query: str) -> str:
        """Return a video URL from a search query using yt_dlp."""
        opts = self.ydl_opts.copy()
        opts["quiet"] = True
        opts["noplaylist"] = True
        opts["default_search"] = "ytsearch1"  # Use YouTube search

        return await self.loop.run_in_executor(None, self._blocking_search, query, opts)
    
    def _blocking_search(self, query, opts):
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if "entries" in info:
                return info["entries"][0]["webpage_url"]
            return info["webpage_url"]


    async def play(self, query: str):
        if not query.startswith("http"):
            try:
                query = await self._get_url_from_query(query)
            except Exception as e:
                print(f"Search failed for query '{query}': {e}")
                return

        try:
            _, title = await self._create_source(query)
        except Exception as e:
            print(f"Failed to extract info for {query}: {e}")
            return

        await self.queue.put((query, title))

        if self.player_task is None or self.player_task.done():
            self.player_task = asyncio.create_task(self._player_loop())

    def skip(self):
        """Skip current song and start next in queue."""
        if self.voice_client.is_playing():
            self.voice_client.stop()  # This triggers after_playing callback, so next song plays

    def stop(self):
        if self.voice_client.is_playing():
            self.voice_client.stop()
        while not self.queue.empty():
            self.queue.get_nowait()
            self.queue.task_done()
        self.current = None

    def pause(self):
        if self.voice_client.is_playing():
            self.voice_client.pause()

    def resume(self):
        if self.voice_client.is_paused():
            self.voice_client.resume()


    def get_queue(self):
        """Return a list of URLs currently in queue."""
        return list(self.queue._queue)

    def get_current(self):
        """Return the title of the currently playing song or None."""
        return self.current
