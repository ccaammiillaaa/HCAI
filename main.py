import whisper
import wave
import numpy as np
import scipy.signal as signal
from dataclasses import dataclass, asdict
from record_and_ASR_test import StreamParams, Recorder
import pyaudio
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import socket
import threading
import os
import time

# Initialize stop flag
stop_server_thread = False

# the LLM
model = OllamaLLM(model="llama3.1")

prompt = ChatPromptTemplate.from_messages([
    ("system",
    """
    You are a classifier. Categorize the user's sentence into exactly ONE of these:

    - Train
    - Teddy Bear
    - Robot
    - Could not understand

    Rules:
    1. Output ONLY the category name.
    2. Do not explain your reasoning.
    3. If unclear: "Could not understand".
    """
    ),
    ("human", "{input}")
])

chain = prompt | model

def classify_text(text: str) -> str:
    output = chain.invoke({"input": text})
    return output.strip()

#def send_dummy_messages_to_unity():
#    """Send test messages to Unity without audio recording"""
#    HOST, PORT = "127.0.0.1", 25001
#    
#    test_messages = [
#        "Train",
#        "Teddy Bear", 
#        "Robot",
#        "Could not understand",
#        "Train",
#        "Robot"
#    ]
#    
#    try:
#        print(f"Connecting to Unity at {HOST}:{PORT}...")
#        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#        s.connect((HOST, PORT))
#        print("✅ Connected to Unity\n")
#        
#        # Send initial connection message
#          s.sendall(b"Python dummy test client")
#        time.sleep(1)
        
        # Send test messages
#        for i, message in enumerate(test_messages, 1):
#           print(f"Sending {i}/{len(test_messages)}: '{message}'")
    #         s.sendall(message.encode("utf-8"))
    #         time.sleep(2)  # Wait 2 seconds between messages
        
    #     print("\n✅ All dummy messages sent!")
        
    #     # Send stop signal
    #     time.sleep(1)
    #     s.sendall(b"stop")
    #     s.close()
    #     print("Connection closed.")
        
    # except Exception as e:
    #     print(f"❌ Error: {e}")

# # Only run socket code if this file is run directly
# if __name__ == "__main__":
#     import sys
    
#     # Check command line argument
#     if len(sys.argv) > 1 and sys.argv[1] == "--test":
#         print("=== Running Dummy Message Test ===\n")
#         send_dummy_messages_to_unity()
#     else:
#         # Normal operation with audio recording
#         HOST, PORT = "127.0.0.1", 25001
#         data = "LLM classifier connected"

# Only run socket code if this file is run directly
if __name__ == "__main__":
    # Normal operation with audio recording
    HOST, PORT = "127.0.0.1", 25001
    data = "LLM classifier connected"
       
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect((HOST, PORT))
        s.sendall(data.encode("utf-8"))
        print("Connected to Unity server")
    except:
        print("A socket exception occurred") 

    def listen_to_server_loop_func():
        global stop_server_thread
        while not stop_server_thread:
            try:
                data = s.recv(1024)
                if not data:
                    break
                stringdata = data.decode('utf-8')
                handleServerMessage(stringdata)
            except Exception as e:
                print(f"Error receiving data: {e}")
                break
            
    listen_thread = threading.Thread(target=listen_to_server_loop_func)
    listen_thread.start()

    # Load Whisper model
    speech_model = whisper.load_model("tiny.en")

    #Server message handler
    def handleServerMessage(stringdata):
        global stop_server_thread

        if stringdata == "stop":
            s.close()
            stop_server_thread = True

        elif stringdata == "speechstart":
            print("🎤 Starting recording...")
            stream_params = StreamParams()
            recorder = Recorder(stream_params)
            recorder.record(5, "audio.wav")
            print("✅ Recording complete")

        elif stringdata == "speechstop":
            print("📝 Transcribing audio...")
                
            # Load and resample audio (like in test_audio_classification.py)
            with wave.open("audio.wav", "rb") as wav_file:
                sample_rate = wav_file.getframerate()
                frames = wav_file.readframes(wav_file.getnframes())
                audio_data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
                    
                # Convert stereo to mono
                if wav_file.getnchannels() == 2:
                    audio_data = audio_data.reshape(-1, 2).mean(axis=1)
                
            # Resample to 16kHz for Whisper
            if sample_rate != 16000:
                num_samples = int(len(audio_data) * 16000 / sample_rate)
                audio_data = signal.resample(audio_data, num_samples)
                
            transcript = speech_model.transcribe(audio=audio_data)
            text = transcript["text"]
            print("TRANSCRIPT:", text)

            category = classify_text(text)
            print("CATEGORY:", category)

            s.send(category.encode("utf-8"))

        else:
            print("Received:", stringdata)







# # main.py
# import socket
# import threading

# # Localhost and port
# HOST, PORT = "127.0.0.1", 25001

# def process_user_text(text):
#     text = text.lower()

#     # Basic toy detection
#     if "train" in text:
#         return "spawn_train", "Ho ho ho! A train coming right up!"
#     elif "teddy" in text or "bear" in text:
#         return "spawn_teddy", "A soft teddy bear for you! Here it comes!"
#     elif "robot" in text:
#         return "spawn_robot", "A shiny robot is being assembled!"
#     else:
#         return "none", "Sorry my friend, I didn't understand the request."

# def handle_client(conn, addr):
#     print(f"Connected to Unity: {addr}")

#     buffer = b""

#     try:
#         while True:
#             data = conn.recv(1024)
#             if not data:
#                 break

#             buffer += data

#             # process lines ending with newline
#             while b"\n" in buffer:
#                 line, buffer = buffer.split(b"\n", 1)
#                 message = line.decode().strip()

#                 print(f"📩 Received from Unity: {message}")

#                 command, santa_response = process_user_text(message)

#                 #Python to Unity send with newline
#                 response = f"{command}|{santa_response}\n"
#                 conn.sendall(response.encode('utf-8'))

#     except Exception as e:
#         print(f"Error: {e}")

#     finally:
#         print(f"Disconnected from Unity: {addr}")
  
# def start_server():
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
#         server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         server.bind((HOST, PORT))
#         server.listen()

#         print(f"🎄 Python AI server running on {HOST}:{PORT}")
#         print("Waiting for Unity to connect...")
        
#         while True:
#                 conn, addr = server.accept()
#                 threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
                
# if __name__ == "__main__":
#     start_server()

