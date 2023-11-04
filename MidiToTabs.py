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
    half_beat_index: int


@dataclass
class GuitarNote:
    string_name: str
    string_index: int  # number 0-5, 0 representing the high e string
    fret: int
    start_time: int = 0
    half_beat_index: int = 0


@dataclass
class Tab:
    guitar_note_list: list


# Clears the given directory from path of all files
def clear_directory(path):
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)


def print_note_range(paired_notes):
    paired_notes = sorted(paired_notes, key=lambda x: x[0].note)
    print("Min Note: " + str(paired_notes[0][0].note) + ". Max Note: " + str(paired_notes[-1][0].note))


# Translates from MIDI note number (0-128) to name with octave and number
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
    clear_directory(dest)

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
        temp_song.tracks.append(important_meta_messages + current_track)
        temp_song.save(f'SplitTrackDepot\\{current_track.name}.mid')
        temp_song = MidiFile()


# Create notes from the given track
def create_notes(single_track, ticks_to_seconds_ratio, seconds_per_beat):
    notes_on = []
    notes_off = []
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
            time_seconds = time_counter * ticks_to_seconds_ratio
        except Exception:
            print("Message without time:" + message)
        if type(message) == mido.midifiles.meta.MetaMessage:
            continue
        if message.type == "note_on":
            temp_note = Note(note_number_to_name(message.note), message.note,
                             True, message.velocity, message.channel, time_seconds, round(2*time_seconds/seconds_per_beat))
            notes_on.append(temp_note)
        elif message.type == "note_off":
            temp_note = Note(note_number_to_name(message.note), message.note,
                             False, message.velocity, message.channel, time_seconds, round(2*time_seconds/seconds_per_beat))
            notes_off.append(temp_note)
        else:
            pass  # print("Not a Note!")
    return notes_on, notes_off


# Pairs up a note's on and off messages (represented as note
# objects) into a singular tuple with the on note first and
# the off note second
def pair_up_notes(notes_on, notes_off):
    notes_on = sorted(notes_on, key=lambda x: x.name)
    notes_off = sorted(notes_off, key=lambda x: x.name)
    paired_notes = []
    if len(notes_on) == len(notes_off):
        for x in range(len(notes_on)):
            paired_notes.append((notes_on[x], notes_off[x]))
    return paired_notes


def graph_track(paired_notes):
    # Define data segments
    note_graph_data = []
    for paired_note in paired_notes:
        note_graph_data.append(((paired_note[0].time, paired_note[0].note),
                                (paired_note[1].time, paired_note[1].note)))

    # Reordering so notes (as points) are in sequence
    note_graph_data = sorted(note_graph_data, key=lambda x: x[0][0])

    # Print graph data
    # for note_graph_point in note_graph_data:
    #     print(note_graph_point)

    # Create graph
    _, ax = plot.subplots()
    ax.set_xlabel('Time (Seconds)')
    ax.set_ylabel('Note (0-128)')
    ax.set_title('Plot of MIDI Data')

    # Plot each line segment on graph
    for start, end in note_graph_data:
        x_values = [start[0], end[0]]
        y_values = [start[1], end[1]]
        ax.plot(x_values, y_values, marker='o', linestyle='-')

    # Show graph
    plot.show()

    return


def create_guitar_index():
    low_e_string = (40, 57)
    a_string = (45, 62)
    d_string = (50, 67)
    g_string = (55, 72)
    b_string = (59, 76)
    e_string = (64, 81)

    guitar_index = {}
    for note_num in range(40, 82):
        string_fret_combo = []
        if e_string[0] <= note_num <= e_string[1]:
            string_fret_combo.append(GuitarNote("e", 0, note_num - e_string[0]))
        if b_string[0] <= note_num <= b_string[1]:
            string_fret_combo.append(GuitarNote("b", 1, note_num - b_string[0]))
        if g_string[0] <= note_num <= g_string[1]:
            string_fret_combo.append(GuitarNote("g", 2, note_num - g_string[0]))
        if low_e_string[0] <= note_num <= low_e_string[1]:
            string_fret_combo.append(GuitarNote("d", 3, note_num - d_string[0]))
        if a_string[0] <= note_num <= a_string[1]:
            string_fret_combo.append(GuitarNote("a", 4, note_num - a_string[0]))
        if d_string[0] <= note_num <= d_string[1]:
            string_fret_combo.append(GuitarNote("E", 5, note_num - low_e_string[0]))

        guitar_index[note_num] = string_fret_combo

    return guitar_index


def translate_notes(paired_notes, guitar_index):
    guitar_note_list = []
    paired_notes = sorted(paired_notes, key=lambda x: x[0].time)
    for paired_note in paired_notes:
        potential_guitar_notes = guitar_index[paired_note[0].note]
        # todo optimize note picked
        guitar_note = potential_guitar_notes[0]
        guitar_note_list.append(GuitarNote(guitar_note.string_name, guitar_note.string_index,
                                           guitar_note.fret, paired_note[0].time, paired_note[0].half_beat_index))
    return Tab(sorted(guitar_note_list, key=lambda x: x.start_time))


def print_tab(tab):
    guitar_strings = ["e| ", "b| ", "g| ", "d| ", "a| ", "E| "]

    song_len = tab.guitar_note_list[-1].half_beat_index + 2
    note_index = 0
    for time_index in range(song_len):
        # to account for fret nums > 2 characters long (10-17), and no notes at this time tick
        max_string_len = len(guitar_strings[0]) + 1
        current_guitar_note = tab.guitar_note_list[note_index]
        while current_guitar_note and current_guitar_note.half_beat_index == time_index:  # catches notes on this time tick
            fret = str(current_guitar_note.fret)
            guitar_strings[current_guitar_note.string_index] += fret
            max_string_len = max(max_string_len, len(guitar_strings[current_guitar_note.string_index]))
            note_index += 1
            current_guitar_note = tab.guitar_note_list[note_index] if note_index < len(tab.guitar_note_list) else None

        for guitar_string in guitar_strings:
            if len(guitar_string) < max_string_len:  # add dashes to strings that don't have notes at this time tick
                guitar_string + "-" * (max_string_len - len(guitar_string))

    for guitar_string in guitar_strings:
        print(guitar_string)


def main():
    guitar_index = create_guitar_index()

    # Read in our selected midi file
    blinding_lights = MidiFile('AUD_DS1340.mid', clip=True)
    print(blinding_lights)
    print("\n\n\n")

    # Figure out the midi tick to seconds ratio
    tempo = 0
    for message in blinding_lights.tracks[0]:
        if type(message) == mido.midifiles.meta.MetaMessage:
            if message.type == 'set_tempo':
                tempo = message.tempo
                break
    ticks_to_seconds_ratio = tempo / 1000000 / blinding_lights.ticks_per_beat
    seconds_per_beat = blinding_lights.ticks_per_beat * ticks_to_seconds_ratio

    # Split into tracks
    song_to_tracks(blinding_lights, 'SplitTrackDepot')

    # We are going to analyze one track within our song
    single_track = MidiFile('SplitTrackDepot/Vocal Guide.mid', clip=True).tracks[0]

    # Print out info about messages within our single track
    # including whether it was a note on or off, what the note
    # was, and the message as a whole.
    # print(single_track)

    notes_on, notes_off = create_notes(single_track, ticks_to_seconds_ratio, seconds_per_beat)

    # Pair up the notes_on and notes_off that we collected
    paired_notes = pair_up_notes(notes_on, notes_off)
    
    # Print out all of the paired notes
    # for paired_note in paired_notes:
    #     print(paired_note)

    # Graph the track
    graph_track(paired_notes)

    guitar_notes = translate_notes(paired_notes, guitar_index)
    for note in guitar_notes.guitar_note_list:
        print(note)

    print_note_range(paired_notes)
    return 0


if __name__ == '__main__':
    main()
