# Hyperedit

Removes silences from your videos.

## Recommended use

You've recorded some footage with multiple audio tracks but there's a lot of silence and you want to speed up the editing process

## Requirements

- vosk-transcriber
    - `pipx install vosk`
- mplayer
    - Windows: `scoop install mplayer`
    - Mac: `brew install mplayer`
- ffmpeg (ideally with hardware encoding support)
- python

## Roadmap

- Improve performance some more
- Software encoding support
- SRT overrides actually used
- Higher quality rendering options
