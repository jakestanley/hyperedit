#!/usr/bin/env python3
import subprocess
import argparse
from py.ffmpeg import get_params_for_gpu

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
    with open('ffmpeg-concat.log', 'w') as log:
        e = subprocess.run(cmd, stdout=log, stderr=log)
        if e.returncode != 0:
            raise(f"Error concatenating clips: ffmpeg returned exit code {e.returncode}")

if __name__ == '__main__':
    print("Warning: Direct execution not yet officially supported. This is only for quickly merging files")
    parser = argparse.ArgumentParser(description="Concatenate files")
    parser.add_argument('-f', '--files', type=str, nargs='+', help="File list of output files to concatenate")
    args = parser.parse_args()

    if not args.files:
        raise Exception("No files specified")

    create_file_list(args.files, 'tmp-concat-list.txt')
    concatenate_clips('tmp-concat-list.txt', 'output.mp4', 'nvidia')