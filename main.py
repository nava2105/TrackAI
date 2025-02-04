import subprocess
import os


# for 4 stems model use "demucs "file_path""
def separate_audio(file_path, model="htdemucs_6s", output_dir="output", device="cpu"):
    """
    Runs Demucs to separate audio sources from a given file.

    :param file_path: Path to the audio file (MP3, WAV, etc.)
    :param model: Demucs model to use (default is "htdemucs_6s" for 6 stems)
    :param output_dir: Directory where the separated stems will be saved
    :param device: Device to use for processing ("cpu" or "cuda" for GPU)
    """
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


def list_output_files(file_path, model="htdemucs_6s"):
    """
    Lists all output files from Demucs processing.
    """
    output_dir = f"output/{model}/{file_path.replace('.mp3', '')}"
    if not os.path.exists(output_dir):
        print(f"Error: Output directory {output_dir} not found.")
        return []

    files = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]
    if not files:
        print("No output files found.")
        return []

    print("Available output files:")
    for idx, file in enumerate(files):
        print(f"{idx + 1}. {file}")
    return files


def convert_to_midi(wav_file):
    """
    Converts a separated WAV file to MIDI using basic-pitch.

    The MIDI file will be saved inside the same directory as the WAV file.

    :param wav_file: Path to the separated WAV file
    """
    if not os.path.exists(wav_file):
        print(f"Error: File {wav_file} not found.")
        return

    # Get the folder containing the WAV file and create a MIDI subdirectory
    wav_folder = os.path.dirname(wav_file)
    midi_output_dir = os.path.join(wav_folder, "midi")
    os.makedirs(midi_output_dir, exist_ok=True)

    print(f"Converting {wav_file} to MIDI...")

    command = [
        "basic-pitch",
        midi_output_dir,  # Save MIDI inside the same folder as WAV
        wav_file,
        "--save-midi"
    ]

    subprocess.run(command, check=True)
    print(f"MIDI conversion complete. MIDI files saved in {midi_output_dir}.")


if __name__ == "__main__":
    audio_file = "Jim Croce - Time In A Bottle.mp3"

    # separate_audio(audio_file)

    output_files = list_output_files(audio_file)
    if output_files:
        selected_index = int(input("Enter the number of the file to convert to MIDI: ")) - 1
        if 0 <= selected_index < len(output_files):
            selected_file = os.path.join("output", "htdemucs_6s", audio_file.replace('.mp3', ''),
                                         output_files[selected_index])
            print(f"Selected File: {selected_file}")

            # Convert selected WAV file to MIDI and store it in the same directory
            convert_to_midi(selected_file)

        else:
            print("Invalid selection.")
