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

In rough priority order

- SRT overrides actually used
    - this may cause problems however if manual editing process has already started. you may need to remove the old ones and re-insert
- Higher quality rendering options
- Selective re-rendering of SRTs
- Batch mode, i.e point at a folder with an options file and just run it
- Excludes file for ignoring selected SRTs
- Overwrite option.
    - After editing in Resolve for example we can replace the files with high quality ones
- Lower quality rendering options
- Improve performance some more
- Software encoding support
