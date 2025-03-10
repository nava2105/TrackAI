# TrackAI: Note and Chord Recognition System using Classification Models
![Python](https://img.shields.io/badge/python-3.9-%233776AB.svg?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-1.1.2-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-1.3.3-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/scikit--learn-0.24.2-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Whisper](https://img.shields.io/badge/Whisper-OpenAI-%23000000.svg?style=for-the-badge&logo=openai&logoColor=white)

## Table of Contents
1. [Abstract](#abstract)
2. [Theoretical Framework](#theoretical-framework)
3. [Methodology](#model-evaluation)
4. [Deployment](#deployment)
5. [Technical Implementation](#technical-implementation)
6. [Installation](#installation)
7. [Usage](#usage)

## Abstract
TrackAI is an AI-based system designed to recognize musical notes and chords from audio files in WAV and MIDI formats. By leveraging signal processing and machine learning techniques, the system enables automated music transcription and analysis for musicians, composers, and sound analysts. This document discusses the feature extraction methods, classification model implementations, and evaluation results across different musical genres, along with future improvements.

## Theoretical Framework
- **Data Mining**: Used to discover patterns in large datasets, aiding in music analysis.
- **AI in Music**: Machine learning, particularly deep learning, is effective in analyzing audio signals and classifying musical elements.
- **Audio Signal Processing**: Fourier transforms and source separation techniques help extract individual instrument sounds from recordings.

## Methodology
TrackAI follows the CRISP-DM methodology:
1. **Business Understanding**: Develop a data mining model to classify notes and chords from audio files.
2. **Data Understanding & Preparation**: WAV files allow high-quality source separation, while MIDI files facilitate structured analysis.
3. **Modeling**: Using a dataset of 2590 MIDI files, augmented to 6965, models were trained to classify chords with different machine learning algorithms.

## Model Evaluation
Various classification models were tested:
- **Neural Networks**: 87% accuracy, best performer
- **Random Forest**: 86%
- **SVM**: 86%
- **K-Nearest Neighbors**: 85%
- **Logistic Regression**: 82%
- **Naïve Bayes**: 75%

## Deployment
TrackAI processes audio files by:
- **Source Separation**: Uses htdemucs_6s (Meta AI) to split audio into six components (guitar, bass, percussion, keyboard, vocals, others).
- **MIDI Conversion**: Uses basic-pitch (Spotify) to transcribe audio into MIDI.
- **Chord Identification**: Compares MIDI notes against a trained classification model.
- **Lyric Transcription**: Uses Whisper (OpenAI) for text extraction.

A prototype was built using Flask (Python) to create a songbook generator, displaying chords alongside lyrics.

## Technical Implementation
TrackAI is developed in Python 3.9, utilizing:
- **Demucs** for audio source separation.
- **Basic-pitch** for MIDI conversion.
- **Scikit-learn** for classification models.
- **Mido** for MIDI file manipulation.
- **Flask** for the web interface.
- **Pandas & Joblib** for data handling.

## Installation
### Prerequisites
- **Python 3.9**: Ensure that Python is installed and configured in your system.

### Installation

- **Clone the repository**
  ```bash
  git clone https://github.com/nava2105/TrackAI.git
  cd TrackAI
  ```
- **Required Libraries**: Install the necessary libraries using pip:
  ```bash
  pip install -r requirements.txt
  ```
- **Run the application**
  ```bash
  python app.py
  ```
- **Access the application:** Open your web browser and navigate to http://localhost:5000

## Usage
Once the application is up and running, you can interact with the system by uploading audio files for processing, generating lyrics, and viewing chords.
