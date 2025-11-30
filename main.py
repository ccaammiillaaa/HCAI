# main.py
import socket
import threading

# Localhost and port
HOST = '127.0.0.1'
PORT = 25001

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

def handle_client(conn, addr):
    print(f"Connected to Unity: {addr}")

    buffer = b""

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            buffer += data

            # process lines ending with newline
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                message = line.decode().strip()

                print(f"📩 Received from Unity: {message}")

                command, santa_response = process_user_text(message)

                #Python to Unity send with newline
                response = f"{command}|{santa_response}\n"
                conn.sendall(response.encode('utf-8'))

    except Exception as e:
        print(f"Error: {e}")

    finally:
        print(f"Disconnected from Unity: {addr}")
  
def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()

        print(f"🎄 Python AI server running on {HOST}:{PORT}")
        print("Waiting for Unity to connect...")
        
        while True:
                conn, addr = server.accept()
                threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
                
if __name__ == "__main__":
    start_server()

