import socket
import threading
import os
import time
import json
# Configuration
CLIENTS = {
    'pi1': ('192.168.180.17', 5000), #192.168.40.211
   'pi2': ('192.168.180.182', 5000)
    # 'pi3': ('192.168.1.103', 5000)
}
NUM_IMAGES = 5  # Default number of images to capture
SERVER_IMAGE_BASE = './server_images'

def send_command(client_addr, command, arg=None):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect(client_addr)
            
            if command == 'CAPTURE':
                message = f"CAPTURE:{arg}"
            else:
                message = command
                
            s.sendall(message.encode())
            
            if command == 'GET':
                receive_images(s, client_addr[0])
                
    except Exception as e:
        print(f"Error with {client_addr[0]}: {str(e)}")

def receive_images(sock, pi_name):
    save_dir = os.path.join(SERVER_IMAGE_BASE, pi_name)
    os.makedirs(save_dir, exist_ok=True)
    
    try:
        while True:
            # Read header length (first 4 bytes)
            header_len_bytes = sock.recv(4)
            if not header_len_bytes:
                break
                
            header_len = int.from_bytes(header_len_bytes, byteorder='big')
            
            # Read header JSON data
            header_data = sock.recv(header_len).decode()
            if header_data == "END":
                break
                
            try:
                header = json.loads(header_data)
                filename = header['name']
                filesize = header['size']
            except (json.JSONDecodeError, KeyError):
                print("Invalid header format")
                continue

            # Receive binary image data
            image_path = os.path.join(save_dir, filename)
            with open(image_path, 'wb') as f:
                received = 0
                while received < filesize:
                    chunk = sock.recv(min(4096, filesize - received))
                    if not chunk:
                        raise ConnectionError("Incomplete transfer")
                    f.write(chunk)
                    received += len(chunk)
            
            print(f"Received {filename} ({filesize} bytes)")
            
    except Exception as e:
        print(f"Transfer error: {str(e)}")

def capture_images():
    print(f"\nStarting simultaneous image capture ({NUM_IMAGES} images)...")
    threads = []
    for name, addr in CLIENTS.items():
        t = threading.Thread(target=send_command, args=(addr, 'CAPTURE', NUM_IMAGES))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    print("Capture command sent to all Pis\n")

def get_images():
    print("\nRetrieving images from Pis...")
    for name, addr in CLIENTS.items():
        print(f"Getting images from {name}...")
        send_command(addr, 'GET')
    print("All images retrieved\n")

def reset_pis():
    print("\nResetting all Pis...")
    threads = []
    for name, addr in CLIENTS.items():
        t = threading.Thread(target=send_command, args=(addr, 'RESET'))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    print("Reset command sent to all Pis\n")

def main():
    os.makedirs(SERVER_IMAGE_BASE, exist_ok=True)
    
    while True:
        print("\nRaspberry Pi Cluster Control")
        print("1. Capture Images")
        print("2. Retrieve Images")
        print("3. Reset Pis")
        print("4. Exit")
        
        choice = input("Select option: ")
        
        if choice == '1':
            capture_images()
        elif choice == '2':
            get_images()
        elif choice == '3':
            reset_pis()
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid option")

if __name__ == '__main__':
    main()
