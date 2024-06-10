#!/usr/bin/env python3
from scripts.args import parseSplitVideoArgs

from hyperedit import split_video

def main():
    args = parseSplitVideoArgs()

    split_video(srt_file_path=args.srt_file_path, 
                video_file_path=args.video_file_path, 
                preview=args.preview, 
                range=args.range,
                overwrite=args.overwrite,
                gpu=args.gpu)
