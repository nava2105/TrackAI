from flask import Flask, render_template, request, redirect, url_for
import os
import subprocess
import yt_dlp
import mido
import joblib
import pandas as pd

app = Flask(__name__)

model = joblib.load("chord_classifier.pkl")
mlb = joblib.load("notes_encoder.pkl")
UPLOAD_FOLDER = 'songs'
OUTPUT_DIR = 'output'
MIDI_DIR = "midi"
MODEL_NAME = "htdemucs_6s"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
TIME_THRESHOLD = 50
MERGE_THRESHOLD = 1000

def list_songs(directory="songs"):
    """Lists all files in the songs folder."""
    if not os.path.exists(directory):
        return []
    return [f for f in os.listdir(directory) if f.endswith(".mp3") or f.endswith(".wav")]

def download_audio(song_name, song_author):
    """Downloads an audio file from YouTube based on a search query."""
    output_filename = os.path.join(UPLOAD_FOLDER, f"{song_author} - {song_name}")
    search_query = f"{song_name} {song_author} official audio"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_filename,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(f"ytsearch:{search_query}", download=True)
    return output_filename

def separate_audio(file_path, model=MODEL_NAME, output_dir=OUTPUT_DIR, device="cpu"):
    """Runs Demucs to separate audio sources from a given file if it hasn't been separated yet."""
    output_path = os.path.join(output_dir, model, file_path.replace(".mp3", "").replace(".wav", ""))
    output_path = output_path.replace(os.path.sep + "songs" + os.path.sep, os.path.sep)

    if os.path.exists(output_path) and os.listdir(output_path):
        print(f"✅ Audio already separated: {output_path}")
        return output_path  # Skip processing if the folder already exists with files

    if not os.path.exists(file_path):
        print(f"❌ Error: File {file_path} not found.")
        return None

    print(f"🔄 Running Demucs on {file_path} using model {model}...")

    command = [
        "demucs", "-n", model,
        "-d", device,
        "--out", output_dir,
        file_path
    ]

    subprocess.run(command, check=True)
    print(f"✅ Separation complete. Output saved in {output_path}")
    return output_path

def list_output_files(file_path, model=MODEL_NAME):
    """Lists all output files from Demucs processing."""
    output_path = os.path.join(OUTPUT_DIR, model, file_path.replace(".mp3", "").replace(".wav", ""))
    output_path = output_path.replace(os.path.sep + "songs" + os.path.sep, os.path.sep)
    if not os.path.exists(output_path):
        print(f"Error: Output directory {output_path} not found.")
        return []

    files = [f for f in os.listdir(output_path) if os.path.isfile(os.path.join(output_path, f))]

    if not files:
        print("No output files found.")
        return []

    return files, output_path

def convert_to_midi(wav_file):
    """Converts a WAV file to MIDI, processes it, reconstructs it, and extracts chords."""
    if not os.path.exists(wav_file):
        print(f"❌ Error: File {wav_file} not found.")
        return None

    midi_output_dir = os.path.join(os.path.dirname(wav_file), MIDI_DIR)
    midi_file = os.path.join(midi_output_dir, os.path.basename(wav_file).replace(".wav", "_basic_pitch.mid"))

    if os.path.exists(midi_file):
        print(f"✅ MIDI file already exists: {midi_file}")
    else:
        os.makedirs(midi_output_dir, exist_ok=True)
        print(f"🔄 Converting {wav_file} to MIDI...")
        command = [
            "basic-pitch",
            midi_output_dir,  # Output directory
            wav_file,
            "--save-midi"
        ]
        subprocess.run(command, check=True)
        midi_files = [f for f in os.listdir(midi_output_dir) if f.endswith(".mid")]
        if not midi_files:
            print("❌ Error: No MIDI file was created.")
            return None
        midi_file = os.path.join(midi_output_dir, midi_files[0])
        print(f"✅ MIDI conversion complete. MIDI file saved as {midi_file}")

    processed_midi = process_midi(midi_file)
    reconstructed_midi = reconstruct_midi(midi_file, processed_midi)

    # Extract chords after reconstructing the MIDI
    wav_filename = os.path.basename(wav_file).replace(".wav", "")
    chords_csv_path = detect_chords(reconstructed_midi, wav_filename)
    print(chords_csv_path)

    if chords_csv_path:
        print(f"✅ Chord detection complete. Chords saved in {chords_csv_path}")
        return redirect(url_for('show_chords', filename=chords_csv_path))
    return None

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

def detect_chords(midi_path, wav_filename):
    """Detects chords in the MIDI file using the trained model and saves the output in the same folder with a proper name."""
    if not os.path.exists(midi_path):
        print(f"❌ Error: MIDI file {midi_path} not found.")
        return None

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

    # Save CSV with the correct WAV-based name
    output_folder = os.path.dirname(midi_path)
    chords_csv_path = os.path.join(output_folder, f"{wav_filename}_detected_chords.csv")

    df.to_csv(chords_csv_path, index=False)

    print(f"✅ Chords saved in {chords_csv_path}")
    return chords_csv_path

@app.route('/')
def index():
    songs = list_songs(UPLOAD_FOLDER)
    return render_template('index.html', songs=songs)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
    return redirect(url_for('index'))

@app.route('/download', methods=['POST'])
def download():
    song_name = request.form.get('song_name')
    song_author = request.form.get('song_author')
    if song_name and song_author:
        download_audio(song_name, song_author)
    return redirect(url_for('index'))

@app.route('/process/<filename>', methods=['GET'])
def process(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        output_path = separate_audio(file_path)
        if output_path:
            files, _ = list_output_files(filename)
            return render_template('output.html', files=files, output_path=output_path, subdir=os.path.basename(output_path))
    return redirect(url_for('index'))

@app.route('/convert_to_midi/<filename>', methods=['GET'])
def convert(filename):
    subdir = request.args.get('subdir', '').strip()
    if subdir:
        wav_file_path = os.path.join(OUTPUT_DIR, MODEL_NAME, subdir, filename)
    else:
        wav_file_path = os.path.join(OUTPUT_DIR, MODEL_NAME, filename)

    response = convert_to_midi(wav_file_path)
    if response:
        return response
    return redirect(url_for('index'))

@app.route('/chords/<filename>', methods=['GET'])
def show_chords(filename):
    chords_csv_path = filename

    if not os.path.exists(chords_csv_path):
        return "Chord file not found.", 404

    df = pd.read_csv(chords_csv_path)
    chords = df.values.tolist()

    return render_template('chords.html', chords=chords)


if __name__ == '__main__':
    app.run(debug=True)
