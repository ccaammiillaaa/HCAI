# main.py
import socket

HOST = '127.0.0.1'  # Localhost
PORT = 5000        # Port to listen on

# Create a TCP/IP socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Python Server listening on {HOST}:{PORT}")

    conn, addr = server_socket.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode()
            print(f"Received from Unity: {message}")

            #Send back a response
            reply = "Hello from Python Server!"
            conn.sendall(reply.encode())
            
