import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import socket
import threading
import os
import json
import subprocess
import re

class PiClusterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Raspberry Pi Cluster Control")
        self.server_image_base = './server_images'
        os.makedirs(self.server_image_base, exist_ok=True)
        
        # GUI Configuration
        self.pi_entries = []
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Pi Configuration Section
        config_frame = ttk.LabelFrame(main_frame, text="Pi Configuration")
        config_frame.pack(fill=tk.X, pady=5)
        
        # Scrollable Pi List
        self.canvas = tk.Canvas(config_frame)
        scrollbar = ttk.Scrollbar(config_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        add_btn = ttk.Button(config_frame, text="Add Pi", command=self.add_pi)
        add_btn.pack(pady=5)

        # Control Section
        control_frame = ttk.LabelFrame(main_frame, text="Controls")
        control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(control_frame, text="Number of Images:").pack(side=tk.LEFT)
        self.num_images = ttk.Entry(control_frame, width=5)
        self.num_images.insert(0, "5")
        self.num_images.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Capture", command=self.capture_images).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Retrieve", command=self.get_images).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Reset", command=self.reset_pis).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Scan Network", command=self.scan_network).pack(side=tk.LEFT, padx=5)

        # Log Section
        log_frame = ttk.LabelFrame(main_frame, text="Log")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log = scrolledtext.ScrolledText(log_frame, state='disabled', height=10)
        self.log.pack(fill=tk.BOTH, expand=True)
        
        self.add_pi()

    def add_pi(self):
        frame = ttk.Frame(self.scrollable_frame)
        frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(frame, text="IP:").pack(side=tk.LEFT)
        ip_entry = ttk.Entry(frame, width=15)
        ip_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(frame, text="Port:").pack(side=tk.LEFT)
        port_entry = ttk.Entry(frame, width=5)
        port_entry.insert(0, "5000")
        port_entry.pack(side=tk.LEFT, padx=5)
        
        status = tk.Canvas(frame, width=20, height=20)
        self.draw_status(status, 'red')
        status.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame, text="X", width=3, 
                 command=lambda: self.remove_pi(frame)).pack(side=tk.LEFT)
        
        self.pi_entries.append({
            'frame': frame,
            'ip': ip_entry,
            'port': port_entry,
            'status': status
        })

    def remove_pi(self, frame):
        for entry in self.pi_entries:
            if entry['frame'] == frame:
                self.pi_entries.remove(entry)
                frame.destroy()
                break

    def draw_status(self, canvas, color):
        canvas.delete("all")
        canvas.create_oval(2, 2, 18, 18, fill=color, outline='')

    def log_message(self, message):
        self.log.configure(state='normal')
        self.log.insert(tk.END, message + "\n")
        self.log.configure(state='disabled')
        self.log.see(tk.END)

    def capture_images(self):
        try:
            num = int(self.num_images.get())
        except ValueError:
            self.log_message("Invalid number of images")
            return
        
        for entry in self.pi_entries:
            threading.Thread(target=self.send_command, args=(
                entry['ip'].get(),
                int(entry['port'].get()),
                'CAPTURE',
                num,
                entry['status']
            )).start()

    def get_images(self):
        for entry in self.pi_entries:
            threading.Thread(target=self.send_command, args=(
                entry['ip'].get(),
                int(entry['port'].get()),
                'GET',
                None,
                entry['status']
            )).start()

    def reset_pis(self):
        for entry in self.pi_entries:
            threading.Thread(target=self.send_command, args=(
                entry['ip'].get(),
                int(entry['port'].get()),
                'RESET',
                None,
                entry['status']
            )).start()

    def send_command(self, ip, port, command, arg, status_canvas):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((ip, port))
                self.update_status(status_canvas, 'green')
                
                if command == 'CAPTURE':
                    message = f"CAPTURE:{arg}"
                else:
                    message = command
                
                s.sendall(message.encode())
                self.log_message(f"Sent {command} to {ip}:{port}")
                
                if command == 'GET':
                    self.receive_images(s, ip)
                
        except Exception as e:
            self.log_message(f"Error with {ip}:{port} - {str(e)}")
            self.update_status(status_canvas, 'red')

    def receive_images(self, sock, pi_name):
        save_dir = os.path.join(self.server_image_base, pi_name)
        os.makedirs(save_dir, exist_ok=True)
        
        try:
            while True:
                header_len = int.from_bytes(sock.recv(4), byteorder='big')
                header_data = sock.recv(header_len).decode()
                
                if header_data == "END":
                    break
                
                header = json.loads(header_data)
                filename = header['name']
                filesize = header['size']
                
                with open(os.path.join(save_dir, filename), 'wb') as f:
                    remaining = filesize
                    while remaining > 0:
                        chunk = sock.recv(min(4096, remaining))
                        f.write(chunk)
                        remaining -= len(chunk)
                
                self.log_message(f"Received {filename} from {pi_name}")
                
        except Exception as e:
            self.log_message(f"Transfer error with {pi_name}: {str(e)}")

    def update_status(self, canvas, color):
        self.root.after(0, self.draw_status, canvas, color)

    def scan_network(self):
        def run_arp_scan():
            try:
                result = subprocess.Popen(
                    ['sudo', 'arp-scan', '--localnet'],
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE
                )
                output, error = result.communicate()
                
                if error:
                    self.log_message(f"Scan error: {error.decode()}")
                    return
                
                ips = self.parse_arp_output(output.decode())
                self.show_scan_results(ips)
                
            except Exception as e:
                self.log_message(f"Scan failed: {str(e)}")
                messagebox.showerror("Error", 
                    "Failed to run arp-scan. Make sure it's installed and you have sudo permissions.")

        threading.Thread(target=run_arp_scan).start()

    def parse_arp_output(self, output):
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        lines = output.split('\n')
        ips = []
        
        for line in lines:
            if re.search(ip_pattern, line):
                ip_match = re.search(ip_pattern, line)
                if ip_match:
                    ip = ip_match.group()
                    if ip not in ips:
                        ips.append(ip)
        return ips

    def show_scan_results(self, ips):
        result_window = tk.Toplevel(self.root)
        result_window.title("Network Scan Results")
        
        listbox = tk.Listbox(result_window, width=30, height=15)
        listbox.pack(padx=10, pady=10)
        
        for ip in ips:
            listbox.insert(tk.END, ip)
            
        def use_selected_ip():
            selected = listbox.curselection()
            if selected:
                ip = listbox.get(selected[0])
                self.add_pi_with_ip(ip)
                result_window.destroy()
                
        ttk.Button(result_window, text="Use Selected IP", command=use_selected_ip).pack(pady=5)

    def add_pi_with_ip(self, ip):
        self.add_pi()
        new_entry = self.pi_entries[-1]
        new_entry['ip'].delete(0, tk.END)
        new_entry['ip'].insert(0, ip)
        new_entry['port'].delete(0, tk.END)
        new_entry['port'].insert(0, "5000")

if __name__ == '__main__':
    root = tk.Tk()
    app = PiClusterGUI(root)
    root.mainloop()