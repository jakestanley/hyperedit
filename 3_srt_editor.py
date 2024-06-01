import subprocess
import os

from py.args import parseSrtEditorArgs
from py.srt import parse_srt, seconds_to_srt_timestamp, write_srt, create_srt_entry

def replace_or_add_srt_entry(srt_entries, srt_id, new_start, new_end, new_text):
    entry_found = False
    for i in range(len(srt_entries)):
        entry = srt_entries[i]
        if int(entry[0]) == srt_id:
            srt_entries[i] = create_srt_entry(srt_id, new_start, new_end, new_text)
            entry_found = True
            break
    
    if not entry_found:
        new_entry = create_srt_entry(srt_id, new_start, new_end, new_text)
        srt_entries.append(new_entry)
        srt_entries.sort(key=lambda e: e[0])

def remove_srt_entry(srt_entries, srt_id):
    for entry in srt_entries:
        if int(entry[0]) == srt_id:
            srt_entries.remove(entry)
            break

args = parseSrtEditorArgs()

srt_file_path = args.srt_file_path
srt_id = args.srt_id

srts = parse_srt(srt_file_path)
if len(srts) == 0:
    raise Exception("SRT file is empty")

try:
    srt = srts[srt_id - 1]
except IndexError:
    raise Exception(f"SRT ID {srt_id} is not in the provded SRT file")

if args.command != "remove":
    start_offset = args.start_offset
    end_offset = args.end_offset

    start = srt[1] - start_offset
    end = srt[2] + end_offset

    duration = end - start

if args.command == "edit" or args.command == "remove":
    directory = os.path.dirname(args.srt_file_path)
    basename, _ = os.path.splitext(args.srt_file_path)
    srt_overrides_path = f"{basename}-overrides.srt"

    if os.path.exists(srt_overrides_path):
        srt_entries = parse_srt(srt_overrides_path)
    else:
        srt_entries = []

    if args.command == "edit":
        replace_or_add_srt_entry(srt_entries, srt_id, start, end, 'text unused')
    else:
        remove_srt_entry(srt_entries, srt_id)
    
    write_srt(srt_overrides_path, srt_entries)
elif args.command == "remove":
    raise("Not yet implemented")
elif args.command == "preview":
    command = [
        'mplayer',
        '-ss', f'{start}',
        '-endpos', f'{duration}',
        args.video_file_path
    ]

    print(f"Playing SRT {srt_id} at range {srt[1]} - {srt[2]} (offsets -{start_offset},{end_offset})")
    subprocess.run(command)
    print(f"Played SRT {srt_id} at range {srt[1]} - {srt[2]} (offsets -{start_offset},{end_offset})")









