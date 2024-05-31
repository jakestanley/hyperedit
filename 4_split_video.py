import subprocess
import os
import datetime
import time

from py.args import parseSplitVideoArgs
from py.srt import parse_srt

def format_time(time_str):
    return time_str.replace(':', '-').replace('.', '_')

def escape_text(text):
    return text.replace(":", r'\:').replace(",", r'\,').replace("'", r"\'")

def get_seek_time(time_str, delta_seconds):
    """Get formatted seek time"""
    time_obj = datetime.datetime.strptime(time_str, '%H:%M:%S.%f')
    adjusted_time = time_obj + datetime.timedelta(seconds=delta_seconds)
    if adjusted_time < datetime.datetime(1900, 1, 1):
        return '00:00:00.000'
    return adjusted_time.strftime('%H:%M:%S.%f')

def calculate_seek_offset(start, seek_time):
    """Calculate the offset between actual start time and the initial fast seek."""
    start_time = datetime.datetime.strptime(start, '%H:%M:%S.%f')
    adjusted_start_time = datetime.datetime.strptime(seek_time, '%H:%M:%S.%f')
    delta = start_time - adjusted_start_time
    return str(delta)

def calculate_duration(start, end):
    """Calculate the duration between the start and end times."""
    start_time = datetime.datetime.strptime(start, '%H:%M:%S.%f')
    end_time = datetime.datetime.strptime(end, '%H:%M:%S.%f')
    duration = end_time - start_time
    return str(duration)

def get_hardware(gpu):
    # TODO case insensitive
    if gpu == 'apple':
        encoder = 'h264_videotoolbox'
        hwaccel = 'videotoolbox'
    elif gpu == 'nvidia':
        encoder = 'h264_nvenc'
        hwaccel = 'cuvid'
    else:
        raise Exception(f"Invalid GPU: {gpu}")

    return encoder, hwaccel

def generate_ffmpeg_commands(video_file, time_ranges, output_prefix, gpu, overlay=False):

    encoder, hwaccel = get_hardware(gpu)

    commands = []
    output_files = []
    srt_ids = []
    for srt_id, start, end in time_ranges: # TODO progress
        formatted_start = format_time(start)
        formatted_end = format_time(end)
        seek_time = get_seek_time(start, -2)
        seek_offset = calculate_seek_offset(start, seek_time)
        duration = calculate_duration(start, end)
        output_file = f"{output_prefix}_{srt_id}_{formatted_start}_to_{formatted_end}.mp4"
        
        ## OVERWRITE
        if not os.path.exists(output_file):
            cmd = [
                'ffmpeg',
                # '-hwaccel', hwaccel, # this doesn't work on mac OR windows right now
                '-ss', seek_time,
                '-i', video_file, 
                '-ss', seek_offset,
                '-t', duration, 
                '-c:v', encoder, 
                '-b:v', '5M'
            ]
            if overlay:
                human_readable_text = escape_text(f"ID: {srt_id}, Start: {start}, End: {end}")
                drawtext = f"drawtext=text='{human_readable_text}':fontsize=72:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=5:x=10:y=10"
                cmd.extend(['-vf', drawtext])
            cmd.append(output_file)

            commands.append(cmd)
            srt_ids.append(srt_id)
        output_files.append(output_file)
    return commands, output_files, srt_ids

def run_ffmpeg_commands(commands, srt_ids):
    with open('ffmpeg.log', 'w') as log:
        for i in range(len(commands)):
            print(f"Splitting clip {i+1} of {len(srt_ids)}... ", end='', flush=True)
            start_time = time.time()
            e = subprocess.run(commands[i], stdout=log, stderr=log)
            if e.returncode != 0:
                raise(f"Error splitting clip {i+1} of {len(srt_ids)}: ffmpeg returned exit code {e.returncode}")
            end_time = time.time()
            print(f" {end_time - start_time:.1f} seconds")

def create_file_list(output_files, list_filename):
    with open(list_filename, 'w') as file:
        for output_file in output_files:
            file.write(f"file '{output_file}'\n")

def concatenate_clips(file_list, output_file, gpu):

    encoder, hwaccel = get_hardware(gpu)

    cmd = [
        'ffmpeg', 
        '-y', 
        '-f', 'concat', 
        '-safe', '0', 
        '-i', file_list, 
        '-c:v', encoder, 
        '-b:v', '5M', 
        output_file
    ]
    with open('ffmpeg.log', 'a') as log:
        e = subprocess.run(cmd, stdout=log, stderr=log)
        if e.returncode != 0:
            raise(f"Error concatenating clips: ffmpeg returned exit code {e.returncode}")

args = parseSplitVideoArgs()

# Paths to your files
srt_file_path = args.srt_file_path
video_file_path = args.video_file_path
directory = os.path.dirname(args.video_file_path)
output_prefix, _ = os.path.splitext(args.video_file_path)
list_filename = 'file_list.txt'
final_output = f"{output_prefix}_final.mp4"

# Parse SRT and generate FFmpeg commands
# limited to 10 for testing purposes
time_ranges = parse_srt(srt_file_path)
ffmpeg_commands, output_files, srt_ids = generate_ffmpeg_commands(video_file_path, time_ranges, output_prefix, args.gpu, args.overlay)

# Run the FFmpeg commands to split the video
run_ffmpeg_commands(ffmpeg_commands, srt_ids)

# Create the file list for concatenation
create_file_list(output_files, list_filename)

# Concatenate the split clips into a single video
concatenate_clips(list_filename, final_output, args.gpu)

# Clean up the intermediate files (optional)
# for output_file in output_files:
#     os.remove(output_file)
# os.remove(list_filename)

print("Final video has been successfully generated.")
