# Ni3D: Low-Cost Distributed 3D Hand Scanner

Ni3D is a scalable, non-invasive, and cost-effective 3D scanning system built using Raspberry Pi Zero units and photogrammetry techniques. Designed for applications in **healthcare, ergonomics, HCI**, and **virtual environments**, Ni3D offers sub-millimeter accuracy (≈ 0.62 mm) comparable to commercial scanners costing over €150,000—at a fraction of the price.

---

## 🧠 Key Features

- **Multi-Camera Photogrammetry**: Synchronized image capture using Raspberry Pi Zeros and high-resolution camera modules.
- **Modular Design**: Easily scalable architecture for expanding camera arrays.
- **Low Cost**: Built using off-the-shelf hardware (e.g., Pi Zero, ArduCam, LEDs).
- **Real-Time Feedback**: Controlled via a central module for synchronized capture and reconstruction.
- **Applications**: Prosthetics, ergonomic tool design, reverse engineering, and more.

---

## 📷 System Overview

The Ni3D system is modular and includes:

### 🔹 1. Data Capturing Module
- **Hardware**: Raspberry Pi Zero W + 5MP ArduCam modules
- **Function**: Captures synchronized multi-angle images around the hand.
- **Setup**: Cameras mounted on a 3D-printed ring for optimal angular distribution.

### 🔹 2. Data Transmission Module
- **Technology**: Uses `Compound Pi` and custom scripts for UDP-based LAN communication.
- **Topology**: One central controller orchestrating multiple Raspberry Pi nodes.

### 🔹 3. Data Processing Module
- **Tools**: Photogrammetry software (e.g., Agisoft Metashape, OpenMVG).
- **Output**: High-resolution 3D meshes from image sets.

### 🔹 4. Lighting Module
- **Hardware**: 12V white LED strips wrapped around the scanner.
- **Benefit**: Reduces motion blur and shadowing for higher quality captures.

### 🔹 5. Power Supply Module
- **Options**: 4S Li-ion battery or 12V regulated power adapter.
- **Purpose**: Powers Pis, lighting, and motors.

---

## 🛠 Prototypes and Evolution

### ⚙️ Ni3D Zero (Initial Prototype)
- **1 Camera** on a static Pi above a rotating platform.
- **Stepper Motor + Arduino Mega** for 30° incremented turns.
- **Manual synchronization** between rotation and image capture.

![Rotating Platform Setup](image/ni3d_zero_rotating_platform.jpg)

---

### ⚙️ Ni3D 1.0
- **Multi-node setup** with multiple Pi Zero + V2 Cameras.
- **Centralized control** over Ethernet.
- **Real-time multi-angle image capture**.
- **3D-Printed Frame** for camera mounting.

![System Architecture](image/system_architecture.jpg)
![Ni3D 1.0 Prototype](image/ni3d_1_0_prototype.jpg)

---

### ⚙️ Ni3D 2.0
- **Queued Data Retrieval**: Solves collision-based data loss by sequential Pi polling.
- **Improved Protocol**: Command-response messaging with ACKs, retries, and error detection.
- **Persistent Sockets**: Boosts data throughput for high-volume image transfers.

![Ni3D 2.0 Prototype](image/ni3d_2_0_setup.jpg)

---

## 🧪 Testing & Results

### ✅ Synchronization
- Image capture across nodes within **<50 ms latency**, ideal for photogrammetry.

### ✅ 3D Reconstruction Accuracy
- Achieved **sub-millimeter resolution**.
- **Consistent results** across sessions due to improved lighting and stability.

![Input Images](image/image_capture_views.jpg)
![3D Reconstruction Output](image/reconstruction_output.jpg)

---

## 📈 Challenges & Solutions

| Challenge | Solution |
|----------|----------|
| Image loss due to network congestion | Queued sequential data transfer |
| Timing mismatch between capture and rotation | Synchronized Pi-Arduino signaling |
| Inconsistent lighting | Installed LED ring illumination |
| Power instability | Centralized power regulation circuit |

---

## 🔮 Future Improvements

- **Automated Camera Calibration**
- **Real-Time Reconstruction Viewer**
- **Wireless Sync via Wi-Fi 6 or BLE Mesh**
- **Dynamic Viewpoint Expansion** with more Pi nodes

---

## 📁 Repository Structure

```plaintext
Ni3D/
├── image/                  # Diagrams, architecture, results
├── Server/                 # Python scripts for server control
├── Client/                # Python scripts for Pi control
├── report.pdf/             # Additional technical documentation
└── README.md               # You are here
