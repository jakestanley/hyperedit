import re

from py.time import seconds_to_hmsm

def parse_srt(file_path):
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
    
    return time_ranges

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
