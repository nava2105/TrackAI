import os
import random
from mido import MidiFile, MidiTrack, Message

train_midi_folder = "C:/Users/Mateo/Documents/UCE/2024 - 2025/mineria/7200 fichiers MIDI accords piano - Ressource/training"
min_count = 5  # Mínimo de ocurrencias deseadas para cada acorde

# Contador de acordes
chord_counts = {}


def parse_midi(midi_path):
    midi = MidiFile(midi_path)
    chords = []
    for track in midi.tracks:
        chord_name = None
        for msg in track:
            if msg.type == 'track_name':
                chord_name = msg.name.strip().split(" ")[-1]
        if chord_name:
            chords.append(chord_name)
    return chords


# Contar los acordes
for file in os.listdir(train_midi_folder):
    if file.endswith(".mid"):
        chords = parse_midi(os.path.join(train_midi_folder, file))
        for chord in chords:
            chord_counts[chord] = chord_counts.get(chord, 0) + 1

# Identificar acordes con menos de min_count apariciones
chords_to_duplicate = [chord for chord, count in chord_counts.items() if count < min_count]


def modify_and_save_midi(file_path, new_file_path, variation=2):
    midi = MidiFile(file_path)
    new_midi = MidiFile()

    for track in midi.tracks:
        new_track = MidiTrack()
        for msg in track:
            if msg.type == 'note_on' or msg.type == 'note_off':
                # Variar la nota ligeramente hacia arriba o hacia abajo
                msg.note = max(0, min(127, msg.note + random.randint(-variation, variation)))
            new_track.append(msg)
        new_midi.tracks.append(new_track)

    new_midi.save(new_file_path)


# Duplicar y modificar los archivos MIDI
for file in os.listdir(train_midi_folder):
    if file.endswith(".mid"):
        chords = parse_midi(os.path.join(train_midi_folder, file))
        if any(chord in chords_to_duplicate for chord in chords):
            new_file_path = os.path.join(train_midi_folder, "Mod-" + file)
            modify_and_save_midi(os.path.join(train_midi_folder, file), new_file_path)

print("Archivos duplicados y modificados guardados con prefijo 'Mod-'.")
