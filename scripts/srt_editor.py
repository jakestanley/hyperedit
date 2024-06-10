#!/usr/bin/env python3
import subprocess
import os

from scripts.args import parseSrtEditorArgs
from hyperedit.srt import parse_srt, write_srt, create_srt_entry, merge, backup_srt, replace_or_add_srt_entry, remove_srt_entry

def main():

    args = parseSrtEditorArgs()

    if not args.command:
        raise Exception("command is required")

    srt_file_path = args.srt_file_path
    srt_id = args.srt_id

    if os.path.exists(srt_file_path) == False:
        raise Exception(f"SRT file {srt_file_path} does not exist")

    srts = parse_srt(srt_file_path)
    if len(srts) == 0:
        raise Exception("SRT file is empty")

    try:
        # user types 1, but python indexes from 0
        srt = srts[srt_id - 1] # there's a bug here where it's doing the wrong one. the wrong ID might be getting set elsewhere # TODO fix
    except IndexError:
        raise Exception(f"SRT ID {srt_id} is not in the provded SRT file")

    if args.command != "remove":
        start_offset = args.start_offset
        end_offset = args.end_offset

        start = srt[1] - start_offset
        end = srt[2] + end_offset

        duration = end - start

    if args.command == "edit" or args.command == "remove":
        basename, _ = os.path.splitext(srt_file_path)

        if args.command == "edit":
            replace_or_add_srt_entry(srts, srt_id, start, end, 'text unused')
        else:
            remove_srt_entry(srts, srt_id)
        
        merged_srts = merge(srts)
        formatted_srts = []
        # srt_id = 1
        for srt_id, start, end in merged_srts:
            formatted_srts.append(create_srt_entry(srt_id=srt_id, start=start, end=end))
            # NOTE: avoiding doing this. reindexing SRTs is done in deaggress but 
            #   here it would result in loads of SRTs needing to be re-rendered
            # srt_id += 1

        backup_srt(srt_file_path)
        write_srt(srt_file_path, formatted_srts)
    elif args.command == "remove":
        raise("Not yet implemented")
    elif args.command == "preview":
        if args.player == 'vlc':
            command = [
                'vlc',
                args.video_file_path,
                '--start-time', f'{start}',
                '--stop-time', f'{start + duration}'
            ]
        # TODO: fix mplayer seek time being off
        # recommend VLC as mplayer seek time is off
        elif args.player == 'mplayer':
            command = [
                'mplayer',
                '-ss', f'{start}',
                '-endpos', f'{duration}',
                args.video_file_path
            ]
        else:
            raise Exception(f"Unsupported player {args.player}")

        print(f"Playing SRT {srt[0]} at range {srt[1]} - {srt[2]} (offsets -{start_offset},{end_offset})")
        subprocess.run(command)
        print(f"Played SRT {srt[0]} at range {srt[1]} - {srt[2]} (offsets -{start_offset},{end_offset})")








