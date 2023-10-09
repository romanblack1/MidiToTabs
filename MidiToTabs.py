from mido import MidiFile


def main():
    file = MidiFile('', clip=True)
    file.print_tracks()
    return 1
