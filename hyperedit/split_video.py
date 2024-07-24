import subprocess
import os
import time

from hyperedit.srt import seconds_to_srt_timestamp, GetPrimitiveSrtListHash
from hyperedit.ffmpeg import get_params_for_gpu, seconds_to_ffmpeg_timestamp as stff
from hyperedit.time import seconds_to_output_timestamp, seconds_to_time_remaining
from hyperedit.concatenate import create_file_list, concatenate_clips

def _escape_text(text):
    return text.replace(":", r'\:').replace(",", r'\,').replace("'", r"\'")

def _generate_split_ffmpeg_commands(
        srts=[],
        original_video_file_path=None, 
        output_directory=None, 
        preview=False, 
        overwrite=False,
        gpu=None
        ):

    gpu_params = get_params_for_gpu(gpu)
    srt_hash = GetPrimitiveSrtListHash(srts)

    commands = []
    output_files = []
    srt_ids = []
    for srt_id, start, end, _ in srts:
        formatted_start = seconds_to_output_timestamp(start)
        formatted_end = seconds_to_output_timestamp(end)
        seek_time = start - 2
        if seek_time < 0:
            seek_time = 0
        seek_offset = start - seek_time
        duration = end - start

        filter_complex = []
        maps = []

        output_file = os.path.join(output_directory, f"{"preview" if preview else "final"}_S{srt_id}_{formatted_start}_to_{formatted_end}.mp4")
        preset = gpu_params['fast_preset'] if preview else gpu_params['quality_preset']

        # if we're in preview mode, render at lower detail with "debug" text
        if preview:

            # scale video
            filter_complex.append(f"[0:v]scale=-1:480[v_scaled]")

            # preview text 1 # TODO function for this
            preview_text_1 = _escape_text(f"ID: {srt_id}, Start: {seconds_to_srt_timestamp(start)}, End: {seconds_to_srt_timestamp(end)}")
            drawtext = f"drawtext=text='{preview_text_1}':fontsize=24:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=2:x=10:y=10"
            filter_complex.append(f"[v_scaled]{drawtext}[v_overlaid1]")

            # preview text 2
            # TODO: hyperedit-gui should save the SRTs with a hash for later
            if srt_hash:
                preview_text_2 = _escape_text(f"SRT hash: {srt_hash}")
                drawtext = f"drawtext=text='{preview_text_2}':fontsize=12:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=2:x=10:y=40"
                filter_complex.append(f"[v_overlaid1]{drawtext}[v_overlaid2]")
                maps.append('[v_overlaid2]')
            else:
                maps.append('[v_overlaid1]')

        else:
            # map all video and audio streams
            maps.append('0:v')
            
        # always append all audio streams
        maps.append('0:a')

        if not os.path.exists(output_file) or overwrite:
            cmd = [
                'ffmpeg', '-y',
                # '-hwaccel', hwaccel, # this doesn't work on mac OR windows right now
                '-ss', stff(seek_time),
                '-i', original_video_file_path, 
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

def split(
        srts: list[list[str]]=None, # TODO is this type hint correct?
        original_video_file_path=None,
        output_directory=None,
        preview=False,
        overwrite=False,
        gpu=None
        ):
    
    if not srts:
        raise Exception("Argument 'srts' is required")

    if original_video_file_path is None:
        raise Exception("Argument 'original_video_file_path' is required")

    # for hyperedit this should be project-path/CLIPS
    if not output_directory:
        # if not provided, create a directory with the file path name and put it in CLIPS
        output_directory = os.path.join(os.path.dirname(original_video_file_path), os.path.basename(original_video_file_path), "CLIPS")

    # generate ffmpeg commands 
    #ffmpeg_commands, output_files, srt_ids = _generate_split_ffmpeg_commands(original_video_file_path, srts, output_prefix, gpu, preview, overwrite)
    ffmpeg_commands, output_files, srt_ids = _generate_split_ffmpeg_commands(
        srts=srts,
        original_video_file_path=original_video_file_path, 
        output_directory=output_directory,
        preview=preview,
        overwrite=overwrite,
        gpu=gpu)

    # Run the FFmpeg commands to split the video
    if len(ffmpeg_commands) == 0:
        print("No clips to split.")
    else:
        start_time = time.time()
        durations = _run_ffmpeg_commands(ffmpeg_commands, srt_ids)
        end_time = time.time()
        print(f"Splitting took {end_time - start_time:.1f} seconds")
        print(f"Average split time: {sum(durations)/len(durations):.1f} seconds")

    return output_files

def concat(
        srts: list[list[str]] = [],
        original_video_file_path=None,
        output_directory=None,
        preview=False,
        overwrite=False, # TODO use this parameter
        gpu=None,
        files=[]):
    
    if output_directory is None:
        output_directory = os.path.join(os.path.dirname(original_video_file_path), os.path.basename(original_video_file_path), "RENDERS")

    final_output = os.path.join(output_directory, f"{"preview" if preview else "final"}_{GetPrimitiveSrtListHash(srts)}.mp4")
    list_filename = f'file_list_{int(time.time())}.txt'

    # Create the file list for concatenation
    create_file_list(files, list_filename)

    # Concatenate the split clips into a single video
    start_time = time.time()
    concatenate_clips(list_filename, final_output, gpu)
    end_time = time.time()
    
    print(f"Concatenation took {end_time - start_time:.1f} seconds")
    print(f"{"Preview" if preview else "Final"} video has been successfully generated.")

    return final_output
