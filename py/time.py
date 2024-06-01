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
