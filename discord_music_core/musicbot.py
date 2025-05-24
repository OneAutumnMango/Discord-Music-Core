import yt_dlp
import discord

class MusicBot:
    def __init__(self):
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'default_search': 'auto',
            'noplaylist': True,
        }

    async def play(self, url: str):
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
            title = info.get('title', 'Unknown Title')

        source = await discord.FFmpegOpusAudio.from_probe(audio_url, method='fallback')
        return source, title


if __name__ == "__main__":
    import asyncio

    async def test():
        bot = MusicBot()
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        source, title = await bot.play(url)
        print(f"Got audio source for: {title}")
        print(f"Type: {type(source)}")

    asyncio.run(test())