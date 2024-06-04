def seconds_to_hmsm(seconds):
    # Calculate hours, minutes, and seconds
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)

    return hours, minutes, secs, milliseconds

def seconds_to_output_timestamp(seconds):
    # Format the seconds for output file name
    hours, minutes, secs, milliseconds = seconds_to_hmsm(seconds)
    return f"{hours:02d}-{minutes:02d}-{secs:02d}_{milliseconds:03d}"

def seconds_to_time_remaining(seconds):
    # Calculate hours, minutes, and seconds
    hours, minutes, secs, _ = seconds_to_hmsm(seconds)

    if hours == 0:
        time_remaining = f"{minutes} minutes"
    if hours == 0 and minutes == 0:
        time_remaining = f"{secs} seconds"
    if hours == 0 and minutes == 0 and secs == 0:
        time_remaining = f"nearly done"

    # Format the time remaining for output
    return time_remaining