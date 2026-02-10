# 🤖 Physical AI: Humanoid Hand

An interactive **Physical AI** (Embodied AI) project that bridges computer vision and robotic actuation. This system uses a Raspberry Pi 5 to process hand gestures in real-time and physically replicate them on a **5-DOF Metal Humanoid Hand** to play Rock-Paper-Scissors.

![Robot Setup](images/setup_full.jpg)

## 🧠 What is Physical AI?
Unlike standard software AI that lives on a screen, this project demonstrates **Embodied Intelligence**—the ability of an AI system to perceive its environment (via camera) and physically interact with it (via servos).

## 🎮 Features
* **Perception:** Real-time hand tracking using MediaPipe and OpenCV (60 FPS on Pi 5).
* **Actuation:** Precise control of 5 independent metal-gear servos via PCA9685.
* **3 Interaction Modes:**
    * **Game Mode:** The robot perceives your move, calculates the winner, and physically reacts with the winning hand.
    * **Mimic Mode:** Zero-latency "Shadow Hand" that copies human dexterity.
    * **Test Mode:** Manual calibration for hardware tuning.
* **Safety:** Implements "Soft Start" logic to prevent high-torque servo stalls.

## 📸 Demo

| Rock | Paper | Scissors |
| :---: | :---: | :---: |
| ![Rock](images/demo_rock.png) | ![Paper](images/demo_paper.png) | ![Scissors](images/demo_scissors.png) |

## 🛠️ Hardware & Wiring Guide

### 🧰 Materials List
* **Compute:** Raspberry Pi 5 (4GB/8GB).
* **Actuators:** 5-DOF Metal Humanoid Hand with **MG90S** or **A0090** digital servos.
* **Driver:** PCA9685 16-Channel PWM Driver (I2C).
* **Vision:** USB Webcam (Logitech C920 or similar).
* **Power:** External 5V 4A Power Supply (Critical for Physical AI reliability).

### 🔌 Wiring Instructions

#### 1. Power Supply (The Heartbeat)
Physical AI requires stable current. Do not power servos from the Pi.
* **External 5V (+) ->** Connect to **V+** terminal on PCA9685.
* **External GND (-) ->** Connect to **GND** terminal on PCA9685.

#### 2. Signal Logic (The Brain)
Connect PCA9685 to Raspberry Pi GPIO:
| PCA9685 Pin | Raspberry Pi 5 Pin | Function |
| :--- | :--- | :--- |
| **VCC** | **3.3V** (Pin 1) | Logic Power |
| **GND** | **GND** (Pin 6) | Common Ground |
| **SCL** | **GPIO 3** (Pin 5) | I2C Clock |
| **SDA** | **GPIO 2** (Pin 3) | I2C Data |

#### 3. Actuator Mapping
| Finger | Channel | Logic Type |
| :--- | :--- | :--- |
| **Index** | **Ch 0** | Standard |
| **Middle** | **Ch 1** | Standard |
| **Thumb** | **Ch 2** | Standard |
| **Ring** | **Ch 3** | **Reversed** |
| **Pinky** | **Ch 4** | **Reversed** |

## 🖼️ Hardware Gallery

| Mechanism View | Top View |
| :---: | :---: |
| ![Mechanism View](images/setup_hand_isolated.jpg) | ![Top View](images/setup_top.jpg) |

| Side View | Front View |
| :---: | :---: |
| ![Side View](images/setup_side.jpg) | ![Front View](images/setup_front.jpg) |

## 📦 Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/assix/Humanoid-Hand-Physical-AI.git](https://github.com/assix/Humanoid-Hand-Physical-AI.git)
    cd Humanoid-Hand-Physical-AI
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Enable I2C:**
    ```bash
    sudo raspi-config
    # Interface Options -> I2C -> Enable
    ```

## 🚀 Usage

Run the Physical AI Controller:
```bash
python main.py
```

### ⌨️ Controls
| Key | Action |
| :--- | :--- |
| **`X`** | **Start Game** (Countdown -> Fight!) |
| **`M`** | **Mimic Mode** (Teleoperation) |
| **`T`** | **Test Mode** (Manual Control) |
| **`SPACE`** | **Relax** (Cut power to motors) |
| **`Q`** | Quit |

## 📝 License
[MIT](LICENSE)
