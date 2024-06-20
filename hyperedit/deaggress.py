#!/usr/bin/env python3
import os

from hyperedit.srt import parse_srt, deaggress_ranges_by_seconds, write_srt, create_srt_entry

def deaggress(
        srt_file_path=None,
        deaggress_seconds=1,
        overwrite=False,
        output_path = None):

    if not srt_file_path:
        raise Exception("SRT file path is required")

    if not os.path.exists(srt_file_path):
        raise(f"File {srt_file_path} does not exist")

    basename, _ = os.path.splitext(srt_file_path)
    if not output_path:
        output_path = f"{basename}_deaggressed_{deaggress_seconds}.srt"

    if os.path.exists(output_path) and not overwrite:
        raise Exception(f"Deaggressed SRT by {deaggress_seconds} already exists at {output_path}")

    print(f"Deaggressing SRT by {deaggress_seconds}")

    time_ranges = parse_srt(srt_file_path)
    print(f"Source SRTs: {len(time_ranges)}")
    time_ranges = deaggress_ranges_by_seconds(time_ranges, deaggress_seconds)
    print(f"Deaggressed SRTS: {len(time_ranges)}")

    # reorder and format
    srt_entries = []
    srt_id = 1
    for entry in time_ranges:
        srt_entries.append(create_srt_entry(srt_id, entry[1], entry[2], 'unused text'))
        srt_id += 1

    write_srt(output_path, srt_entries)
    return output_path
