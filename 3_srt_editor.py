import subprocess
import os
import re

from py.args import parseSrtEditorArgs
from py.srt import parse_srt, srt_timestamp_to_seconds, seconds_to_srt_timestamp

def parse_entry(entry):
    lines = entry.split('\n')
    srt_id = int(lines[0])
    timestamp = lines[1]
    text = '\n'.join(lines[2:])
    return {
        'id': srt_id,
        'timestamp': timestamp,
        'text': text
    }

def read_srt(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    entries = content.strip().split('\n\n')
    if entries == ['']:
        return []
    parsed_entries = [parse_entry(entry) for entry in entries]
    return parsed_entries

def format_entry(entry):
    return f"{entry['id']}\n{entry['timestamp']}\n{entry['text']}"

def replace_or_add_srt_entry(srt_entries, srt_id, new_start, new_end, new_text):
    entry_found = False
    for entry in srt_entries:
        if entry['id'] == srt_id:
            entry['timestamp'] = f"{new_start} --> {new_end}"
            entry['text'] = new_text
            entry_found = True
            break
    
    if not entry_found:
        new_entry = {
            'id': srt_id,
            'timestamp': f"{new_start} --> {new_end}",
            'text': new_text
        }
        srt_entries.append(new_entry)
        srt_entries.sort(key=lambda e: e['id'])

def remove_srt_entry(srt_entries, srt_id):
    for entry in srt_entries:
        if entry['id'] == srt_id:
            srt_entries.remove(entry)
            break

def write_srt(file_path, srt_entries):
    with open(file_path, 'w', encoding='utf-8') as file:
        content = '\n\n'.join(format_entry(entry) for entry in srt_entries)
        file.write(content)

args = parseSrtEditorArgs()

srt_file_path = args.srt_file_path
srt_id = args.srt_id

srts = parse_srt(srt_file_path)
# TODO: handle array bounds exception
srt = srts[srt_id - 1]

if args.command != "remove":
    start_offset = args.start_offset
    end_offset = args.end_offset

    start = srt_timestamp_to_seconds(srt[1]) - start_offset
    end = srt_timestamp_to_seconds(srt[2]) + end_offset

    duration = end - start

if args.command == "edit" or args.command == "remove":
    # TODO: split video should incorporate the source and any overrides
    # print("Saving edits")
    directory = os.path.dirname(args.srt_file_path)
    basename, _ = os.path.splitext(args.srt_file_path)
    srt_overrides_path = f"{basename}-overrides.srt"

    # TODO: handle if an SRT does not exist in the original file
    srt_entries = read_srt(srt_overrides_path)
    if args.command == "edit":
        replace_or_add_srt_entry(srt_entries, srt_id, seconds_to_srt_timestamp(start), seconds_to_srt_timestamp(end), 'text unused')
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









