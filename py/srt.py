import re

def parse_srt(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    pattern = re.compile(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n')
    matches = pattern.findall(content)
    
    time_ranges = []
    for match in matches:
        srt_id = match[0]
        start_time = match[1].replace(',', '.')
        end_time = match[2].replace(',', '.')
        time_ranges.append((srt_id, start_time, end_time))
    
    return time_ranges

def srt_timestamp_to_seconds(time_str):
    """Convert a time string in hh:mm:ss.sss format to seconds (float)."""
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)

def seconds_to_srt_timestamp(seconds):
    # Calculate hours, minutes, and seconds
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    
    # Format the timestamp as HH:MM:SS,mmm
    timestamp = f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"
    
    return timestamp
