import subprocess
import os

def _do_transcribe(input_path, output_path):
    vosk_command = [
        'vosk-transcriber',
        '-i', input_path,
        '-t', 'srt',
        '-o',
        output_path
    ]

    # Run the ffmpeg command
    with open('vosk-transcriber.log', 'w') as log:
        result = subprocess.run(vosk_command, stdout=log, stderr=log)

    # Check if the command was successful
    if result.returncode == 0:
        print("Generated SRT successfully")
    else:
        raise("Error generating SRT:")
        # print(result.stderr.decode())

def transcribe(audio_file_path=None, to_file=None):

    if audio_file_path is None:
        raise Exception("Application error: 'audio_file_path' argument missing")

    if to_file:
        output_file_path = to_file
    else:
        basename, _ = os.path.splitext(audio_file_path)
        output_file_path = f"{basename}.srt"

    # TODO: option to overwrite
    if os.path.exists(output_file_path):
        print(f"SRT file already exists at {output_file_path}")
        return output_file_path

    _do_transcribe(audio_file_path, output_file_path)
    return output_file_path
