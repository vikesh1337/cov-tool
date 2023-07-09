import socket
import gzip
import os

# Socket object creation
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Server address and port
server_address = ('localhost', 9999)

# Server address and port binding to the socket
server_socket.bind(server_address)

# Listen for incoming connections
server_socket.listen(1)

print("Server is listening for incoming connections...")

# Accept client connection
client_socket, client_address = server_socket.accept()

print("Accepted connection from:", client_address)

# Receive the filename from the client
filename_bytes = client_socket.recv(1024)
filename = filename_bytes.decode()

# Receive the compressed file data from the client
compressed_data = client_socket.recv(1024)

# Decompress the file data
decompressed_data = gzip.decompress(compressed_data)

# Write the received data to a file
with open(filename, 'wb') as file:
    file.write(decompressed_data)

print("File received and saved as:", filename)

# Close the client socket and server socket
client_socket.close()
server_socket.close()