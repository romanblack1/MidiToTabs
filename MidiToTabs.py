import os
import mido
from mido import MidiFile


# Splits a given midi song into midi files containing each
# track separately, saves them in the given dest
def song_to_tracks(song: MidiFile, dest: str):
    # Clearing Destination of Midi Files
    for filename in os.listdir(dest):
        file_path = os.path.join(dest, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # Splitting Tracks and Writing Files to dest
    temp_song = MidiFile()
    for current_track in song.tracks:
        temp_song.tracks.append(current_track)
        temp_song.save(f'SplitTrackDepot\\{current_track.name}.mid')
        temp_song = MidiFile()


def main():
    blinding_lights = MidiFile('AUD_DS1340.mid', clip=True)
    song_to_tracks(blinding_lights, 'SplitTrackDepot')
    single_track = MidiFile('SplitTrackDepot/Vocal Guide.mid', clip=True).tracks[0]
    #print(single_track)
    for message in single_track:
        if type(message) == mido.midifiles.meta.MetaMessage:
            continue
        if message.type == "note_on":
            print("Note Begin!")
        elif message.type == "note_off":
            print("Note End!")
        else:
            print("Not a Note!")
        # print(message)
    return 0


if __name__ == '__main__':
    main()
