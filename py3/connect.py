import socket 
import threading
import struct
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
        try:
            # Read the first 4 bytes to get the frame size
            frame_size_data = client_socket.recv(4)
            if not frame_size_data:
                break  # Client disconnected
            
            # Unpack the frame size (big-endian 4-byte integer)
            frame_size = struct.unpack("!I", frame_size_data)[0]

            # Receive the exact amount of bytes specified in frame_size
            frame_data = b""
            while len(frame_data) < frame_size:
                packet = client_socket.recv(frame_size - len(frame_data))
                if not packet:
                    break  # Connection lost
                frame_data += packet

            if len(frame_data) != frame_size:
                print("Error: Incomplete frame received.")
                continue  # Skip processing this frame

            # Process the full frame
            process_frame(frame_data)

        except Exception as e:
            print(f"Error in handle_client: {e}")
            break

    client_socket.close()

if __name__ == "__main__":
    start_server()
    

