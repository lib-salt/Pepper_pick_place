import socket 
import threading
from view_object_rec import process_frame


host = '127.0.0.1'
port = 12345
buffer_size = 4096


# Create socket
socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_server.bind((host, port))
socket_server.listen(2) # 2 connections allowed 

def start_server():
    while True:
        print("Waiting for connection...")
        client_socket, client_address = socket_server.accept()
        print(f"Connection from {client_address}")

        # New thread to handle client
        threading.Thread(target=handle_client, args=(client_socket,)).start()


def handle_client(client_socket):
    while True:
        frame_data = 'b'
        while len(frame_data) < buffer_size:
            packet = client_socket.recv(buffer_size)
            if not packet:
                break
            frame_data += packet

        if not frame_data:
            break

        process_frame(frame_data)

    client_socket.close()

if __name__ == "__main__":
    start_server()
    

