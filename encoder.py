import tkinter as tk
from tkinter import filedialog
from cryptography.fernet import Fernet
import math
from PIL import Image, ImageTk
import os

KEY_FILENAME = "encryption_key.key"
key = Fernet.generate_key()

def save_key_to_file(key: bytes, filename: str):
    with open(filename, "wb") as key_file:
        key_file.write(key)


def load_key(filename: str):
    if os.path.exists(filename):
        with open(filename, "rb") as key_file:
            return key_file.read()
    else:
        return None


def generate_key():
    return Fernet.generate_key()


def encrypt_text(text: str, key: bytes) -> bytes:
    f = Fernet(key)
    return f.encrypt(text.encode())


def decrypt_text(encrypted_data: bytes, key: bytes) -> str:
    f = Fernet(key)
    return f.decrypt(encrypted_data).decode()


def create_color_grid(rgb_values, filename, num_cols):
    num_rows = math.ceil(len(rgb_values) / num_cols)
    cell_size = 50

    image = Image.new("RGB", (num_cols * cell_size, num_rows * cell_size))

    for i in range(num_rows):
        for j in range(num_cols):
            idx = i * num_cols + j
            if idx < len(rgb_values):
                r, g, b = rgb_values[idx]
                for x in range(cell_size):
                    for y in range(cell_size):
                        image.putpixel((j * cell_size + x, i * cell_size + y), (r, g, b))

    image.save(filename)


def store_encrypted_data_in_image(encrypted_data: bytes, filename: str):
    data_length = len(encrypted_data)
    encrypted_data = encrypted_data.ljust(data_length + (3 - data_length % 3) % 3, b'\x00')
    triplets = [encrypted_data[i:i + 3] for i in range(0, len(encrypted_data), 3)]
    rgb_values = [(triplet[0], triplet[1], triplet[2]) for triplet in triplets]
    num_cols = math.ceil(math.sqrt(len(rgb_values)))
    create_color_grid(rgb_values, filename, num_cols)


def retrieve_encrypted_data_from_image(filename: str) -> bytes:
    image = Image.open(filename)
    cell_size = 50
    num_cols = image.width // cell_size
    rgb_values = []

    for i in range(image.height // cell_size):
        for j in range(num_cols):
            x, y = j * cell_size, i * cell_size
            r, g, b = image.getpixel((x, y))
            rgb_values.append((r, g, b))

    encrypted_data = b''.join([bytes(triplet) for triplet in rgb_values]).rstrip(b'\x00')
    return encrypted_data


def browse_input_file():
    filename = filedialog.askopenfilename(title="Select input image")
    if filename:
        input_file_var.set(filename)


def browse_output_file():
    filename = filedialog.asksaveasfilename(title="Save image as", defaultextension=".png", filetypes=[("PNG files", "*.png")])
    if filename:
        output_file_var.set(filename)


# New function to generate and store the key
def save_key():
    global key
    key = generate_key()


def browse_key_file(is_save):
    global key
    filename = filedialog.askopenfilename(title="Select key file") if not is_save else filedialog.asksaveasfilename(title="Save key as", defaultextension=".key", filetypes=[("Key files", "*.key")])
    if filename:
        if is_save:
            save_key_to_file(key, filename)
        else:
            loaded_key = load_key(filename)
            if loaded_key:
                key = loaded_key
            else:
                status_label.config(text="Invalid key file.")


def display_image(filename):
    if not os.path.exists(filename):
        return

    image = Image.open(filename)
    image.thumbnail((200, 200))
    photo = ImageTk.PhotoImage(image)

    if hasattr(image_label, 'image') and image_label.image:
        image_label.config(image="")
        image_label.image = None

    image_label.image = photo
    image_label.config(image=photo)


def encrypt_and_save():
    global key
    text = text_to_encrypt.get()
    encrypted_data = encrypt_text(text, key)
    store_encrypted_data_in_image(encrypted_data, output_file_var.get())
    status_label.config(text="The color grid has been saved.")
    display_image(output_file_var.get())

def decrypt_and_show():
    global key
    if key is None:
        status_label.config(text="No encryption key provided.")
        return

    retrieved_encrypted_data = retrieve_encrypted_data_from_image(input_file_var.get())
    retrieved_text = decrypt_text(retrieved_encrypted_data, key)
    decrypted_text.set(retrieved_text)
    display_image(input_file_var.get())



root = tk.Tk()
root.title("Image-based Text Encryption/Decryption")

text_to_encrypt = tk.StringVar()
input_file_var = tk.StringVar()
output_file_var = tk.StringVar()
decrypted_text = tk.StringVar()

tk.Label(root, text="Text to encrypt:").grid(row=0, column=0, sticky="w")
tk.Entry(root, textvariable=text_to_encrypt, width=50).grid(row=0, column=1)
tk.Button(root, text="Encrypt and Save", command=encrypt_and_save).grid(row=0, column=2)

tk.Label(root, text="Save encrypted image as:").grid(row=1, column=0, sticky="w")
tk.Entry(root, textvariable=output_file_var, width=50).grid(row=1, column=1)
tk.Button(root, text="Browse", command=browse_output_file).grid(row=1, column=2)

tk.Label(root, text="Select input image:").grid(row=2, column=0, sticky="w")
tk.Entry(root, textvariable=input_file_var, width=50).grid(row=2, column=1)
tk.Button(root, text="Browse", command=browse_input_file).grid(row=2, column=2)

tk.Label(root, text="Decrypted text:").grid(row=3, column=0, sticky="w")
tk.Entry(root, textvariable=decrypted_text, width=50).grid(row=3, column=1)
tk.Button(root, text="Decrypt and Show", command=decrypt_and_show).grid(row=3, column=2)

status_label = tk.Label(root, text="", fg="blue")
status_label.grid(row=4, column=0, columnspan=3)

tk.Button(root, text="Load Key", command=lambda: browse_key_file(False)).grid(row=5, column=1, sticky="w")
tk.Button(root, text="Save Key", command=lambda: browse_key_file(True)).grid(row=5, column=1, sticky="e")

image_label = tk.Label(root)
image_label.grid(row=6, column=0, columnspan=3)

root.mainloop()

