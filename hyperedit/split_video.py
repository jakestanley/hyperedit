import subprocess
import os
import time

from hyperedit.srt import parse_srt, seconds_to_srt_timestamp, GetPrimitiveSrtListHash
from hyperedit.ffmpeg import get_params_for_gpu, seconds_to_ffmpeg_timestamp as stff
from hyperedit.time import seconds_to_output_timestamp, seconds_to_time_remaining
from hyperedit.concatenate import create_file_list, concatenate_clips

def _escape_text(text):
    return text.replace(":", r'\:').replace(",", r'\,').replace("'", r"\'")

def _generate_ffmpeg_commands(video_file, time_ranges, output_prefix, gpu, preview=False, overwrite=False, srt_file_path=None):

    gpu_params = get_params_for_gpu(gpu)

    commands = []
    output_files = []
    srt_ids = []
    for srt_id, start, end, _ in time_ranges:
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
    with open('ffmpeg-split.log', 'w') as log: # TODO: split video should incorporate the source and any overrides
        for i in range(len(commands)):
            print(f"Splitting clip {i+1} of {len(srt_ids)}... ", end='', flush=True)
            start_time = time.time()
            e = subprocess.run(commands[i], stdout=log, stderr=log)
            if e.returncode != 0:
                raise(f"Error splitting clip {i+1} of {len(srt_ids)}: ffmpeg returned exit code {e.returncode}")
            end_time = time.time()
            duration = end_time - start_time
            durations.append(duration)
            print(f" {duration:.1f} seconds. Rolling average: {sum(durations)/len(durations):.1f} seconds. ETA: {seconds_to_time_remaining((sum(durations)/len(durations))*(len(commands)-i))}\r", end='', flush=True)
    return durations

def split_video(
        srt_file_path=None,
        srts=None,
        video_file_path=None,
        preview=False,
        overwrite=False,
        range=None,
        gpu=None,
        output_directory=None
        ):
    
    if srt_file_path is None:
        if srts:
            time_ranges = srts
        else:
            raise Exception("One of arguments srt_file_path or srts are required")
    else:
        time_ranges = parse_srt(srt_file_path)

    if video_file_path is None:
        raise Exception("Video file path is required")
    
    # TODO test required args are present or raise exception

    if not output_directory:
    # if output directory not provided, put the clips in the same directory as the source video file
        if preview:
            output_prefix = f"{os.path.splitext(video_file_path)[0]}_preview"
        else:
            output_prefix, _ = os.path.splitext(video_file_path)
    else:
    # if output directory is provided, put the clips in the provided directory
        if preview:
            output_prefix = os.path.join(output_directory, "preview")
        else:
            output_prefix = output_directory

    # TODO use args to generate this instead of just using a timestamp
    list_filename = f'file_list_{int(time.time())}.txt'

    # TODO ignore if srts provided
    if srts:
        final_output = f"{output_prefix}_final_{GetPrimitiveSrtListHash(srts)}.mp4"
    elif range:
        final_output = f"{output_prefix}_final_{range[0]}-{range[1]}.mp4"
        time_ranges = parse_srt(srt_file_path)[(range[0]-1):(range[1]-1)]
    else:
        final_output = f"{output_prefix}_final.mp4"

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
