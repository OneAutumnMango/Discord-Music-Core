# Discord Music Core

Python-based core module for a Discord music bot that supports playing audio from YouTube, queue management, and playback control.

---

## Features

- Play audio from URLs or search queries (YouTube or other platforms supported by `yt_dlp`)
- Async queue management for songs
- Skip, pause, resume, and stop playback controls
- Automatically plays queued songs one after another
- Retrieves currently playing song info and queued songs

---

## Requirements

- Python 3.7+
- `discord.py`
- `yt_dlp`
- `FFmpeg` installed and accessible in your system PATH

---

## Installation

```bash
pip install git+https://github.com/OneAutumnMango/Discord-Music-Core.git
```

Make sure FFmpeg is installed

- On Linux/macOS: install via your package manager (`apt`, `brew`, etc.)
- On Windows: download from [ffmpeg.org](https://ffmpeg.org/) and add to PATH

---

## Usage Example

A usage example can be found in my Discord bot music cog linked [here](https://github.com/OneAutumnMango/Discord-Bot/blob/main/cogs/music.py)


---

## API Overview

### `MusicBot(voice_client: discord.VoiceClient, loop: asyncio.AbstractEventLoop, afk_timeout: int)`

Create a music bot instance tied to a Discord voice client with configurable afk_timeout

### `async play(query: str)`

Add a song to the queue, accepts URLs or search queries.

### `skip()`

Skip the currently playing song.

### `stop()`

Stop playback and clear the queue.

### `pause()`

Pause playback.

### `resume()`

Resume paused playback.

### `get_queue() -> list`

Returns list of queued (url, title) tuples.

### `get_current() -> Optional[str]`

Returns the title of the currently playing song or `None`.

