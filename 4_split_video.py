import subprocess
import os

from py.args import parseSplitVideoArgs
from py.srt import parse_srt

def format_time(time_str):
    return time_str.replace(':', '-').replace('.', '_')

def escape_text(text):
    return text.replace(":", r'\:').replace(",", r'\,').replace("'", r"\'")

def generate_ffmpeg_commands(video_file, time_ranges, output_prefix, overlay=False):
    commands = []
    output_files = []
    srt_ids = []
    for srt_id, start, end in time_ranges: # TODO progress
        formatted_start = format_time(start)
        formatted_end = format_time(end)
        output_file = f"{output_prefix}_{srt_id}_{formatted_start}_to_{formatted_end}.mp4"
        
        ## OVERWRITE
        if not os.path.exists(output_file):
            cmd = [
                'ffmpeg', '-i', video_file, '-ss', start, '-to', end, '-c:v', 'h264_videotoolbox', '-b:v', '5M'
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
    i = 0
    with open('ffmpeg.log', 'w') as log:
        for cmd in commands:
            i+=1
            print(f"Splitting clip on SRT {srt_ids[i]} of {len(srt_ids)}")
            subprocess.run(cmd, stdout=log, stderr=log)

def create_file_list(output_files, list_filename):
    with open(list_filename, 'w') as file:
        for output_file in output_files:
            file.write(f"file '{output_file}'\n")

def concatenate_clips(file_list, output_file):
    cmd = [
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', file_list, '-c:v', 'h264_videotoolbox', '-b:v', '5M', output_file
    ]
    subprocess.run(cmd)

args = parseSplitVideoArgs()

# Paths to your files
srt_file_path = args.srt_file_path
video_file_path = args.video_file_path
directory = os.path.dirname(args.video_file_path)
output_prefix, _ = os.path.splitext(args.video_file_path)
list_filename = 'file_list.txt'
final_output = f"{output_prefix}_final.mp4"
overlay = args.overlay

# Parse SRT and generate FFmpeg commands
# limited to 10 for testing purposes
time_ranges = parse_srt(srt_file_path)
ffmpeg_commands, output_files, srt_ids = generate_ffmpeg_commands(video_file_path, time_ranges, output_prefix, overlay)

# Run the FFmpeg commands to split the video
run_ffmpeg_commands(ffmpeg_commands, srt_ids)

# Create the file list for concatenation
create_file_list(output_files, list_filename)

# Concatenate the split clips into a single video
concatenate_clips(list_filename, final_output)

# Clean up the intermediate files (optional)
# for output_file in output_files:
#     os.remove(output_file)
# os.remove(list_filename)

print("Final video has been successfully generated.")
