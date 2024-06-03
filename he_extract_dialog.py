import subprocess
import os

from py.args import parseExtractDialogArgs

def _merge_audio_tracks(input_video, tracks, output_audio):
    # Construct the filter_complex string based on the provided track indices
    input_tracks = ''.join(f'[0:a:{i}]' for i in tracks)
    filter_complex = f"{input_tracks}amerge=inputs={len(tracks)}"

    # Define the ffmpeg command
    ffmpeg_command = [
        'ffmpeg',
        '-y', # overwrites
        '-i', input_video,
        '-filter_complex', filter_complex,
        '-ac', str(len(tracks)),
        '-c:a', 'pcm_s16le',
        output_audio
    ]
    
    # Run the ffmpeg command
    result = subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Check if the command was successful
    if result.returncode == 0:
        print("Audio tracks merged successfully.")
    else:
        print("Error merging audio tracks:")
        print(result.stderr.decode())

def extract_dialog(video_file_path, tracks):
    basename, _ = os.path.splitext(video_file_path)
    output_audio_file = os.path.join(f"{basename}_merged.wav")
    _merge_audio_tracks(video_file_path, tracks, output_audio_file)
    return output_audio_file


if __name__ == "__main__":
    args = parseExtractDialogArgs()
    extract_dialog(args.video_file_path, args.tracks)
