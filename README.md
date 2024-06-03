# Hyperedit

Removes silences from your videos.

## Recommended use

You've recorded some footage with multiple audio tracks but there's a lot of silence and you want to speed up the editing process

Because mplayer and vlc will only play one audio stream unless you want to preview all your files in Resolve, I strongly recommend a setup like:

- Track 0: Game audio and all voice
- Track 1: Game audio
- Track 2: Your voice
- Track 3: Other voice

With this setup, you can use the `--tracks` argument as such: `--tracks 2 3` and then you can just remove the all audio track in post.

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

- Higher quality rendering options
- Batch mode, i.e point at a folder with an options file and just run it
- Improve performance some more
- Software encoding support
- analyse game audio for volume peaks and use this as weights

## Implementation

This application has to handle three time formats:

- Time in seconds as float (preferred internally)
- Time in SRT format
- Time in ffmpeg friendly format
- Time in output file friendly format

I have tried to limit transforming to and from seconds as float to only where necessary.
