from collections import Counter
import os
from mido import MidiFile

train_midi_folder = "C:/Users/Mateo/Documents/UCE/2024 - 2025/mineria/7200 fichiers MIDI accords piano - Ressource/training"

def parse_midi(midi_path):
    midi = MidiFile(midi_path)
    chords = []

    for track in midi.tracks:
        chord_name = None
        notes = []
        for msg in track:
            if msg.type == 'track_name':  # Extract chord name
                chord_name = msg.name.strip()
                chord_name = chord_name.split(" ")[-1]  # Take last substring as chord name
            if msg.type == 'note_on' and msg.velocity > 0:
                notes.append(msg.note)

        if chord_name and notes:
            chords.append(chord_name)  # Only record the chord name

    return chords

# Process all MIDI files and collect chord names
midi_data = []
for file in os.listdir(train_midi_folder):
    if file.endswith(".mid"):
        midi_data.extend(parse_midi(os.path.join(train_midi_folder, file)))

# Count the frequency of each chord
chord_counts = Counter(midi_data)

# Print the results
for chord, count in chord_counts.items():
    print(f"{chord}: {count}")


# To identify missing chords, you can compare chord_counts.keys() with a predefined list of all possible chords.
