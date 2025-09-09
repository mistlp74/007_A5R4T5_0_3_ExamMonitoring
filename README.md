# ExamMonitoring

## Description

**ExamMonitoring** is a simple Flask + Socket.IO web-application fot simulation real-time online exam monitoring.
Students join a session and their webcam stream is captured in the browser, and sent to the server where a lightweight face presence check (MediaPipe Face Detection accelerated via a Cython module) is performed.  
Teachers see students’ frames in real time and receive system alerts about potential violations (face not detected)

---

## Features

- Create / join session via a 6‑digit code
- Roles: Teacher / Student
- Real‑time:
  - Image (base64) frame streaming from students to teachers
  - Text chat (teacher ↔ student, teacher ↔ teacher)
- Basic face presence detection (MediaPipe)
- Violation alerts (missing face) with cooldown (anti-spam)
- Event logging to `server.log`
- Simple structure (no over-engineered layering)
- Cython module (`cy_frame.pyx`) for faster frame processing

---

## Requirements

- Python 3.10+ (recommended)
- Core libraries (add to `requirements.txt`):
  - `flask`
  - `flask-socketio`
  - `python-socketio`
  - `mediapipe`
  - `opencv-python`
  - `numpy`
  - `cython`

---

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/ExamMonitoring.git
    cd ExamMonitoring
    ```
2. Install dependecies:
   ```bash
    pip install flask
    pip install flask-socketio
    pip install python-socketio
    pip install mediapipe
    pip install opencv-python
    pip install numpy
    pip install cython
    ```
3. Build the Cython module:
    ```bash
    python setup.py build_ext --inplace
    ```

---

## Usage

1. Start the server:
    ```bash
    python app.py
   
2. Open in a browser:
    ```
    http://127.0.0.1:5000/
   
3. Enter a name and select a role:
   - Teacher → creates a session (receives a 6‑digit code)
   - Student → enters the provided session code
4. Teacher sees students’ frames and receives “face not detected” alerts.
5. Student sends camera frames every ~100 ms (configurable).

---

## Troubleshooting

- **No frames visible to teacher**  
  Camera denied or Mediapipe error.  
  *Solution:* Check browser console / allow camera
- **High CPU usage**  
  High frame rate + large resolution  
  *solution*: Increase  the intervals beetwen frames

---

## Author

Developed by [mistlp74](https://github.com/mistlp74)