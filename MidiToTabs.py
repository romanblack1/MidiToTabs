import os
import mido
from mido import MidiFile


def note_number_to_name(note_number):
    # Define a list of note names
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    # Calculate the octave and note index
    octave = note_number // 12
    note_index = note_number % 12
    # Get the note name based on the note index
    note_name = note_names[note_index]
    return f"{note_name}{octave}"


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
    # Read in our selected midi file
    blinding_lights = MidiFile('AUD_DS1340.mid', clip=True)
    # Split into tracks
    song_to_tracks(blinding_lights, 'SplitTrackDepot')
    # We are going to analyze one track within our song
    single_track = MidiFile('SplitTrackDepot/Vocal Guide.mid', clip=True).tracks[0]
    # print(single_track)
    # Print out info about messages within our single track
    # including whether it was a note on or off, what the note
    # was, and the message as a whole. We then print the array
    # of messages sorted by note and then time
    messages = []
    for message in single_track:
        if type(message) == mido.midifiles.meta.MetaMessage:
            continue
        if message.type == "note_on":
            print("Note Begin!")
            print("Note Name and Octave: " + note_number_to_name(message.note))
            messages.append(message)
        elif message.type == "note_off":
            print("Note End!")
            print("Note Name and Octave: " + note_number_to_name(message.note))
            messages.append(message)
        else:
            print("Not a Note!")
        print(message)
    messages = sorted(messages, key=lambda x: (x.note, x.time))
    print("\n")
    for message in messages:
        print(message)
    return 0


if __name__ == '__main__':
    main()
