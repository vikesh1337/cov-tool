import tkinter as tk
from tkinter import messagebox
from threading import Thread
import socket
import struct
import pyAesCrypt
import gzip
import os

class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Server GUI")
        
        self.server_address = ('localhost', 8888)
        self.buffer_size = 64 * 1024
        
        self.ip_label = tk.Label(root, text="IP Address:")
        self.ip_label.pack()
        
        self.ip_var = tk.StringVar()
        self.ip_display = tk.Label(root, textvariable=self.ip_var)
        self.ip_display.pack()
        
        self.filename_label = tk.Label(root, text="Filename:")
        self.filename_label.pack()
        
        self.filename_var = tk.StringVar()
        self.filename_display = tk.Label(root, textvariable=self.filename_var)
        self.filename_display.pack()
        
        self.filesize_label = tk.Label(root, text="File Size:")
        self.filesize_label.pack()
        
        self.filesize_var = tk.StringVar()
        self.filesize_display = tk.Label(root, textvariable=self.filesize_var)
        self.filesize_display.pack()
        
        self.start_server_button = tk.Button(root, text="Start Server", command=self.start_server_thread)
        self.start_server_button.pack()
        
        self.quit_button = tk.Button(root, text="Quit", command=root.quit)
        self.quit_button.pack()
        
    def start_server_thread(self):
        server_thread = Thread(target=self.start_server)
        server_thread.start()
        
    def start_server(self):
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind(self.server_address)
            server_socket.listen(1)
            self.ip_var.set("Waiting for a connection...")
            
            client_socket, client_address = server_socket.accept()
            self.ip_var.set("Connected to: " + str(client_address))
            
            filename_with_extension = client_socket.recv(1024).decode('utf-8')
            self.filename_var.set(filename_with_extension)
            client_socket.send(b'ACK')
            
            data_size = client_socket.recv(8)
            data_size = struct.unpack('!Q', data_size)[0]
            client_socket.send(b'ACK')
            
            encrypted_data = self.receive_data(client_socket, data_size)
            
            password = "please-use-a-long-and-random-password"
            decrypted_file = filename_with_extension + ".decrypted"
            
            with open(decrypted_file, "wb") as fOut:
                fOut.write(encrypted_data)
            
            decrypted_data = b""
            with open(decrypted_file, "rb") as file:
                decrypted_data = file.read()
            
            decompressed_data = gzip.decompress(decrypted_data)
            original_extension = os.path.splitext(filename_with_extension)[1]
            output_filename = filename_with_extension.replace(original_extension, '')
            
            with open(output_filename, "wb") as fOut:
                fOut.write(decompressed_data)
            
            self.filesize_var.set(f"Size: {len(decompressed_data)} bytes")
            messagebox.showinfo("Success", "File received and decompressed successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", "An error occurred during file transfer: " + str(e))
            
        finally:
            client_socket.close()
            server_socket.close()
            os.remove(decrypted_file)
            self.ip_var.set("")
            self.filename_var.set("")
            self.filesize_var.set("")
    
    def receive_data(self, sock, size):
        data = b''
        while len(data) < size:
            packet = sock.recv(size - len(data))
            if not packet:
                return None
            data += packet
        return data

root = tk.Tk()
gui = ServerGUI(root)
root.mainloop()