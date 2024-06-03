import argparse

parser = argparse.ArgumentParser()

def _addOverwriteArgs(parser):
    parser.add_argument('-o', '--overwrite',
                        action='store_true',
                        default=False
                        )

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
    
def _addPlayerArgs(parser):
    parser.add_argument('-p', '--player', type=str, 
                        default='mplayer'
                        )
    
def _addSrtIdArgs(parser):
    parser.add_argument('-i', '--srt-id', type=int, 
                        required=True)
    
def _addPreviewArgs(parser):
    parser.add_argument("--preview", 
                        action='store_true', 
                        help="Overlay SRT and timestamps onto clips and used fast preset")

def _addRangeArgs(parser):
    parser.add_argument("-r", "--range",
                        required=False, 
                        # description='Range of clips to render',
                        type=int, nargs='+')

def _addDeaggressArgs(parser):
    parser.add_argument("-d", "--deaggress-seconds", 
                        required=True, 
                        type=float, 
                        help="add n seconds of padding around SRTs")
    
def _addStartEndOffsetArgs(parser):
    parser.add_argument('-s', '--start-offset', type=float, default=0.0)
    parser.add_argument('-e', '--end-offset',   type=float, default=0.0)

def _addTracksArgs(parser):
    parser.add_argument('-t', '--tracks',           
                        required=True, 
                        # description='Track numbers (zero indexed) that contain voice only',
                        type=int, nargs='+')
    
def _addGpuArgs(parser):
    parser.add_argument("-g", "--gpu", 
                        type=str, 
                        required=True, 
                        help="e.g apple or nvidia")

def parseExtractDialogArgs():
    parser = argparse.ArgumentParser()

    _addVideoPathArgs(parser)
    _addTracksArgs(parser)

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
    _addOverwriteArgs(parser)
    _addDeaggressArgs(parser)

    return parser.parse_args()

def parseSrtEditorArgs():
    parser = argparse.ArgumentParser()

    # command parser
    subparsers = parser.add_subparsers(dest='command')

    # preview subcommand and arguments
    preview_subparser = subparsers.add_parser('preview', description="Preview edit")
    _addSrtPathArgs(preview_subparser)
    _addVideoPathArgs(preview_subparser)
    _addPlayerArgs(preview_subparser)
    _addSrtIdArgs(preview_subparser)
    _addStartEndOffsetArgs(preview_subparser)

    # edit subcommand and arguments
    edit_subparser = subparsers.add_parser('edit', description="Save edit")
    _addSrtPathArgs(edit_subparser)
    _addSrtIdArgs(edit_subparser)
    _addStartEndOffsetArgs(edit_subparser)

    # remove just uses only global options
    remove_subparser = subparsers.add_parser('remove', description="Remove edit")
    _addSrtIdArgs(remove_subparser)

    return parser.parse_args()

def parseSplitVideoArgs():
    parser = argparse.ArgumentParser(description='Split a video into multiple clips based on subtitles.')

    _addVideoPathArgs(parser)
    _addSrtPathArgs(parser)
    _addOverwriteArgs(parser)
    _addGpuArgs(parser)
    _addPreviewArgs(parser)
    _addRangeArgs(parser)

    return parser.parse_args()

def parseBatchArgs():
    parser = argparse.ArgumentParser(description='Batch process hyperedit operations')
    _addVideoPathArgs(parser)
    _addTracksArgs(parser)
    _addDeaggressArgs(parser)
    _addOverwriteArgs(parser)
    _addPreviewArgs(parser)
    _addRangeArgs(parser)
    _addGpuArgs(parser)

    return parser.parse_args()
