import subprocess
import os
import mido
import joblib
import pandas as pd

# Load chord classifier model
model = joblib.load("chord_classifier.pkl")
mlb = joblib.load("notes_encoder.pkl")

# Paths
MODEL_NAME = "htdemucs_6s"
OUTPUT_DIR = "output"
MIDI_DIR = "midi"
TIME_THRESHOLD = 50  # Max ticks between notes to group as chords
MERGE_THRESHOLD = 1000  # Max ticks to merge separated notes


def separate_audio(file_path, model=MODEL_NAME, output_dir=OUTPUT_DIR, device="cpu"):
    """Runs Demucs to separate audio sources from a given file."""
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    print(f"Running Demucs on {file_path} using model {model}...")

    command = [
        "demucs", "-n", model,
        "-d", device,
        "--out", output_dir,
        file_path
    ]

    subprocess.run(command, check=True)
    print(f"Separation complete. Output saved in {output_dir}.")


def list_output_files(file_path, model=MODEL_NAME):
    """Lists all output files from Demucs processing."""
    output_path = os.path.join(OUTPUT_DIR, model, file_path.replace(".mp3", "").replace(".wav", ""))
    if not os.path.exists(output_path):
        print(f"Error: Output directory {output_path} not found.")
        return []

    files = [f for f in os.listdir(output_path) if os.path.isfile(os.path.join(output_path, f))]

    if not files:
        print("No output files found.")
        return []

    print("Available instrument files:")
    for idx, file in enumerate(files):
        print(f"{idx + 1}. {file}")

    return files, output_path


def convert_to_midi(wav_file):
    """Converts a WAV file to MIDI using Basic Pitch."""
    if not os.path.exists(wav_file):
        print(f"Error: File {wav_file} not found.")
        return

    midi_output_dir = os.path.join(os.path.dirname(wav_file), MIDI_DIR)
    os.makedirs(midi_output_dir, exist_ok=True)

    print(f"Converting {wav_file} to MIDI...")

    command = [
        "basic-pitch",
        midi_output_dir,
        wav_file,
        "--save-midi"
    ]

    subprocess.run(command, check=True)
    print(f"MIDI conversion complete. MIDI files saved in {midi_output_dir}.")

    return midi_output_dir  # Return the folder where MIDI was saved


def process_midi(midi_path):
    """Processes the MIDI file by grouping notes into chords."""
    midi_file = mido.MidiFile(midi_path)
    filtered_midi = mido.MidiFile()
    filtered_tracks = []

    for track in midi_file.tracks:
        new_track = mido.MidiTrack()
        note_ranges = {}

        for msg in track:
            if msg.type == "note_on" and msg.velocity > 0:
                if msg.note in note_ranges:
                    last_note = note_ranges[msg.note]
                    if msg.time - last_note['end_time'] <= MERGE_THRESHOLD:
                        last_note['end_time'] = msg.time
                    else:
                        note_ranges[msg.note] = {'start_time': msg.time, 'end_time': msg.time}
                else:
                    note_ranges[msg.note] = {'start_time': msg.time, 'end_time': msg.time}

            elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                if msg.note in note_ranges:
                    note_ranges[msg.note]['end_time'] = msg.time

        for note, times in note_ranges.items():
            new_track.append(mido.Message("note_on", note=note, velocity=64, time=times['start_time']))
            new_track.append(mido.Message("note_off", note=note, velocity=0, time=times['end_time']))

        filtered_tracks.append(new_track)

    filtered_midi.tracks.extend(filtered_tracks)
    processed_midi_path = midi_path.replace(".mid", "_processed.mid")
    filtered_midi.save(processed_midi_path)

    print(f"✅ Processed MIDI saved as {processed_midi_path}")
    return processed_midi_path


def reconstruct_midi(original_midi, processed_midi):
    """Reorders the processed MIDI according to the original sequence."""
    original_midi_file = mido.MidiFile(original_midi)
    processed_midi_file = mido.MidiFile(processed_midi)
    reconstructed_midi = mido.MidiFile()
    reconstructed_tracks = []

    original_sequence = [msg.note for track in original_midi_file.tracks for msg in track if
                         msg.type == "note_on" and msg.velocity > 0]
    processed_notes = [msg for track in processed_midi_file.tracks for msg in track if
                       msg.type == "note_on" and msg.velocity > 0]

    new_track = mido.MidiTrack()
    note_map = {}

    for note in original_sequence:
        for msg in processed_notes:
            if msg.note == note and note not in note_map:
                note_map[note] = msg
                break

    for note in original_sequence:
        if note in note_map:
            msg_on = note_map[note]
            msg_off = mido.Message("note_off", note=note, velocity=0, time=msg_on.time + 200)
            new_track.append(msg_on)
            new_track.append(msg_off)

    reconstructed_tracks.append(new_track)
    reconstructed_midi.tracks.extend(reconstructed_tracks)

    reconstructed_path = processed_midi.replace("_processed.mid", "_reconstructed.mid")
    reconstructed_midi.save(reconstructed_path)

    print(f"✅ Reconstructed MIDI saved as {reconstructed_path}")
    return reconstructed_path


def detect_chords(midi_path):
    """Detects chords in the MIDI file using the trained model."""
    midi_file = mido.MidiFile(midi_path)
    chords = []
    current_chord = []
    current_time = 0

    for track in midi_file.tracks:
        for msg in track:
            if msg.type == "note_on" and msg.velocity > 0:
                if current_chord and (msg.time - current_time > TIME_THRESHOLD):
                    chords.append(sorted(current_chord))
                    current_chord = []

                current_chord.append(msg.note)
                current_time = msg.time

    if current_chord:
        chords.append(sorted(current_chord))

    valid_chords = [(chord, model.predict(mlb.transform([chord]))[0] if chord else "Unknown") for chord in chords]

    df = pd.DataFrame(valid_chords, columns=["Notes", "Predicted Chord"])
    df.to_csv("detected_chords.csv", index=False)

    print("✅ Chords saved in detected_chords.csv")
    return "detected_chords.csv"


if __name__ == "__main__":
    audio_file = "Slipknot-Snuff.mp3"

    separate_audio(audio_file)

    files, output_path = list_output_files(audio_file)
    if files:
        selected_index = int(input("Enter the number of the file to convert to MIDI: ")) - 1
        selected_file = os.path.join(output_path, files[selected_index])

        midi_folder = convert_to_midi(selected_file)
        midi_file = os.path.join(midi_folder, "guitar_basic_pitch.mid")

        processed_midi = process_midi(midi_file)
        reconstructed_midi = reconstruct_midi(midi_file, processed_midi)
        detect_chords(reconstructed_midi)
