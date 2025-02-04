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


if __name__ == "__main__":
    # Example usage
    audio_file = "Ladytron - Destroy Everything You Touch.mp3"
    separate_audio(audio_file)
