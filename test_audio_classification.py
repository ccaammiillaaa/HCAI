import whisper
import wave
import numpy as np
from record_and_ASR_test import StreamParams, Recorder
from main import classify_text
import os
from scipy import signal

print("=== Audio Recording + Transcription + Classification Test ===\n")

# Step 1: Record audio
print("Recording will start in 3 seconds...")
print("Please say one of: 'train', 'teddy bear', 'robot', or something else")
import time
time.sleep(3)

stream_params = StreamParams()
recorder = Recorder(stream_params)
recorder.record(5, "audio.wav")

# Check file size
file_size = os.path.getsize("audio.wav")
print(f"\nAudio file size: {file_size} bytes")

# Step 2: Load and transcribe audio
print("Loading audio file...")
with wave.open("audio.wav", "rb") as wav_file:
    print(f"Sample rate: {wav_file.getframerate()}")
    print(f"Channels: {wav_file.getnchannels()}")
    print(f"Frames: {wav_file.getnframes()}")
    print(f"Duration: {wav_file.getnframes() / wav_file.getframerate():.2f} seconds")
    
    sample_rate = wav_file.getframerate()
    frames = wav_file.readframes(wav_file.getnframes())
    audio_data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
    
    # Convert stereo to mono if needed
    if wav_file.getnchannels() == 2:
        audio_data = audio_data.reshape(-1, 2).mean(axis=1)
    
    print(f"Audio data shape: {audio_data.shape}")
    print(f"Audio data range: [{audio_data.min():.3f}, {audio_data.max():.3f}]")

# Resample to 16kHz (Whisper's expected sample rate)
if sample_rate != 16000:
    print(f"Resampling from {sample_rate}Hz to 16000Hz...")
    num_samples = int(len(audio_data) * 16000 / sample_rate)
    audio_data = signal.resample(audio_data, num_samples)
    print(f"Resampled audio shape: {audio_data.shape}")

print("\nTranscribing...")
speech_model = whisper.load_model("tiny.en")
transcript = speech_model.transcribe(audio=audio_data)
transcribed_text = transcript["text"]

# Step 3: Classify the transcription
print("\n--- Results ---")
print(f"Transcription: '{transcribed_text}'")

category = classify_text(transcribed_text)
print(f"Classification: '{category}'")

print("\n Complete pipeline test successful!")