# main.py
import socket

HOST = '127.0.0.1'  # Localhost
PORT = 5000        # Port to listen on

def process_user_text(text):
    text = text.lower()

    # Basic toy detection
    if "train" in text:
        return "spawn_train", "Ho ho ho! A train coming right up!"
    elif "teddy" in text or "bear" in text:
        return "spawn_teddy", "A soft teddy bear for you! Here it comes!"
    elif "robot" in text:
        return "spawn_robot", "A shiny robot is being assembled!"
    else:
        return "none", "Sorry my friend, I didn't understand the request."

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"🎄 Python AI server running on {HOST}:{PORT}")

        conn, addr = s.accept()
        print(f"Connected to Unity: {addr}")

        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break

                message = data.decode()
                print(f"📩 Received from Unity: {message}")

                command, santa_response = process_user_text(message)

                # Format response for Unity
                response = f"{command}|{santa_response}"
                conn.sendall(response.encode())


if __name__ == "__main__":
    start_server()