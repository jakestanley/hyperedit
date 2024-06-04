#!/usr/bin/env python3
from py.args import parseBatchArgs
from he_extract_dialog import extract_dialog
from he_transcribe import transcribe
from he_deaggress import deaggress
from he_split_video import split_video

args = parseBatchArgs()

# TODO if args.video_file_path is a directory, process all files in directory
# TODO: ensure returned even if extract_dialog was not required
audio_file_path = extract_dialog(
    video_file_path=args.video_file_path, 
    tracks=args.tracks
    )

# TODO: ensure returned even if transcribe was not required
srt_file_path = transcribe(
    audio_file_path=audio_file_path
    )

# TODO: ensure returned even if deaggress was not required
if args.deaggress_seconds:
    srt_file_path = deaggress(
            srt_file_path=srt_file_path,
            deaggress_seconds=args.deaggress_seconds,
            overwrite=args.overwrite
    )

# TODO if args.video_file_path is a directory, process all files in directory
concat_video_path = split_video(
    srt_file_path=srt_file_path, 
    video_file_path=args.video_file_path,
    preview=args.preview,
    overwrite=args.overwrite,
    range=args.range,
    gpu=args.gpu
    )
