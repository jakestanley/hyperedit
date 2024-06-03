#!/usr/bin/env python3
import subprocess
import os

from py.args import parseTranscribeArgs

def _do_transcribe(input_path, output_path):
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
        raise("Error generating SRT:")
        # print(result.stderr.decode())

def transcribe(audio_file_path=None):

    if audio_file_path is None:
        raise Exception("Application error: 'audio_file_path' argument missing")

    basename, _ = os.path.splitext(audio_file_path)
    output_file_path = f"{basename}.srt"

    # TODO: option to overwrite
    if os.path.exists(output_file_path):
        print(f"SRT file already exists at {output_file_path}")
        return output_file_path

    _do_transcribe(audio_file_path, output_file_path)
    return output_file_path

if __name__ == "__main__":
    args = parseTranscribeArgs()
    transcribe(args.audio_file_path)
