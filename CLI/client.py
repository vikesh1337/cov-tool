import socket
import sys
import os
import gzip
import pyAesCrypt
import struct

# Socket object creation
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Server address and port
server_address = ('127.0.0.1', 8888)

# Connect to the server
client_socket.connect(server_address)

# Get the filename or file path from the command-line argument
if len(sys.argv) < 2:
    print("Usage: python3 client.py <filename>")
    sys.exit(1)

file_path = sys.argv[1]
filename = os.path.basename(file_path)

# Read the file data
try:
    with open(file_path, 'rb') as file:
        file_data = file.read()
except FileNotFoundError:
    print("File not found:", file_path)
    sys.exit(1)

# Compress the file data using gzip
compressed_data = gzip.compress(file_data)

# Encrypt and send the compressed data
password = "please-use-a-long-and-random-password"
encrypted_file = filename + ".aes"
buffer_size = 64 * 1024

with open(encrypted_file, "wb") as fOut:
    fOut.write(compressed_data)

print("File compressed and encrypted.")

# Read the encrypted data
try:
    with open(encrypted_file, "rb") as file:
        encrypted_data = file.read()
except FileNotFoundError:
    print("Encrypted file not found:", encrypted_file)
    sys.exit(1)

# Send the filename to the server
client_socket.send(filename.encode('utf-8'))

# Wait for the acknowledgment from the server
acknowledgment = client_socket.recv(1024)

if acknowledgment != b'ACK':
    print("Server did not acknowledge the filename.")
    client_socket.close()
    sys.exit(1)

# Send the encrypted file data size to the server
data_size = struct.pack('!Q', len(encrypted_data))
client_socket.send(data_size)

# Wait for the acknowledgment from the server
acknowledgment = client_socket.recv(1024)

if acknowledgment != b'ACK':
    print("Server did not acknowledge the data size.")
    client_socket.close()
    sys.exit(1)

# Send the encrypted file data to the server
client_socket.sendall(encrypted_data)

print("File sent successfully!")

client_socket.close()

os.remove(encrypted_file)
print(".aes file deleted")
