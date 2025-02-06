import os
import joblib
import pandas as pd
from mido import MidiFile
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.ensemble import RandomForestClassifier  # Using Random Forest instead of XGBoost
import re  # For cleaning chord names

# Paths
train_midi_folder = "C:/Users/Mateo/Documents/UCE/2024 - 2025/mineria/7200 fichiers MIDI accords piano - Ressource/training"


# Function to parse MIDI files and extract chord data
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
            chords.append({"chord": chord_name, "notes": sorted(notes)})

    return chords


# Process all MIDI files in training folder
midi_data = []
for file in os.listdir(train_midi_folder):
    if file.endswith(".mid"):
        midi_data.extend(parse_midi(os.path.join(train_midi_folder, file)))

# Convert to DataFrame
df = pd.DataFrame(midi_data)

# Encode notes as binary features
mlb = MultiLabelBinarizer()
X = mlb.fit_transform(df['notes'])  # Convert lists to a feature matrix
y = df['chord']

# Train the model with Random Forest
model = RandomForestClassifier(n_estimators=500, max_depth=20, min_samples_split=5, min_samples_leaf=2, random_state=42)
model.fit(X, y)

# Save model and encoder
joblib.dump(model, "chord_classifier.pkl")
joblib.dump(mlb, "notes_encoder.pkl")

print("Model training complete. Model saved as 'chord_classifier.pkl' and encoder as 'notes_encoder.pkl'.")
