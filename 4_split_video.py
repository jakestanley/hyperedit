import subprocess
import os
import datetime
import time

from py.args import parseSplitVideoArgs
from py.srt import parse_srt, seconds_to_srt_timestamp
from py.ffmpeg import get_params_for_gpu, seconds_to_ffmpeg_timestamp as stff
from py.time import seconds_to_output_timestamp

def escape_text(text):
    return text.replace(":", r'\:').replace(",", r'\,').replace("'", r"\'")

def generate_ffmpeg_commands(video_file, time_ranges, output_prefix, gpu, overlay=False):

    gpu_params = get_params_for_gpu(gpu)

    commands = []
    output_files = []
    srt_ids = []
    for srt_id, start, end in time_ranges:
        formatted_start = seconds_to_output_timestamp(start)
        formatted_end = seconds_to_output_timestamp(end)
        seek_time = start - 2
        seek_offset = start - seek_time
        duration = end - start
        output_file = f"{output_prefix}_{srt_id}_{formatted_start}_to_{formatted_end}.mp4"

        if overlay:
            preset = gpu_params['fast_preset']
        else:
            preset = gpu_params['quality_preset']

        if not os.path.exists(output_file): # TODO different options for full render
            cmd = [
                'ffmpeg',
                # '-hwaccel', hwaccel, # this doesn't work on mac OR windows right now
                '-ss', stff(seek_time),
                '-i', video_file, 
                '-ss', stff(seek_offset),
                '-t', stff(duration), 
                '-c:v', gpu_params['encoder'], 
                gpu_params['preset_param'], preset,
                '-b:v', '5M',
                # Map all video and audio streams
                '-map', '0:v', '-map', '0:a'
            ]

            if overlay: # TODO: customise overlay more, maybe include source SRTs, date, etc
                human_readable_text = escape_text(f"ID: {srt_id}, Start: {seconds_to_srt_timestamp(start)}, End: {seconds_to_srt_timestamp(end)}")
                drawtext = f"drawtext=text='{human_readable_text}':fontsize=72:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=5:x=10:y=10"
                cmd.extend(['-vf', drawtext])
            cmd.append(output_file)

            commands.append(cmd)
            srt_ids.append(srt_id)
        output_files.append(output_file)
    return commands, output_files, srt_ids

def run_ffmpeg_commands(commands, srt_ids):
    with open('ffmpeg.log', 'w') as log: # TODO: split video should incorporate the source and any overrides
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
        for output_file in output_files[0:10]:
            file.write(f"file '{output_file}'\n")

def concatenate_clips(file_list, output_file, gpu):

    gpu_params = get_params_for_gpu(gpu)

    cmd = [
        'ffmpeg', 
        '-y', 
        '-f', 'concat', 
        '-safe', '0', 
        '-i', file_list, 
        '-c:v', gpu_params['encoder'],
        '-b:v', '5M',
        # Map all video and audio streams
        '-map', '0:v', '-map', '0:a',
        output_file
    ]
    with open('ffmpeg.log', 'a') as log:
        e = subprocess.run(cmd, stdout=log, stderr=log)
        if e.returncode != 0:
            raise(f"Error concatenating clips: ffmpeg returned exit code {e.returncode}")
# TODO: add option to select clip range for rendering (i.e youtube shorts)
args = parseSplitVideoArgs()

# Paths to your files
srt_file_path = args.srt_file_path
video_file_path = args.video_file_path
directory = os.path.dirname(args.video_file_path)
output_prefix, _ = os.path.splitext(args.video_file_path)
list_filename = 'file_list.txt'


# Parse SRT
if args.range:
    final_output = f"{output_prefix}_final_{args.range[0]}-{args.range[1]}.mp4"
    time_ranges = parse_srt(srt_file_path)[(args.range[0]-1):(args.range[1]-1)]
else:
    final_output = f"{output_prefix}_final.mp4"
    time_ranges = parse_srt(srt_file_path)

# generate ffmpeg commands
ffmpeg_commands, output_files, srt_ids = generate_ffmpeg_commands(video_file_path, time_ranges, output_prefix, args.gpu, args.overlay)

# Run the FFmpeg commands to split the video
run_ffmpeg_commands(ffmpeg_commands, srt_ids)

# Create the file list for concatenation
create_file_list(output_files, list_filename)

# Concatenate the split clips into a single video
concatenate_clips(list_filename, final_output, args.gpu)

print("Final video has been successfully generated.")
