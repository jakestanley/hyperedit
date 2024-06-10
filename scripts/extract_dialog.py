from scripts.args import parseExtractDialogArgs

from hyperedit.extract_dialog import extract_dialog

def main():
    args = parseExtractDialogArgs()
    extract_dialog(args.video_file_path, args.tracks)
