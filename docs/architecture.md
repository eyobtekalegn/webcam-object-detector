# Application Architecture & Design

## Overview
Webcam Object Detector is designed as a modular desktop application following Qt's model-view-worker pattern. It keeps heavy frame processing and deep-learning inference off the main GUI thread to ensure a smooth, responsive user interface on Debian 13 GNOME.

---

## Architectural Layout

```
                  +-----------------------------------+
                  |      PySide6 MainWindow UI       |
                  |  (VideoView, DetectionPanel, etc) |
                  +-----------------+-----------------+
                                    |
                          Qt Signals|& Slots
                                    v
                  +-----------------+-----------------+
                  |     DetectionWorker Thread        |
                  +--------+-----------------+--------+
                           |                 |
                           v                 v
                 +---------+---+     +-------+---------+
                 | CameraMgr   |     | ObjectDetector  |
                 | (OpenCV)    |     | (YOLOv8 CPU)    |
                 +-------------+     +-----------------+
```

---

## Key Modules

### 1. `config.py`
Handles application configuration reading, validation against default parameters, and local JSON persistence (`~/.config/webcam_detector/config.json`).

### 2. `camera.py`
Provides `CameraManager` to wrap OpenCV `VideoCapture`. Scans available camera indices and sets camera parameters safely.

### 3. `detector.py`
Encapsulates `ultralytics.YOLO` model execution. Ensures model execution takes place on CPU and formats output into clean `FrameDetections` and `DetectionResult` objects.

### 4. `rendering.py`
Pure functional rendering logic to draw bounding box rectangles, badge backgrounds, class text, and confidence percentages with high-contrast colors onto OpenCV BGR frames.

### 5. `statistics.py`
Uses a sliding window queue (`PerformanceTracker`) to compute accurate moving-average FPS and latency metrics in milliseconds without fabrication.

### 6. `worker.py`
Qt `QThread` subclass that owns the webcam read and YOLO inference loop. Communicates with Qt widgets using thread-safe Signals (`frame_processed`, `error_occurred`, `stopped`).

### 7. `ui/`
PySide6 widget components styled with custom QSS stylesheet (`styles.py`):
- `video_view.py`: Video display frame scaling aspect ratio.
- `detection_panel.py`: Live stats breakdown and object class list.
- `settings_dialog.py`: Modal configuration window.
- `main_window.py`: Application main window orchestrating controls and worker signals.
