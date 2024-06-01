from py.time import seconds_to_hmsm

def get_params_for_gpu(gpu):
    if str.lower(gpu) == 'apple':
        return {
            'encoder': 'h264_videotoolbox',
            'hwaccel': 'videotoolbox',
            'preset_param': '-quality',
            'fast_preset': 'fast',
            'quality_preset': 'high'
        }

    elif str.lower(gpu) == 'nvidia':
        return {
            'encoder': 'h264_nvenc',
            'hwaccel': 'cuvid',
            'preset_param': '-preset',
            'fast_preset': 'llhp', # low latency high performance
            'quality_preset': 'llhq' # low latency high quality
        }
    else:
        raise Exception(f"Invalid GPU: {gpu}")

def seconds_to_ffmpeg_timestamp(seconds):
    hours, minutes, secs, milliseconds = seconds_to_hmsm(seconds)

    # Format the timestamp as HH:MM:SS,mmm
    timestamp = f"{hours:02}:{minutes:02}:{secs:02}"
    
    return timestamp