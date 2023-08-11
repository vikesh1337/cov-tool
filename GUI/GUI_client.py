import tkinter as tk
from tkinter import filedialog
import socket
import os
import gzip

class ClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Client GUI")
        self.server_address_label = tk.Label(root, text="Server Address:")
        self.server_address_label.pack()      
        self.server_address_entry = tk.Entry(root)
        self.server_address_entry.pack()

        self.file_path_label = tk.Label(root, text="File Path:")
        self.file_path_label.pack()

        self.file_path_entry = tk.Entry(root, state="readonly")
        self.file_path_entry.pack()

        self.browse_button = tk.Button(root, text="Browse", command=self.browse_file)
        self.browse_button.pack()

        self.filesize_label = tk.Label(root, text="File Size:")
        self.filesize_label.pack()      

        self.filesize_var = tk.StringVar()
        self.filesize_display = tk.Label(root, textvariable=self.filesize_var)
        self.filesize_display.pack()

        self.send_button = tk.Button(root, text="Send File", command=self.send_file)
        self.send_button.pack()

        self.quit_button = tk.Button(root, text="Quit", command=root.quit)
        self.quit_button.pack()

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        self.file_path_entry.config(state="normal")
        self.file_path_entry.delete(0, tk.END)
        self.file_path_entry.insert(0, file_path)
        self.file_path_entry.config(state="readonly")
        self.update_filesize(file_path)     

    def update_filesize(self, file_path):
        try:
            file_size = os.path.getsize(file_path)
            self.filesize_var.set(f"Size: {file_size} bytes")

        except:
            self.filesize_var.set("")          

    def send_file(self):
        try:
            server_address = self.server_address_entry.get()
            file_path = self.file_path_entry.get()         
            if not server_address or not file_path:
                tk.messagebox.showerror("Error", "Server address and file path are required.")
                return

            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((server_address, 8888))

            filename = os.path.basename(file_path)
            try:
                with open(file_path, 'rb') as file:
                    file_data = file.read()

            except FileNotFoundError:
                tk.messagebox.showerror("Error", "File not found.")
                client_socket.close()
                return

            compressed_data = gzip.compress(file_data)
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
  
            client_socket.send(filename.encode('utf-8'))
            acknowledgment = client_socket.recv(1024)

            if acknowledgment != b'ACK':
                tk.messagebox.showerror("Error", "Server did not acknowledge the filename.")
                client_socket.close()
                return

            data_size = len(compressed_data)
            data_size_bytes = data_size.to_bytes(8, byteorder='big')
            client_socket.send(data_size_bytes)
            
            acknowledgment = client_socket.recv(1024)
            if acknowledgment != b'ACK':
                tk.messagebox.showerror("Error", "Server did not acknowledge the data size.")
                client_socket.close()
                return     

            client_socket.sendall(compressed_data)
            tk.messagebox.showinfo("Success", "File sent successfully!")

        except Exception as e:
            tk.messagebox.showerror("Error", "An error occurred during file transfer: " + str(e))

        finally:
            client_socket.close()
            os.remove(encrypted_file)


root = tk.Tk()
gui = ClientGUI(root)
root.mainloop()
