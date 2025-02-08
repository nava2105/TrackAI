from flask import Flask, render_template, request, redirect, url_for
import os
import subprocess
import yt_dlp

app = Flask(__name__)
UPLOAD_FOLDER = 'songs'
OUTPUT_DIR = 'output'
MIDI_DIR = "midi"
MODEL_NAME = "htdemucs_6s"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
    """Converts a WAV file to MIDI using Basic Pitch if the MIDI file does not already exist."""
    if not os.path.exists(wav_file):
        print(f"❌ Error: File {wav_file} not found.")
        return None

    midi_output_dir = os.path.join(os.path.dirname(wav_file), MIDI_DIR)
    midi_file = os.path.join(midi_output_dir, os.path.basename(wav_file).replace(".wav", "_basic_pitch.mid"))

    if os.path.exists(midi_file):
        print(f"✅ MIDI file already exists: {midi_file}")
        return midi_file

    os.makedirs(midi_output_dir, exist_ok=True)

    print(f"🔄 Converting {wav_file} to MIDI...")

    command = [
        "basic-pitch",
        midi_output_dir,  # Positional argument for output directory
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
    return midi_file

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

    midi_file = convert_to_midi(wav_file_path)
    if midi_file:
        return f"MIDI file created: <a href='{midi_file}' download>Download MIDI</a>"
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
