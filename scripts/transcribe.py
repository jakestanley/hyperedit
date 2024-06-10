#!/usr/bin/env python3

from scripts.args import parseTranscribeArgs

from hyperedit.transcribe import transcribe

def main():
    args = parseTranscribeArgs()
    transcribe(args.audio_file_path)