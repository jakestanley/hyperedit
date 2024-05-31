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
