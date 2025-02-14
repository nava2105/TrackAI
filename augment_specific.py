import os
import random
from mido import MidiFile, MidiTrack, Message

from data_augmention import chords_to_duplicate

train_midi_folder = "C:/Users/Mateo/Documents/UCE/2024 - 2025/mineria/7200 fichiers MIDI accords piano - Ressource/training"

# Updated list of chords to duplicate
# chords_to_duplicate = [
#     "A#6", "A2", "AM7", "Aadd9", "Ab6", "Ab69", "Ab7", "Ab7+11", "Ab7-5", "Ab7sus4", "Ab9", "Ab9sus4", "AbM7",
#     "AbM7+5", "Abadd11", "Abadd9", "Abdim6", "Abm69", "Abm7", "Abm9", "Abmadd9", "Abmaj9", "Absus2", "Absus4",
#     "Amaj7", "Amaj9", "B2", "Badd9", "Bb2", "Bb7-5", "BbM7", "Bbadd9", "Bbdim6", "Bbm7-5", "Bbmaj7", "Bbmaj9",
#     "Bmaj7", "Bmaj9", "Bsus2", "C#2", "C#6", "C#69", "C#7+11", "C#7+5", "C#7-5", "C#7-9", "C#7sus4", "C#M7+5",
#     "C#add11", "C#dim6", "C#m69", "C#m7", "C#m7-5", "C#m9", "C#maj7", "C#sus4", "C2", "Cadd9", "Cb", "Cb69",
#     "Cb7-5", "Cbsus2", "Cmaj7", "D#69", "D#9sus4", "D#m7-5", "D2", "DM9", "Dadd9", "Db2", "Db7", "Db9",
#     "Db9sus4", "DbM9", "Dbadd9", "Dbm6", "DbmM7", "Dbmadd9", "Dbmaj7", "Dbsus2", "Dmaj7", "Dmaj9", "E2",
#     "Eadd9", "Eb2", "Eb6", "Eb69", "Eb7", "Eb7+11", "Eb7+5", "Eb7-5", "Eb7-9", "Eb7sus4", "Eb9", "Eb9sus4",
#     "EbM7+5", "Ebadd11", "Ebadd9", "Ebdim6", "Ebm6", "Ebm69", "Ebm7", "Ebm7-5", "Ebm9", "EbmM7", "Ebmadd9",
#     "Ebmaj7", "Ebmaj9", "Ebsus2", "Ebsus4", "Emaj7", "Emaj9", "F#2", "F#6", "F#69", "F#7", "F#7+11", "F#7+5",
#     "F#7-5", "F#7-9", "F#7sus4", "F#9", "F#9sus4", "F#M7+5", "F#add11", "F#add9", "F#dim6", "F#m6", "F#m69",
#     "F#m7-5", "F#mM7", "F#madd9", "F#maj7", "F#maj9", "F#sus2", "F#sus4", "F2", "Fadd9", "G#7+5", "G#7-9",
#     "G#m6", "G#m7", "G#m7-5", "G#m9", "G#mM7", "G2", "Gadd9", "Gb7+11", "GbM9", "Gmaj7", "Gmaj9"
# ]
# chords_to_duplicate = [
#     "Gsus2"
# ]
# chords_to_duplicate = [
#     "A2", "AM7", "AM9", "Abm9", "Amaj7", "Amaj9", "BM7", "BM9", "Bb2", "BbM7", "BbM9",
#     "Bbmaj7", "Bbmaj9", "Bmaj7", "Bmaj9", "CM7", "CM9", "Cadd9", "D#m9", "DM9",
#     "Dadd9", "Dmaj9", "E2", "EM7", "EM9", "EbM7", "EbM9", "Ebm9", "Ebmaj7", "Ebmaj9",
#     "FM7", "FM9", "Fadd9", "G#m9", "GM7", "GM9", "Gadd9"
# ]
chords_to_duplicate = [
    "Dbm7", "D#7-9", "D#7sus4", "Dbmaj9"
]

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


# Duplicate and modify only MIDI files containing chords from the updated list
for file in os.listdir(train_midi_folder):
    if file.endswith(".mid"):
        chords = parse_midi(os.path.join(train_midi_folder, file))
        if any(chord in chords_to_duplicate for chord in chords):
            new_file_path = os.path.join(train_midi_folder, "Aug-" + file)
            modify_and_save_midi(os.path.join(train_midi_folder, file), new_file_path)
            print(f"Archivo duplicado y modificado: {new_file_path}")

print("Duplicación y modificación de archivos completada.")
