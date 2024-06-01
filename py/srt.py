import re

from py.time import seconds_to_hmsm

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

# TODO: actually make this part of the transcription?
#   - Time in SRT format
#   - Time in seconds as float
#   - Time in ffmpeg friendly format
def deaggress(time_ranges, seconds=0.5):
    """Deaggress the subtitles by a given amount of seconds."""
    deaggregated_time_ranges = []
    for srt_id, start_seconds, end_seconds in time_ranges:
        deaggregated_start_time = start_seconds - seconds
        deaggregated_end_time = end_seconds + seconds
        deaggregated_time_ranges.append((srt_id, deaggregated_start_time, deaggregated_end_time))
    return merge(deaggregated_time_ranges)

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
