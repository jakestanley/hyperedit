#!/usr/bin/env python3
import subprocess
import os
import time

from py.args import parseSplitVideoArgs
from py.srt import parse_srt, seconds_to_srt_timestamp
from py.ffmpeg import get_params_for_gpu, seconds_to_ffmpeg_timestamp as stff
from py.time import seconds_to_output_timestamp

def _escape_text(text):
    return text.replace(":", r'\:').replace(",", r'\,').replace("'", r"\'")

def _generate_ffmpeg_commands(video_file, time_ranges, output_prefix, gpu, preview=False, overwrite=False, srt_file_path=None):

    gpu_params = get_params_for_gpu(gpu)

    commands = []
    output_files = []
    srt_ids = []
    for srt_id, start, end in time_ranges:
        formatted_start = seconds_to_output_timestamp(start)
        formatted_end = seconds_to_output_timestamp(end)
        seek_time = start - 2
        if seek_time < 0:
            seek_time = 0
        seek_offset = start - seek_time
        duration = end - start


        filter_complex = []
        maps = []

        if preview:
            output_file = f"{output_prefix}_S{srt_id}_{formatted_start}_to_{formatted_end}.mp4"
            preset = gpu_params['fast_preset']
            # scale video
            filter_complex.append(f"[0:v]scale=-1:480[v_scaled]")

            # preview text 1 # TODO function for this
            preview_text_1 = _escape_text(f"ID: {srt_id}, Start: {seconds_to_srt_timestamp(start)}, End: {seconds_to_srt_timestamp(end)}")
            drawtext = f"drawtext=text='{preview_text_1}':fontsize=24:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=2:x=10:y=10"
            filter_complex.append(f"[v_scaled]{drawtext}[v_overlaid1]")

            # preview text 2
            if srt_file_path:
                preview_text_2 = _escape_text(f"SRT file: {os.path.basename(srt_file_path)}")
                drawtext = f"drawtext=text='{preview_text_2}':fontsize=12:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=2:x=10:y=40"
                filter_complex.append(f"[v_overlaid1]{drawtext}[v_overlaid2]")
                maps.append('[v_overlaid2]')
            else:
                maps.append('[v_overlaid1]')
            
            maps.append('0:a')

        else:
            output_file = f"{output_prefix}_S{srt_id}_{formatted_start}_to_{formatted_end}.mp4"
            preset = gpu_params['quality_preset']
            # map all video and audio streams
            maps.append('0:v')
            maps.append('0:a')

        if not os.path.exists(output_file) or overwrite:
            cmd = [
                'ffmpeg', '-y',
                # '-hwaccel', hwaccel, # this doesn't work on mac OR windows right now
                '-ss', stff(seek_time),
                '-i', video_file, 
                '-ss', stff(seek_offset),
                '-t', stff(duration), 
                '-c:v', gpu_params['encoder'], 
                gpu_params['preset_param'], preset,
                '-b:v', '5M'
            ]

            if len(filter_complex) > 0:
                cmd.extend(['-filter_complex', ';'.join(filter_complex)])

            for map in maps:
                cmd.extend(['-map', map])

            cmd.append(output_file)

            # add this ffmpeg command to the list of ffmpeg commands to run
            commands.append(cmd)
            srt_ids.append(srt_id)
        output_files.append(output_file)
    return commands, output_files, srt_ids

def _run_ffmpeg_commands(commands, srt_ids):
    durations = []
    with open('ffmpeg.log', 'w') as log: # TODO: split video should incorporate the source and any overrides
        for i in range(len(commands)):
            print(f"Splitting clip {i+1} of {len(srt_ids)}... ", end='', flush=True)
            start_time = time.time()
            e = subprocess.run(commands[i], stdout=log, stderr=log)
            if e.returncode != 0:
                raise(f"Error splitting clip {i+1} of {len(srt_ids)}: ffmpeg returned exit code {e.returncode}")
            end_time = time.time()
            duration = end_time - start_time
            durations.append(duration)
            print(f" {duration:.1f} seconds. Rolling average: {sum(durations)/len(durations):.1f} seconds. ETA: {((sum(durations)/len(durations))*(len(commands)-i)/60):.1f} minutes")
    return durations

def create_file_list(output_files, list_filename):
    with open(list_filename, 'w') as file:
        for output_file in output_files:
            file.write(f"file '{output_file}'\n")

# TODO separate script for concatenate
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

def split_video(
        srt_file_path=None, 
        video_file_path=None,
        preview=False,
        overwrite=False,
        range=None,
        gpu=None
        ):
    
    if srt_file_path is None:
        raise Exception("SRT file path is required")
    
    if video_file_path is None:
        raise Exception("Video file path is required")
    
    # TODO test required args are present or raise exception

    if preview:
        output_prefix = f"{os.path.splitext(video_file_path)[0]}_preview"
    else:
        output_prefix, _ = os.path.splitext(video_file_path)

    # TODO use args to generate this instead of just using a timestamp
    list_filename = f'file_list_{int(time.time())}.txt'

    # Parse SRT
    if range:
        final_output = f"{output_prefix}_final_{range[0]}-{range[1]}.mp4"
        time_ranges = parse_srt(srt_file_path)[(range[0]-1):(range[1]-1)]
    else:
        final_output = f"{output_prefix}_final.mp4"
        time_ranges = parse_srt(srt_file_path)

    # generate ffmpeg commands 
    # TODO separate output_files and srt_ids generation so concat can go in its own file
    ffmpeg_commands, output_files, srt_ids = _generate_ffmpeg_commands(video_file_path, time_ranges, output_prefix, gpu, preview, overwrite, srt_file_path)

    # Run the FFmpeg commands to split the video
    if len(ffmpeg_commands) == 0:
        print("No clips to split.")
    else:
        start_time = time.time()
        durations = _run_ffmpeg_commands(ffmpeg_commands, srt_ids)
        end_time = time.time()
        print(f"Splitting took {end_time - start_time:.1f} seconds")
        print(f"Average split time: {sum(durations)/len(durations):.1f} seconds")

    # Create the file list for concatenation
    create_file_list(output_files, list_filename)

    # Concatenate the split clips into a single video
    start_time = time.time()
    concatenate_clips(list_filename, final_output, gpu)
    end_time = time.time()
    print(f"Concatenation took {end_time - start_time:.1f} seconds")

    print("Final video has been successfully generated.")

    return final_output

if __name__ == "__main__":

    args = parseSplitVideoArgs()
    split_video(srt_file_path=args.srt_file_path, 
                video_file_path=args.video_file_path, 
                preview=args.preview, 
                range=args.range,
                overwrite=args.overwrite,
                gpu=args.gpu)
