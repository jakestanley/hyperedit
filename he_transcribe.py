import subprocess
import os

from py.args import parseTranscribeArgs

def transcribe(input_path, output_path):
    vosk_command = [
        'vosk-transcriber',
        '-i', input_path,
        '-t', 'srt',
        '-o',
        output_path
    ]

    # Run the ffmpeg command
    result = subprocess.run(vosk_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Check if the command was successful
    if result.returncode == 0:
        print("Generated SRT successfully")
    else:
        print("Error generating SRT:")
        print(result.stderr.decode())

args = parseTranscribeArgs()

directory = os.path.dirname(args.audio_file_path)
basename, _ = os.path.splitext(args.audio_file_path)
output_path = f"{basename}.srt"

transcribe(args.audio_file_path, output_path)
