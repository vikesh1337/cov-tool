import socket
import sys
import os
import gzip

# Socket object creation
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Server address and port
server_address = ('10.0.0.4', 9999)

# Connect to the server
client_socket.connect(server_address)

# Get the filename or file path from the command-line argument
if len(sys.argv) < 2:
    print("Usage: python3 client.py <filename>")
    sys.exit(1)

file_path = sys.argv[1]
filename = os.path.basename(file_path)

# Compress the file data
try:
    with open(file_path, 'rb') as file:
        file_data = file.read()
        compressed_data = gzip.compress(file_data)
except FileNotFoundError:
    print("File not found:", file_path)
    sys.exit(1)

# Send the filename to the server
client_socket.send(filename.encode())

# Send the compressed file data to the server
client_socket.sendall(compressed_data)

print("File sent successfully!")

client_socket.close()