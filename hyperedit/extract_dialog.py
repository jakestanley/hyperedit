#!/usr/bin/env python3
import subprocess
import os

def _merge_audio_tracks(input_video, tracks, output_audio):
    # Construct the filter_complex string based on the provided track indices
    input_tracks = ''.join(f'[0:a:{i}]' for i in tracks)
    filter_complex = f"{input_tracks}amerge=inputs={len(tracks)}"

    # Define the ffmpeg command
    ffmpeg_command = [
        'ffmpeg',
        '-stats',
        '-y', # overwrites
        '-i', input_video,
        '-filter_complex', filter_complex,
        '-ac', str(len(tracks)),
        '-c:a', 'pcm_s16le',
        output_audio
    ]
    
    # Run the ffmpeg command
    with open('ffmpeg-audio.log', 'w') as log:
        result = subprocess.run(ffmpeg_command, stdout=log, stderr=log)
    
    # Check if the command was successful
    if result.returncode == 0:
        print("Audio tracks merged successfully.")
    else:
        print("Error merging audio tracks:")
        print(result.stderr.decode())

def get_audio_tracks(video_file_path):
    # Define the ffmpeg command to show the available audio tracks
    ffmpeg_command = [
        'ffmpeg',
        '-stats',
        '-i', video_file_path,
        '-q', '0'
    ]

    # Run the ffmpeg command and capture the output
    result = subprocess.run(ffmpeg_command, capture_output=True, text=True)

    # Parse the output to get the available audio track indices
    audio_tracks = []
    for line in result.stdout.splitlines():
        if line.startswith('    Stream #'):
            track_info = line.split(':')[2].strip().split(' ')
            if track_info[0] == 'Audio':
                audio_tracks.append(int(track_info[1]))

    return audio_tracks

def extract_dialog(video_file_path=None, tracks=None):

    if video_file_path is None:
        raise Exception("Application error: 'video_file_path' argument missing")
    
    if tracks is None:
        raise Exception("Application error: 'tracks' argument missing")

    basename, _ = os.path.splitext(video_file_path)
    output_audio_file = os.path.join(f"{basename}_merged.wav")

    if os.path.exists(output_audio_file):
        print(f"Audio file already exists at {output_audio_file}")
        return output_audio_file

    _merge_audio_tracks(video_file_path, tracks, output_audio_file)
    return output_audio_file
