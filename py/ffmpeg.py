from py.time import seconds_to_hmsm

def seconds_to_ffmpeg_timestamp(seconds):
    hours, minutes, secs, milliseconds = seconds_to_hmsm(seconds)

    # Format the timestamp as HH:MM:SS,mmm
    timestamp = f"{hours:02}:{minutes:02}:{secs:02}"
    
    return timestamp