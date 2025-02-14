import os
import joblib
import pandas as pd
from mido import MidiFile
from sklearn.metrics import accuracy_score, classification_report
from io import StringIO

# Load trained model and encoder
model = joblib.load("chord_classifier.pkl")
mlb = joblib.load("notes_encoder.pkl")

# Path to the test MIDI folder
test_midi_folder = "C:/Users/Mateo/Documents/UCE/2024 - 2025/mineria/7200 fichiers MIDI accords piano - Ressource/training"

# Function to parse MIDI files for testing
def parse_midi(midi_path):
    midi = MidiFile(midi_path)
    parsed_data = []

    for track in midi.tracks:
        chord_name = None
        notes = []
        for msg in track:
            if msg.type == 'track_name':  # Extract chord name
                chord_name = msg.name.strip()
                chord_name = chord_name.split(" ")[-1]
            if msg.type == 'note_on' and msg.velocity > 0:
                notes.append(msg.note)

        if chord_name and notes:
            parsed_data.append({"filename": os.path.basename(midi_path), "chord": chord_name, "notes": sorted(notes)})

    return parsed_data

# Process all MIDI files in the testing folder
test_data = []
for file in os.listdir(test_midi_folder):
    if file.endswith(".mid"):
        test_data.extend(parse_midi(os.path.join(test_midi_folder, file)))

# Convert to DataFrame
df_test = pd.DataFrame(test_data)

# Prepare the input data for testing
X_test = mlb.transform(df_test['notes'])

# Predict chords
df_test["predicted_chord"] = model.predict(X_test)

# Calculate accuracy
accuracy = accuracy_score(df_test["chord"], df_test["predicted_chord"])
print(f"Model Accuracy: {accuracy:.2f}")

# Generate classification report
report = classification_report(df_test["chord"], df_test["predicted_chord"], zero_division=0, output_dict=True)

# Print classes with precision less than 80%
print("Classes with precision below 30%:")
for label, metrics in report.items():
    if isinstance(metrics, dict) and metrics["precision"] < 0.30:
        print(f"{label}: Precision = {metrics['precision']:.2f}, Recall = {metrics['recall']:.2f}, F1-Score = {metrics['f1-score']:.2f}")

print("Classes with precision below 50%:")
for label, metrics in report.items():
    if isinstance(metrics, dict) and metrics["precision"] < 0.50:
        print(f"{label}: Precision = {metrics['precision']:.2f}, Recall = {metrics['recall']:.2f}, F1-Score = {metrics['f1-score']:.2f}")

# Save results
df_test.to_csv("test_results.csv", index=False)
print("Testing complete. Results saved in 'test_results.csv'.")
