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

## Basic usage

1. Confirm which tracks contain voice audio only. Note that VLC uses 1-indexes but this application and ffmpeg use 0-indexes.
    - Run `1_extract_dialog.py -t 1 2` (where 1 and 2 are the 0-indexed audio tracks containing voice) and this will merge those tracks into a WAV file in the same directory as the video.
2. Run `2_transcribe.py` which will generate an SRT (subtitle) file of the audio
3. Run `deaggress.py` to merge SRTs if you prefer to avoid stylistic hard cutting or want fewer clips to review
4. Run `4_split_video.py` to split into clips based on the provided SRT file argument and merge them into a final mp4 file 
5. Optional: If you aren't happy with the clip lengths, you can edit the SRTs using `3_srt_editor.py`

## Roadmap

In rough priority order

- SRT overrides actually used
    - this may cause problems however if manual editing process has already started. you may need to remove the old ones and re-insert
- Generate de-aggressed SRT files
    - do this earlier in the process
    - note overlapping SRTs will always be merged regardless 
- Higher quality rendering options
- Selective re-rendering of SRTs
- Batch mode, i.e point at a folder with an options file and just run it
- Excludes file for ignoring selected SRTs
- Overwrite option.
    - After editing in Resolve for example we can replace the files with high quality ones
- Lower quality rendering options
- Improve performance some more
- Software encoding support

## Implementation

This application has to handle three time formats:

- Time in seconds as float (preferred internally)
- Time in SRT format
- Time in ffmpeg friendly format
- Time in output file friendly format

I have tried to limit transforming to and from seconds as float to only where necessary.
