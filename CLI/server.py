import socket
import struct
import pyAesCrypt
import gzip
import os  # Import the os module

# Define the buffer size for decryption
buffer_size = 64 * 1024

# Function to receive a specific number of bytes from the socket
def receive_data(sock, size):
    data = b''
    while len(data) < size:
        packet = sock.recv(size - len(data))
        if not packet:
            return None
        data += packet
    return data

# Socket object creation
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Server address and port
server_address = ('localhost', 8888)

# Bind the server to the specified address and port
server_socket.bind(server_address)

# Listen for incoming connections
server_socket.listen(1)

print("Waiting for a connection...")

# Accept the client connection
client_socket, client_address = server_socket.accept()
print("Connected to:", client_address)

try:
    # Receive the filename from the client
    filename_with_extension = client_socket.recv(1024).decode('utf-8')

    # Send an acknowledgment back to the client
    client_socket.send(b'ACK')

    # Receive the encrypted file data size from the client
    data_size = client_socket.recv(8)
    data_size = struct.unpack('!Q', data_size)[0]

    # Send an acknowledgment back to the client
    client_socket.send(b'ACK')

    # Receive the encrypted file data from the client
    encrypted_data = receive_data(client_socket, data_size)

    # Decrypt the data using pyAesCrypt
    password = "please-use-a-long-and-random-password"
    decrypted_file = filename_with_extension + ".decrypted"

    with open(decrypted_file, "wb") as fOut:
        fOut.write(encrypted_data)
    print("File received and decrypted successfully!")

    # Read the decrypted data
    with open(decrypted_file, "rb") as file:
        decrypted_data = file.read()

    # Decompress the decrypted data using gzip
    decompressed_data = gzip.decompress(decrypted_data)

    # Save the decompressed data with the original extension
    original_extension = os.path.splitext(filename_with_extension)[1]
    output_filename = filename_with_extension.replace(original_extension, '')

    # Save the decompressed data to a file
    with open(output_filename, "wb") as fOut:
        fOut.write(decompressed_data)

    print("File decompressed and saved successfully!")

except Exception as e:
    print("An error occurred during file transfer:", str(e))

finally:
    # Close the client socket
    client_socket.close()

    # Close the server socket
    server_socket.close()
    os.remove(decrypted_file)
    print(".decrypted file deleted.")