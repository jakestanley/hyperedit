from py.args import parserBatchArgs
from he_extract_dialog import extract_dialog

args = parserBatchArgs()

# TODO if args.video_file_path is a directory, process all files in directory
output_audio_file = extract_dialog(video_file_path=args.video_file_path, tracks=args.tracks)
