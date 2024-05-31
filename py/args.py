import argparse

parser = argparse.ArgumentParser()

def _addSrtPathArgs(parser):
    parser.add_argument('-S', '--srt-file-path', type=str, 
                        required=True, 
                        # default="dsdsd2.srt"
                        )
def _addVideoPathArgs(parser):
    parser.add_argument('-v', '--video-file-path',  
                        required=True, 
                        # default='2024-04-22 22-27-37.mkv',
                        type=str)

def parseExtractDialogArgs():
    parser = argparse.ArgumentParser()

    _addVideoPathArgs(parser)
    
    parser.add_argument('-t', '--tracks',           
                        required=True, 
                        # description='Track numbers (zero indexed) that contain voice only',
                        type=int, nargs='+')

    return parser.parse_args()


def parseTranscribeArgs():
    parser = argparse.ArgumentParser()

    parser.add_argument('-a', '--audio-file-path',
                        required=True,
                        # default='output_audio.wav',
                        type=str)

    return parser.parse_args()


def parseSrtEditorArgs():
    parser = argparse.ArgumentParser()

    _addVideoPathArgs(parser)
    _addSrtPathArgs(parser)

    parser.add_argument('-i', '--srt-id', type=int, 
                    required=True, 
                    # default=1
                    )
    parser.add_argument('-s', '--start-offset', type=float, default=0.0)
    parser.add_argument('-e', '--end-offset',   type=float, default=0.0)
    # TODO mutually exclusive. possibley use action groups instead, i.e preview, save, remove
    parser.add_argument("--save",               action='store_true', help="Save edit")
    parser.add_argument("--remove",             action='store_true', help="Remove edit")

    return parser.parse_args()

def parseSplitVideoArgs():
    parser = argparse.ArgumentParser(description='Split a video into multiple clips based on subtitles.')

    _addVideoPathArgs(parser)
    _addSrtPathArgs(parser)
    parser.add_argument("-E", "--encoder", type=str, required=True, help="e.g videotoolbox or nvenc")
    parser.add_argument("--overlay", action='store_true', help="Overlay SRT and timestamps onto clips")

    return parser.parse_args()