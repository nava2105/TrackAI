import mido
import pandas as pd


def generate_midi_from_chords(csv_file, output_midi="recreated_song.mid", tempo=500000):
    """
    Generates a MIDI file from detected chords.

    :param csv_file: Path to the CSV file containing detected chords.
    :param output_midi: Output MIDI file path.
    :param tempo: MIDI tempo (default is 120 BPM).
    """
    df = pd.read_csv(csv_file)

    # Create a new MIDI file
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)

    # Set tempo
    track.append(mido.MetaMessage('set_tempo', tempo=tempo, time=0))

    # Assign fixed duration to each chord
    chord_duration = 480  # Ticks per chord

    for _, row in df.iterrows():
        notes = eval(row["Notes"])  # Convert string list to actual list of notes
        for note in notes:
            track.append(mido.Message("note_on", note=note, velocity=64, time=0))  # Play all notes together

        track.append(
            mido.Message("note_off", note=notes[0], velocity=0, time=chord_duration))  # Delay before next chord
        for note in notes[1:]:
            track.append(mido.Message("note_off", note=note, velocity=0, time=0))  # Turn off remaining notes

    # Save the MIDI file
    mid.save(output_midi)
    print(f"✅ Recreated MIDI saved as {output_midi}")

    return output_midi

generate_midi_from_chords("detected_chords.csv")