import re
import os
import time
import shutil
import subprocess

from hyperedit.time import seconds_to_hmsm

def PreviewSrt(video_path, srt, start_offset, end_offset, player='vlc'):

    start = srt[1] - start_offset
    end = srt[2] + end_offset
    duration = end - start

    if player == 'vlc':
        command = [
            'vlc',
            video_path,
            '--start-time', f'{start}',
            '--stop-time', f'{start + duration}'
        ]
    elif player == 'mplayer':
        command = [
            'mplayer',
            '-ss', f'{start}',
            '-endpos', f'{duration}',
            video_path
        ]
    else:
        raise Exception(f"Unsupported player {player}")


    print(f"Playing SRT {srt[0]} at range {srt[1]} - {srt[2]} (offsets -{start_offset},{end_offset})")
    subprocess.run(command)
    print(f"Played SRT {srt[0]} at range {srt[1]} - {srt[2]} (offsets -{start_offset},{end_offset})")

def replace_or_add_srt_entry(srt_entries, srt_id, new_start, new_end, new_text):
    entry_found = False
    for i in range(len(srt_entries)):
        entry = srt_entries[i]
        if int(entry[0]) == srt_id:
            srt_entries[i] = [srt_id, new_start, new_end]
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

def merge(time_ranges):
    """Merge overlapping subtitles."""
    merged_time_ranges = []
    for srt_id, start_time, end_time in time_ranges:
        merged = False
        for i, (merged_srt_id, merged_start_time, merged_end_time) in enumerate(merged_time_ranges):
            if start_time <= merged_end_time:
                merged_time_ranges[i] = (merged_srt_id, min(start_time, merged_start_time), max(end_time, merged_end_time))
                merged = True
                break
        if not merged:
            merged_time_ranges.append((srt_id, start_time, end_time))
    return merged_time_ranges

def _format_entry(entry):
    return f"{entry[0]}\n{entry[1]}\n{entry[2]}"

def deaggress_ranges_by_seconds(time_ranges, seconds=1):
    """Deaggress the subtitles by a given amount of seconds. End deaggression is halved so that we don't start running into the next clip and cut it off"""
    deaggregated_time_ranges = []
    for srt_id, start_seconds, end_seconds in time_ranges:
        deaggregated_start_time = start_seconds - seconds
        deaggregated_end_time = end_seconds + (seconds / 2)
        deaggregated_time_ranges.append((srt_id, deaggregated_start_time, deaggregated_end_time))
    return merge(deaggregated_time_ranges) # TODO: potential bug: merge might not be respecting start/end times of deaggressed clips

def parse_srt(file_path):

    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)

    with open(file_path, 'r') as file:
        content = file.read()
    
    pattern = re.compile(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n')
    matches = pattern.findall(content)
    
    time_ranges = []
    for match in matches:
        srt_id = match[0]
        start_time = srt_timestamp_to_seconds(match[1])
        end_time = srt_timestamp_to_seconds(match[2])
        time_ranges.append((srt_id, start_time, end_time))

    # TODO merging may reduce the number of SRTs if the user has made modifications
    return time_ranges

def backup_srt(srt_file_path):
    directory = os.path.dirname(srt_file_path)
    basename, _ = os.path.splitext(srt_file_path)
    backup_file_path = f"{basename}.prev{int(time.time())}.srt"
    shutil.copyfile(srt_file_path, backup_file_path)

def create_srt_entry(srt_id, start, end, text="unused text"):
    return [srt_id, f"{seconds_to_srt_timestamp(start)} --> {seconds_to_srt_timestamp(end)}", text]

def write_srt(file_path, srt_entries):
    with open(file_path, 'w', encoding='utf-8') as file:
        content = '\n\n'.join(_format_entry(entry) for entry in srt_entries)
        file.write(content)

def srt_timestamp_to_seconds(time_str):
    """Convert a time string in hh:mm:ss.sss format to seconds (float)."""
    h, m, s = time_str.split(':')
    s, ms = s.split(',')
    return int(h) * 3600 + int(m) * 60 + float(s) + int(ms) / 1000.0

def seconds_to_srt_timestamp(seconds):

    hours, minutes, secs, milliseconds = seconds_to_hmsm(seconds)

    # Format the timestamp as HH:MM:SS,mmm
    timestamp = f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"
    
    return timestamp
