#!/usr/bin/env python3
from scripts.args import parseDeaggressArgs

from hyperedit.deaggress import deaggress

def main():
    args = parseDeaggressArgs()

    deaggress(
        srt_file_path=args.srt_file_path,
        deaggress_seconds=args.deaggress_seconds,
        overwrite=args.overwrite
        )

if __name__ == "__main__":
    main()
