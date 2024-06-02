import os

from py.srt import parse_srt, deaggress, write_srt, create_srt_entry
from py.args import parseDeaggressArgs

args = parseDeaggressArgs()

srt_file_path = args.srt_file_path

if not os.path.exists(srt_file_path):
    raise(f"File {srt_file_path} does not exist")

directory = os.path.dirname(srt_file_path)
basename, _ = os.path.splitext(srt_file_path)
output_path = f"{basename}_deaggressed_{args.deaggress_seconds}.srt"

if os.path.exists(output_path) and not args.overwrite:
    raise Exception(f"Deaggressed SRT by {args.deaggress_seconds} already exists at {output_path}")

print(f"Deaggressing SRT by {args.deaggress_seconds}")

time_ranges = parse_srt(srt_file_path)
print(f"Source SRTs: {len(time_ranges)}")
time_ranges = deaggress(time_ranges, args.deaggress_seconds)
print(f"Deaggressed SRTS: {len(time_ranges)}")

# reorder and format
srt_entries = []
srt_id = 1
for entry in time_ranges:
    srt_entries.append(create_srt_entry(srt_id, entry[1], entry[2], 'unused text'))
    srt_id += 1

write_srt(output_path, srt_entries)
