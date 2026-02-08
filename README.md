# 🤖 Humanoid-Hand-5DOF-RPS

An AI-powered controller for a **5-DOF Metal Humanoid Robotic Hand**. This project uses a Raspberry Pi 5 and MediaPipe hand tracking to play Rock-Paper-Scissors against a human opponent in real-time.

![Robot Setup](images/setup_full.jpg)

## 🎮 Features
* **AI Vision:** Real-time hand tracking using MediaPipe and OpenCV.
* **Game Logic:** Complete game loop with Countdown, Showdown, and Scorekeeping.
* **3 Modes:**
    * **Game Mode:** Play a match against the robot with live scoring.
    * **Mimic Mode:** The robot shadows your hand gestures in real-time.
    * **Test Mode:** Manual keyboard control for calibration and debugging.
* **Safety Features:** "Soft Start" boot sequence and "Relax Mode" to prevent servo stall/buzzing.

## 📸 Demo

| Rock | Paper | Scissors |
| :---: | :---: | :---: |
| ![Rock](images/demo_rock.png) | ![Paper](images/demo_paper.png) | ![Scissors](images/demo_scissors.png) |

# 🛠️ Hardware & Wiring Guide

## 🧰 Materials List
* **Raspberry Pi 5** (4GB or 8GB recommended for smooth MediaPipe tracking).
* **5-DOF Metal Humanoid Robotic Hand:**
    * Left or Right hand model (Metal structure).
    * **Servos:** 5x **MG90S** (Metal Gear) or **A0090** digital servos.
    * *Note: These servos require more current than the Pi can provide directly.*
* **PCA9685 16-Channel PWM Servo Driver:**
    * Interface: I2C.
    * Controls up to 16 servos using only 2 pins on the Pi.
* **External Power Supply (Crucial):**
    * **5V 2A to 4A Power Adapter** (Barrel jack or USB-C breakout).
    * *Do NOT power the servos directly from the Raspberry Pi's 5V pin. You will brown out the Pi.*
* **Jumper Wires:** Female-to-Female for the Pi-to-Driver connection.
* **USB Webcam:** Any standard 720p/1080p webcam (Logitech C920 used in demo).

---

## 🔌 Wiring Instructions

### 1. Power Supply Wiring (The Most Important Step)
The servos need their own power source. The PCA9685 driver has a screw terminal block (green) for this purpose.
* **External 5V (+) ->** Connect to the **V+** screw terminal on the PCA9685.
* **External GND (-) ->** Connect to the **GND** screw terminal on the PCA9685.

### 2. Raspberry Pi to PCA9685 (I2C Connection)
Connect the PCA9685 header pins to the Raspberry Pi GPIO header:

| PCA9685 Pin | Raspberry Pi 5 Pin | Function |
| :--- | :--- | :--- |
| **VCC** | **3.3V** (Pin 1) | Powers the driver chip logic |
| **GND** | **GND** (Pin 6) | Common Ground |
| **SCL** | **GPIO 3 / SCL** (Pin 5) | I2C Clock Line |
| **SDA** | **GPIO 2 / SDA** (Pin 3) | I2C Data Line |
| **OE** | *Not Connected* | Output Enable (Optional) |

> **⚠️ Warning:** Connect VCC to **3.3V**, not 5V. The Pi's logic level is 3.3V.

### 3. Servo Motor Connections
Plug your servo cables into the yellow/red/black headers on the PCA9685.
* **Orientation:** The **Orange/Yellow** wire (Signal) goes to the **Top** (PWM) pin. The **Brown/Black** wire (Ground) goes to the **Bottom** (GND) pin.

| Hand Finger | PCA9685 Channel | Config Note |
| :--- | :--- | :--- |
| **Index Finger** | **Channel 0** | Standard Range (4500-9000) |
| **Middle Finger** | **Channel 1** | Standard Range (4500-7500) |
| **Thumb** | **Channel 2** | Standard Range |
| **Ring Finger** | **Channel 3** | **Reversed Logic** (Closed=Low) |
| **Pinky Finger** | **Channel 4** | **Reversed Logic** (Closed=Low) |

*(Note: Channels 3 and 4 are reversed in software because the servos are physically mounted in the opposite direction on the metal frame.)*

## 📦 Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/assix/Humanoid-hand-5dof-rps.git](https://github.com/assix/Humanoid-hand-5dof-rps.git)
    cd Humanoid-hand-5dof-rps
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Enable I2C on Raspberry Pi:**
    ```bash
    sudo raspi-config
    # Interface Options -> I2C -> Enable
    ```

## 🚀 Usage

Run the main controller script:
```bash
python main.py
```

### ⌨️ Controls
| Key | Action |
| :--- | :--- |
| **`X`** | **Start Game** (Countdown -> Fight!) |
| **`M`** | **Mimic Mode** (Robot copies you) |
| **`T`** | **Test Mode** (Manual Control) |
| **`SPACE`** | **Relax** (Cut power to motors) |
| **`R` / `P` / `S`** | Force Rock / Paper / Scissors |
| **`1` - `5`** | Toggle individual fingers |
| **`Q`** | Quit |

## ⚙️ Calibration
If your servos are buzzing or moving backward, adjust the `SAFE_MIN` and `SAFE_MAX` values in `main.py`.
* **Current Safety Range:** 3000 - 9000 (Duty Cycle)
* **Anti-Buzz Logic:** Specific limits are hardcoded for Ring (Ch 3) and Middle (Ch 1) fingers to prevent physical stalling against the metal frame.

## 📝 License
[MIT](LICENSE)
