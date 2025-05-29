import socket
import os
import time
from datetime import datetime
import subprocess  # For camera capture - modify as needed
import json 
# Configuration
HOST = '0.0.0.0'
PORT = 5000
IMAGE_DIR = './pi_images'
NUM_CAMERAS = 1  # Change if using multiple cameras

def capture_images(num_images):
    os.makedirs(IMAGE_DIR, exist_ok=True)
    
    for i in range(num_images):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = os.path.join(IMAGE_DIR, f'img_{timestamp}_{i}.jpg')
        
        # Replace with your actual capture command
        # Example using libcamera-jpeg:
        subprocess.run([
            'libcamera-jpeg', 
            '-o', filename,
            '--width', '1920',
            '--height', '1080',
            '--nopreview'
        ])
        
        time.sleep(1)  # Adjust delay between captures as needed

def send_images(conn):
    images = [f for f in os.listdir(IMAGE_DIR) if f.endswith('.jpg')]
    
    for img in images:
        path = os.path.join(IMAGE_DIR, img)
        filesize = os.path.getsize(path)
        
        # Create header with JSON
        header = json.dumps({
            'name': img,
            'size': filesize
        }).encode()
        
        # Send header length (4 bytes) then header
        conn.sendall(len(header).to_bytes(4, byteorder='big'))
        conn.sendall(header)
        
        # Send image data
        with open(path, 'rb') as f:
            while True:
                bytes_read = f.read(4096)
                if not bytes_read:
                    break
                conn.sendall(bytes_read)
    
    # Send termination signal
    conn.sendall((4).to_bytes(4, byteorder='big'))
    conn.sendall(json.dumps("END").encode())

def reset_storage():
    for f in os.listdir(IMAGE_DIR):
        if f.endswith('.jpg'):
            os.remove(os.path.join(IMAGE_DIR, f))

def handle_command(conn):
    data = conn.recv(1024).decode()
    
    if data.startswith('CAPTURE'):
        _, num_images = data.split(':')
        capture_images(int(num_images))
        conn.sendall("CAPTURE_COMPLETE".encode())
    elif data == 'GET':
        send_images(conn)
    elif data == 'RESET':
        reset_storage()
        conn.sendall("RESET_COMPLETE".encode())
    else:
        conn.sendall("UNKNOWN_COMMAND".encode())

def main():
    os.makedirs(IMAGE_DIR, exist_ok=True)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Pi client listening on {HOST}:{PORT}")
        
        while True:
            conn, addr = s.accept()
            print(f"Connection from {addr}")
            handle_command(conn)
            conn.close()

if __name__ == '__main__':
    main()
