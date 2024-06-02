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

def parseDeaggressArgs():
    parser = argparse.ArgumentParser()

    _addSrtPathArgs(parser)
    parser.add_argument("-d", "--deaggress-seconds", required=True, type=float, help="add n seconds of padding around SRTs")

    return parser.parse_args()

def parseSrtEditorArgs():
    parser = argparse.ArgumentParser()

    # global options
    _addSrtPathArgs(parser)
    parser.add_argument('-i', '--srt-id', type=int, 
                    required=True, 
                    # default=1
                    )

    # Create a parent parser for shared arguments
    edit_preview_parent_parser = argparse.ArgumentParser(add_help=False)

    # Add shared arguments to the parent parser
    edit_preview_parent_parser.add_argument('-s', '--start-offset', type=float, default=0.0)
    edit_preview_parent_parser.add_argument('-e', '--end-offset',   type=float, default=0.0)

    # command parser
    subparsers = parser.add_subparsers(dest='command')

    # preview subcommand and arguments
    preview_subparser = subparsers.add_parser('preview', parents=[edit_preview_parent_parser], description="Preview edit")
    _addVideoPathArgs(preview_subparser)

    # edit subcommand and arguments
    subparsers.add_parser('edit', parents=[edit_preview_parent_parser], description="Save edit")

    # remove just uses only global options
    subparsers.add_parser('remove', description="Remove edit")

    return parser.parse_args()

def parseSplitVideoArgs():
    parser = argparse.ArgumentParser(description='Split a video into multiple clips based on subtitles.')

    _addVideoPathArgs(parser)
    _addSrtPathArgs(parser)
    parser.add_argument("-g", "--gpu", type=str, required=True, help="e.g apple or nvidia")
    parser.add_argument("--overlay", action='store_true', help="Overlay SRT and timestamps onto clips")
    parser.add_argument("-r", "--range",
                        required=False, 
                        # description='Range of clips to render',
                        type=int, nargs='+')

    return parser.parse_args()