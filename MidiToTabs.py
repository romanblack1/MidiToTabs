import math
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
    quarter_beat_index: int


@dataclass
class GuitarNote:
    string_name: str
    string_index: int  # number 0-5, 0 representing the high e string
    fret: int
    start_time: int = 0
    quarter_beat_index: int = 0


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
    important_meta_messages = []
    channels_dict = {}
    for track_index in range(len(song.tracks)):
        total_time = 0
        for message in song.tracks[track_index]:
            total_time += message.time

            # hard coding place to find important meta messages, todo: fix later after working on more midi files
            # add speciifc meta messages to all tracks so that they play the correct tempo/key/etc.
            if track_index == 0 and type(message) == mido.midifiles.meta.MetaMessage:
                if message.type == 'key_signature' or \
                        message.type == 'time_signature' or \
                        message.type == 'smpte_offset' or \
                        message.type == 'set_tempo':
                    important_meta_messages.append(message)
            elif type(message) == mido.messages.messages.Message and message.type != 'sysex':
                try:
                    channels_dict.setdefault(message.channel, (important_meta_messages.copy(), 0))
                    message.time = total_time - channels_dict[message.channel][1]
                    channels_dict[message.channel][0].append(message)
                    channels_dict[message.channel] = (channels_dict[message.channel][0], total_time)
                except:
                    print(message)
        for channel in channels_dict:
            temp_song = MidiFile()
            temp_song.tracks.append(important_meta_messages + channels_dict[channel][0])
            temp_song.ticks_per_beat = 480
            temp_song.save(f'SplitTrackDepot\\{channel}.mid')


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
                             True, message.velocity, message.channel, time_seconds, round(4*time_seconds/seconds_per_beat))
            notes_on.append(temp_note)
        elif message.type == "note_off":
            temp_note = Note(note_number_to_name(message.note), message.note,
                             False, message.velocity, message.channel, time_seconds, round(4*time_seconds/seconds_per_beat))
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
    current_time = 0
    occupied_strings = set()
    for paired_note in paired_notes:
        if paired_note[0].note not in range(40, 82):
            continue
        potential_guitar_notes = guitar_index[paired_note[0].note]
        if current_time != paired_note[0].quarter_beat_index:
            current_time = paired_note[0].quarter_beat_index
            occupied_strings = set()

        # todo optimize note picked
        guitar_note = None
        for i in range(len(potential_guitar_notes)):
            if potential_guitar_notes[i].string_index not in occupied_strings:
                guitar_note = potential_guitar_notes[i]
                occupied_strings.add(guitar_note.string_index)
                break
        if guitar_note is not None:
            guitar_note_list.append(GuitarNote(guitar_note.string_name, guitar_note.string_index, guitar_note.fret,
                                               paired_note[0].time, paired_note[0].quarter_beat_index))
    return Tab(sorted(guitar_note_list, key=lambda x: x.start_time))


def print_tab(tab, time_sig_numerator):
    guitar_strings = ["e| ", "b| ", "g| ", "d| ", "a| ", "E| "]

    quarter_beats_per_measure = time_sig_numerator * 4
    last_beat_index = tab.guitar_note_list[-1].quarter_beat_index
    song_len = last_beat_index + quarter_beats_per_measure - (last_beat_index % quarter_beats_per_measure) + 1
    note_index = 0
    for time_index in range(1, song_len):
        # to account for fret nums > 2 characters long (10-17), and no notes at this time tick
        max_string_len = len(guitar_strings[0]) + 1
        current_guitar_note = tab.guitar_note_list[note_index] if note_index < len(tab.guitar_note_list) else None
        while current_guitar_note and current_guitar_note.quarter_beat_index == time_index:  # catches notes on this time tick
            fret = str(current_guitar_note.fret)
            guitar_strings[current_guitar_note.string_index] += fret
            max_string_len = max(max_string_len, len(guitar_strings[current_guitar_note.string_index]))
            note_index += 1
            current_guitar_note = tab.guitar_note_list[note_index] if note_index < len(tab.guitar_note_list) else None

        for guitar_string_index in range(len(guitar_strings)):
            # add dashes to strings that don't have notes at this time tick
            if len(guitar_strings[guitar_string_index]) < max_string_len:
                num_dashes = (max_string_len - len(guitar_strings[guitar_string_index]))
                guitar_strings[guitar_string_index] += ("-" * num_dashes)

        if time_index % quarter_beats_per_measure == 0:
            for guitar_string_index in range(len(guitar_strings)):
                guitar_strings[guitar_string_index] += "|"
        if time_index % (quarter_beats_per_measure * 8) == 0:
            print_tab_line(guitar_strings)
            guitar_strings = ["e| ", "b| ", "g| ", "d| ", "a| ", "E| "]

    print_tab_line(guitar_strings)


def print_tab_line(guitar_strings):
    for guitar_string in guitar_strings:
        print(guitar_string)
    print()


def main():
    guitar_index = create_guitar_index()

    # Read in our selected midi file
    # midi_song = MidiFile('blinding_lights.mid', clip=True)
    midi_song = MidiFile('here_comes_the_sun.mid', clip=True)
    # print(midi_song)
    # print("\n\n\n")

    # Figure out the midi tick to seconds ratio
    tempo = 0
    time_sig_numerator = 0
    found_tempo = False
    found_numerator = False
    for message in midi_song.tracks[0]:
        if type(message) == mido.midifiles.meta.MetaMessage:
            if message.type == 'set_tempo':
                tempo = message.tempo
                found_tempo = True
                if found_tempo and found_numerator:
                    break
            if message.type == 'time_signature':
                time_sig_numerator = message.numerator
                found_numerator = True
                if found_tempo and found_numerator:
                    break
    ticks_to_seconds_ratio = tempo / 1000000 / midi_song.ticks_per_beat
    seconds_per_beat = midi_song.ticks_per_beat * ticks_to_seconds_ratio

    # BPM of song
    # print(math.pow(seconds_per_beat, -1) * 60)

    # Split into tracks
    song_to_tracks(midi_song, 'SplitTrackDepot')

    # We are going to analyze one track within our song
    single_track = MidiFile('SplitTrackDepot/0.mid', clip=True).tracks[0]

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
    # graph_track(paired_notes)

    guitar_tab = translate_notes(paired_notes, guitar_index)
    # for note in guitar_tab.guitar_note_list:
    #     print(note)

    # print_note_range(paired_notes)

    print_tab(guitar_tab, time_sig_numerator)

    return 0


if __name__ == '__main__':
    main()
