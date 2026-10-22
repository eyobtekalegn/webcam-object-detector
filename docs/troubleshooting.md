# Troubleshooting Guide

## Common Issues & Solutions

### 1. "Camera Error: Could not open camera at index 0"
**Possible Causes:**
- No camera device is connected.
- The camera is currently being used by another application (e.g. Zoom, Cheese, browser).
- Insufficient permissions to access `/dev/video*`.

**Solutions:**
- Verify camera is connected: `ls -l /dev/video*`
- Add your user account to the `video` group:
  ```bash
  sudo usermod -aG video $USER
  ```
  *(Log out and back in for group changes to take effect).*
- Close any other applications using the webcam.
- Open **⚙️ Settings** in the app and select a different camera index if multiple devices exist.

---

### 2. Low Frame Rate (FPS) or High Latency
**Possible Causes:**
- Higher resolution selected (e.g. 1280x720) on slower CPU hardware.

**Solutions:**
- Open **⚙️ Settings** and set resolution to `640x480 (Recommended for CPU)`.
- Increase confidence threshold slider to filter out weak detections.

---

### 3. Model Weights Download Failure
**Possible Causes:**
- No internet connection during initial setup or first launch.

**Solutions:**
- Ensure network connectivity on first launch so `yolov8n.pt` can download.
- Alternatively, manually place `yolov8n.pt` into `~/.cache/webcam_detector/models/yolov8n.pt`.

---

### 4. How to Inspect Application Diagnostic Logs
Log files are recorded continuously to assist with debugging.

To view real-time log output:
```bash
tail -f ~/.local/state/webcam_detector/app.log
```
