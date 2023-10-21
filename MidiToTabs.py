import os
import mido
from mido import MidiFile
from dataclasses import dataclass
import matplotlib.pyplot as plot


@dataclass
class Note:
    name: str
    note: int
    on: bool
    velocity: int
    channel: int
    time: int


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
    important_meta_messages = []
    for current_track in song.tracks:
        for message in current_track:
            # hard coding place to find important meta messages, todo: fix later after working on more midi files
            # add speciifc meta messages to all tracks so that they play the correct tempo/key/etc.
            if current_track.name == 'Blinding Lights (Demo)' and type(message) == mido.midifiles.meta.MetaMessage:
                if message.type == 'key_signature' or \
                        message.type == 'time_signature' or \
                        message.type == 'smpte_offset' or \
                        message.type == 'set_tempo':
                    important_meta_messages.append(message)
                    current_track.remove(message)
        temp_song.tracks.append(important_meta_messages + current_track)
        temp_song.save(f'SplitTrackDepot\\{current_track.name}.mid')
        temp_song = MidiFile()


def main():
    # Read in our selected midi file
    blinding_lights = MidiFile('AUD_DS1340.mid', clip=True)
    # Split into tracks
    song_to_tracks(blinding_lights, 'SplitTrackDepot')
    # We are going to analyze one track within our song
    single_track = MidiFile('SplitTrackDepot/Vocal Guide.mid', clip=True).tracks[0]
    # Print out info about messages within our single track
    # including whether it was a note on or off, what the note
    # was, and the message as a whole.
    print(single_track)
    # Now sort messages based on whether they are note_on or note_off
    notesOn = []
    notesOff = []
    notes = []
    time_counter = 0
    time_seconds = 0
    for message in single_track:
        try:
            time_counter += message.time
            # Calculate the correct time in seconds by doing MIDI Ticks * (Tempo / PPQ)
            # In this case, we have tempo in microseconds, so we divide by 1000000
            # to get tempo in seconds. 480 PPQ is found in the header of the MidiFile
            # "ticks_per_beat" and tempo is found in a MetaMessage in the track
            # named 'set_tempo' as the value tempo
            time_seconds = time_counter * 350877 / 1000000 / 480
        except Exception:
            print("Message without time:" + message)
        if type(message) == mido.midifiles.meta.MetaMessage:
            continue
        if message.type == "note_on":
            tempNote = Note(note_number_to_name(message.note), message.note, True, message.velocity, message.channel, time_seconds)
            notesOn.append(tempNote)
            notes.append(tempNote)
        elif message.type == "note_off":
            tempNote = Note(note_number_to_name(message.note), message.note, False, message.velocity, message.channel, time_seconds)
            notesOff.append(tempNote)
            notes.append(tempNote)
        else:
            pass  # print("Not a Note!")
    # Now that we have separated note_ons and note_offs we need to
    # order them by what the note actually is, but maintain the
    # sequencing for each note
    print("\n\n")
    for note in notes:
        print(note)
    notesOn = sorted(notesOn, key=lambda x: x.name)
    notesOff = sorted(notesOff, key=lambda x: x.name)
    # Now we can pair up each note on and note off in the sequence
    # so that we know when a certain note starts and ends
    pairedNotes = []
    if len(notesOn) == len(notesOff):
        for x in range(len(notesOn)):
            pairedNotes.append((notesOn[x], notesOff[x]))
    print("\n")
    # Print out all of the paired notes
    for pairedNote in pairedNotes:
        print(pairedNote)
    # Graph visualization of our notes
    note_graph_data = []
    # Define data segments
    for pairedNote in pairedNotes:
        note_graph_data.append(((pairedNote[0].time, pairedNote[0].note),
                                (pairedNote[1].time, pairedNote[1].note)))
    # reordering so notes (as points) are in sequence
    note_graph_data = sorted(note_graph_data, key=lambda x: x[0][0])
    # showing just the first 10 notes
    # note_graph_data = note_graph_data[:10]
    # troubleshooting graph points
    for note_graph_point in note_graph_data:
        print(note_graph_point)
    # Create new figure and axis
    _, ax = plot.subplots()
    # Plot each line segment
    for start, end in note_graph_data:
        x_values = [start[0], end[0]]
        y_values = [start[1], end[1]]
        ax.plot(x_values, y_values, marker = 'o', linestyle='-')
    # Set axis labels
    ax.set_xlabel('Time (Seconds)')
    ax.set_ylabel('Note (0-128)')
    ax.set_title('Plot of MIDI Data')
    plot.show()
    return 0


if __name__ == '__main__':
    main()
