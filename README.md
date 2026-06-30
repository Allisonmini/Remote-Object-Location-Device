# README.md

## Project R.O.L.D. — Remote Object Location Device
**MESA Engineering Challenge Success Overview**

## 🚀 Mission Accomplished
We successfully engineered and deployed a functional 2-axis pan-tilt tracking turret system to navigate, target, and measure object distances within a simulated hazardous environment. By decoupling the operator from the environment, our pilot successfully achieved a target "lock-on" from outside the restricted zone, working completely blind using live wireless telemetry streamed to a custom handheld controller.

---

## 📸 Media Gallery

### System Deployment Video
[Click here to watch the full system demonstration](https://github.com/user-attachments/assets/fcf80629-0e69-4f6a-ad1c-2e3291d94df3)

*Demonstration of the pilot controlling the turret from the hallway and achieving target lock-on.*

### Hardware & Assembly Photos

| Handheld Controller (Role A) | Tracking Turret Base (Role B) |
| :---: | :---: |
| <img src="https://github.com/user-attachments/assets/eeb93717-7a6c-417c-a83b-c8aebfb388d8" width="350"> | <img src="https://github.com/user-attachments/assets/4053fb76-a00b-460b-8761-21579f3abf21" width="350"> |
| *Custom 3D-printed enclosure with OLED telemetry screen* | *2-axis servo base with HC-SR04 sensor and targeted LED shroud* |

---

## 🛠️ What We Built

### 📡 1. Handheld Flight Controller (Role A)
We designed and compiled a standalone, mobile control station operated outside the closed classroom door.
* **Hardware Integration:** Managed inputs from a micro:bit V2 accelerometer and routed outputs to an external I2C OLED display via a Keyestudio Expansion Shield.
* **Firmware Mechanics:** Programmed the system to convert the controller's real-time pitch and roll into coordinate instructions, broadcasting them over a local radio frequency while parsing incoming distance data.

### 🛡️ 2. Deployed Turret Tracking Base (Role B)
We assembled an automated mechanical tracking base positioned entirely within the restricted danger zone.
* **Hardware Integration:** Wired a dual-servo pan-tilt configuration, a targeting light focused via a custom shroud, and an HC-SR04 ultrasonic distance sensor to a central micro:bit V2.
* **Firmware Mechanics:** Configured the base to instantly translate incoming radio vectors into physical servo positioning, align the targeting beam, and broadcast continuous distance updates back to the hallway.

---

## 🔌 Engineered Wiring Blueprint

We successfully mapped and routed the dual-system hardware interface using the following configurations:

### Handheld Controller Interface

| OLED Pin | Shield Pin Column | Purpose |
| :--- | :--- | :--- |
| **GND** | G (Any column) | Common System Ground |
| **VCC** | V (3.3V column) | Logic Power |
| **SCL** | P19 | I2C Clock Line |
| **SDA** | P20 | I2C Data Line |

### Turret Base Interface

| Component | Component Pin | Connection Point | Purpose |
| :--- | :--- | :--- | :--- |
| **3-AAA Battery Pack** | Positive (+) | Servo 1 Red & Servo 2 Red | High-Current Motor Power |
| **3-AAA Battery Pack** | Negative (-) | Micro:bit GND | Common Ground Loop |
| **Servo 1 (Pan)** | Orange/Yellow | Micro:bit **Pin 8** | Horizontal PWM Vector |
| **Servo 2 (Tilt)** | Orange/Yellow | Micro:bit **Pin 12** | Vertical PWM Vector |
| **HC-SR04 Sensor** | Trig | Micro:bit **Pin 0** | Ultrasonic Trigger Pulse |
| **HC-SR04 Sensor** | Echo | Micro:bit **Pin 1** | Ultrasonic Echo Return |
| **Targeting LED** | Long Leg (+) | Micro:bit **Pin 16** | Targeting Beam Power |

---

## 🧠 Solved Engineering Challenges & Technical Triumphs

### ⚡ 1. The High-Current Servo Reset Problem
* **The Challenge:** During initial testing, moving both the pan and tilt servos simultaneously caused the turret's micro:bit to lose power and reset. This happened because the motors drew too much current, causing a voltage drop on the board.
* **Our Solution:** We isolated the power grid. We routed the logic operations through the micro:bit's standard architecture while shifting the high-current lines (Red) of both servos directly to an external 3-AAA battery pack on the 5V rail. We bridged all negative lines to establish a **Common Ground Connection**, stabilizing the signal without risking hardware resets.

### 📊 2. Analog-to-Digital Angular Mapping
* **The Challenge:** Devices output raw coordinate forces ranging between `-1023` and `+1023`. Servos require precise positioning angles strictly bounded between `0°` and `180°`.
* **Our Solution:** We applied mathematical scaling blocks directly within our data loop:
  ```typescript
  let panAngle = Math.map(roll, -1023, 1023, 0, 180)
  let tiltAngle = Math.map(pitch, -1023, 1023, 0, 180)
  ```
  This translated intuitive physical controller tilts directly into smooth mechanical tracking coordinates.

### 📡 3. Radio Buffer Flooding & Telemetry Lag
* **The Challenge:** Continuous tracking loops flooded the wireless network, causing delayed telemetry delivery and erratic servo movements.
* **Our Solution:** We introduced a managed `basic.pause(100)` pacing delay into the core processing thread. This optimized network throughput, providing smooth tracking feedback and instantaneous screen updates without overwhelming the micro:bit's radio buffer.






