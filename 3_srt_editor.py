import subprocess

from py.args import parseSrtEditorArgs
from py.srt import parse_srt, srt_timestamp_to_seconds

args = parseSrtEditorArgs()

video_file_path = args.video_file_path
srt_file_path = args.srt_file_path
srt_id = args.srt_id
start_offset = args.start_offset
end_offset = args.end_offset

srts = parse_srt(srt_file_path)
srt = srts[srt_id - 1]

# TODO add offsets
start = srt_timestamp_to_seconds(srt[1]) - start_offset
end = srt_timestamp_to_seconds(srt[2]) + end_offset

duration = end - start

if args.save:
    # TODO: store edits to a separate file instead of editing the source. 
    #   split video should incorporate the source and any edits
    print("Saving edits")
else:
    command = [
        'mplayer',
        '-ss', f'{start}',
        '-endpos', f'{duration}',
        video_file_path
    ]

    print(f"Playing SRT {srt_id} at range {srt[1]} - {srt[2]} (offsets -{start_offset},{end_offset})")
    subprocess.run(command)
    print(f"Played SRT {srt_id} at range {srt[1]} - {srt[2]} (offsets -{start_offset},{end_offset})")
