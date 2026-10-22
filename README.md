# Webcam Object Detector

**Webcam Object Detector** is a local-first, real-time desktop application built for Debian 13 GNOME that uses OpenCV, PySide6, and a pretrained YOLO nano neural network to detect multiple objects in real time using a standard laptop camera.

---

## Features

- **Real-Time Webcam Inference**: Streams live camera feed with real-time bounding box annotations, category labels, and confidence percentage scores.
- **Dark Navy / Emerald UI**: Dark theme GUI designed for GNOME with high-contrast emerald green accents and clear controls.
- **Live Performance Statistics**: Measures and displays actual frame rate (FPS), CPU inference latency in milliseconds, input resolution, and engine status.
- **Object Counting & Summaries**: Displays active class list counts and detection breakdowns with empty state indicators.
- **Customizable Detection Overlay Controls**: Easily toggle bounding boxes, category labels, and confidence text. Adjustable confidence threshold slider (5% to 95%).
- **High-Quality Screenshot Capture**: Save crisp PNG images of annotated frames directly to a configurable destination directory.
- **Persistent Preferences**: Remembers camera index, resolution, threshold settings, and screenshot paths across application restarts.

---

## Technical Stack

- **Python 3.12+**
- **PySide6**: Qt 6 graphical user interface framework.
- **OpenCV (`opencv-python-headless`)**: Camera access, image manipulation, frame conversion.
- **Ultralytics YOLO (`yolov8n.pt`)**: Pretrained nano object detection model running locally on CPU.
- **NumPy**: Matrix and array manipulation.
- **pytest**: Automated testing suite.

---

## System Requirements (Debian 13 GNOME)

- Debian 13 (Trixie) or Linux-compatible OS.
- Python 3.10+ with `python3-venv` installed (`sudo apt install python3-venv python3-pip`).
- Built-in or USB webcam.

---

## Installation & Setup

Follow these steps to install and run the application inside an isolated Python virtual environment.

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/webcam-object-detector.git
cd webcam-object-detector
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Upgrade pip and Install Dependencies
```bash
pip install --upgrade pip
pip install -e .
```

---

## Launching the Application

Run the application using either the CLI command or module execution:

```bash
# Using installed entry point script:
webcam-detector

# Or using python module:
python3 -m webcam_detector.main
```

---

## Usage Guide

1. **Start Detection**: Click **▶ Start Camera** at the bottom left to initialize camera access and load the YOLO weights onto the CPU.
2. **Adjust Controls**:
   - Open **⚙️ Settings** to change camera device index or resolution (640x480, 800x600, 1280x720).
   - Adjust the confidence threshold slider or toggle box/label visibility.
3. **Capture Screenshots**: Click **📸 Save Screenshot** to write the current frame with all active overlays to `~/Pictures/WebcamDetector/`.
4. **Stop Camera**: Click **⏹ Stop Camera** to safely release the camera resource and worker thread.

---

## Model Licensing & Weights Setup

- **Model Architecture**: YOLOv8 Nano (`yolov8n.pt`) by Ultralytics.
- **Pretrained Categories**: 80 standard COCO dataset object categories (e.g., person, car, bicycle, dog, chair, laptop, phone).
- **Weight Storage**: Pretrained weights are automatically downloaded on first launch and cached under `~/.cache/webcam_detector/models/yolov8n.pt`. Model weights are excluded from Git repository tracking.
- **Licensing Notice**: Ultralytics YOLOv8 is subject to the AGPL-3.0 license.

---

## Running Automated Tests

Run the unit test suite without requiring a physical camera or GPU:

```bash
pytest tests/
```

---

## Log Diagnostics

Application logs are automatically written with rotating size limits to:
`~/.local/state/webcam_detector/app.log`

---

## Known Limitations

- **Physical Webcam Required for Live Feed**: If no physical webcam is connected, the application will display a clear error message. Synthetic frame processing is used in test suites.
- **Pretrained Scope**: The model recognizes only objects included in its 80 COCO category training set.
