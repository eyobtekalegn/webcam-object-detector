"""Main window UI layout, controls, and thread lifecycle orchestration."""

from pathlib import Path
import time
import cv2
import numpy as np

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap, QAction
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QMessageBox, QDialog, QScrollArea
)

from webcam_detector import __version__
from webcam_detector.config import AppConfig, load_config, save_config
from webcam_detector.statistics import PerformanceTracker
from webcam_detector.worker import DetectionWorker
from webcam_detector.ui.styles import DARK_THEME_QSS
from webcam_detector.ui.video_view import VideoViewWidget
from webcam_detector.ui.detection_panel import DetectionPanelWidget
from webcam_detector.ui.settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    """Main application window for Webcam Object Detector."""

    def __init__(self) -> None:
        super().__init__()
        self.config: AppConfig = load_config()
        self.worker: DetectionWorker | None = None
        self.tracker = PerformanceTracker(window_size=30)
        self.latest_raw_frame: np.ndarray | None = None
        self.latest_annotated_frame: np.ndarray | None = None

        self.setWindowTitle("Webcam Object Detector")
        self.resize(1024, 680)
        self.setMinimumSize(800, 500)
        self.setStyleSheet(DARK_THEME_QSS)

        self._init_ui()

    def _init_ui(self) -> None:
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(12)

        # --- A. Header Bar ---
        header = QFrame(self)
        header.setFixedHeight(50)
        header.setStyleSheet("background-color: #1E293B; border-radius: 8px; border: 1px solid #334155;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 0, 16, 0)

        # App Title
        app_title = QLabel("📷 WEBCAM OBJECT DETECTOR", self)
        app_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #F8FAFC; letter-spacing: 0.5px;")

        # Status Indicators
        self.cam_status_label = QLabel("Camera: Offline", self)
        self.cam_status_label.setStyleSheet("color: #94A3B8; font-weight: 500;")

        self.model_status_label = QLabel("Model: YOLOv8n (CPU)", self)
        self.model_status_label.setStyleSheet("color: #38BDF8; font-weight: 500;")

        # Header buttons
        btn_settings = QPushButton("⚙️ Settings", self)
        btn_settings.setFocusPolicy(Qt.NoFocus)
        btn_settings.clicked.connect(self._open_settings)

        btn_help = QPushButton("❓ Help", self)
        btn_help.setFocusPolicy(Qt.NoFocus)
        btn_help.clicked.connect(self._open_help)

        header_layout.addWidget(app_title)
        header_layout.addStretch()
        header_layout.addWidget(self.cam_status_label)
        header_layout.addSpacing(16)
        header_layout.addWidget(self.model_status_label)
        header_layout.addSpacing(20)
        header_layout.addWidget(btn_settings)
        header_layout.addWidget(btn_help)

        main_layout.addWidget(header)

        # --- B. Main Content Area (Video View + Sidebar Panel) ---
        content_layout = QHBoxLayout()
        content_layout.setSpacing(12)

        self.video_view = VideoViewWidget(self)
        content_layout.addWidget(self.video_view, stretch=1)

        self.detection_panel = DetectionPanelWidget(self)
        content_layout.addWidget(self.detection_panel)

        main_layout.addLayout(content_layout, stretch=1)

        # --- C. Controls Bar ---
        controls = QFrame(self)
        controls.setFixedHeight(56)
        controls.setStyleSheet("background-color: #1E293B; border-radius: 8px; border: 1px solid #334155;")
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(16, 0, 16, 0)
        controls_layout.setSpacing(12)

        self.btn_start = QPushButton("▶ Start Camera", self)
        self.btn_start.setProperty("class", "btn-primary")
        self.btn_start.setStyleSheet("background-color: #059669; color: white; font-weight: bold;")
        self.btn_start.clicked.connect(self.start_detection)

        self.btn_stop = QPushButton("⏹ Stop Camera", self)
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_detection)

        self.btn_screenshot = QPushButton("📸 Save Screenshot", self)
        self.btn_screenshot.setEnabled(False)
        self.btn_screenshot.clicked.connect(self.take_screenshot)

        controls_layout.addWidget(self.btn_start)
        controls_layout.addWidget(self.btn_stop)
        controls_layout.addSpacing(12)
        controls_layout.addWidget(self.btn_screenshot)
        controls_layout.addStretch()

        main_layout.addWidget(controls)

    def start_detection(self) -> None:
        """Instantiates worker and starts webcam capture/inference loop."""
        if self.worker is not None and self.worker.isRunning():
            return

        self.tracker.reset()
        self.btn_start.setEnabled(False)
        self.cam_status_label.setText("Camera: Starting...")
        self.cam_status_label.setStyleSheet("color: #F59E0B; font-weight: bold;")
        self.video_view.show_placeholder("Initializing camera feed and YOLO neural network...")

        self.worker = DetectionWorker(config=self.config)
        self.worker.frame_processed.connect(self._on_frame_processed)
        self.worker.error_occurred.connect(self._on_worker_error)
        self.worker.model_loaded.connect(self._on_model_loaded)
        self.worker.stopped.connect(self._on_worker_stopped)

        self.worker.start()

    def stop_detection(self) -> None:
        """Signals worker to stop and cleanup resources."""
        if self.worker is not None and self.worker.isRunning():
            self.btn_stop.setEnabled(False)
            self.cam_status_label.setText("Camera: Stopping...")
            self.cam_status_label.setStyleSheet("color: #F59E0B; font-weight: bold;")
            self.worker.stop()

    def _on_frame_processed(self, annotated_frame: np.ndarray, raw_frame: np.ndarray, detections) -> None:
        """Slot called when worker finishes processing a frame."""
        self.latest_annotated_frame = annotated_frame
        self.latest_raw_frame = raw_frame

        # Update performance metrics
        self.tracker.update(detections.inference_time_ms)
        fps = self.tracker.get_fps()
        avg_lat = self.tracker.get_average_latency_ms()
        res = (raw_frame.shape[1], raw_frame.shape[0])

        # Update UI components
        self.video_view.update_frame(annotated_frame)
        self.detection_panel.update_metrics(fps, avg_lat, res, detections)

        if not self.btn_stop.isEnabled():
            self.btn_stop.setEnabled(True)
            self.btn_screenshot.setEnabled(True)
            self.cam_status_label.setText("Camera: Active")
            self.cam_status_label.setStyleSheet("color: #10B981; font-weight: bold;")

    def _on_model_loaded(self, success: bool, message: str) -> None:
        """Slot called when model loading status is updated."""
        if success:
            self.model_status_label.setText("Model: Ready (CPU)")
            self.model_status_label.setStyleSheet("color: #10B981; font-weight: bold;")
        else:
            self.model_status_label.setText("Model: Error")
            self.model_status_label.setStyleSheet("color: #F43F5E; font-weight: bold;")

    def _on_worker_error(self, message: str) -> None:
        """Slot called when worker encounters a critical camera/inference error."""
        self.video_view.show_error(message)
        QMessageBox.warning(self, "Camera / Detection Error", message)
        self.stop_detection()

    def _on_worker_stopped(self) -> None:
        """Slot called when worker thread fully finishes execution."""
        self.worker = None
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.btn_screenshot.setEnabled(False)
        self.cam_status_label.setText("Camera: Offline")
        self.cam_status_label.setStyleSheet("color: #94A3B8;")
        self.detection_panel.reset()
        self.video_view.show_placeholder("Camera Stopped.\n\nClick 'Start Camera' to resume object detection.")

    def take_screenshot(self) -> None:
        """Saves current annotated frame to disk as PNG."""
        if self.latest_annotated_frame is None:
            QMessageBox.information(self, "Screenshot", "No frame available to save.")
            return

        try:
            save_dir = self.config.get_resolved_screenshot_dir()
            filename = f"detection_{time.strftime('%Y%m%d_%H%M%S')}.png"
            target_path = save_dir / filename

            # Write image using OpenCV
            success = cv2.imwrite(str(target_path), self.latest_annotated_frame)
            if success:
                QMessageBox.information(
                    self,
                    "Screenshot Saved",
                    f"Screenshot saved successfully to:\n\n{target_path}"
                )
            else:
                QMessageBox.critical(
                    self,
                    "Save Failed",
                    f"Could not write image file to {target_path}."
                )
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save screenshot: {e}")

    def _open_settings(self) -> None:
        """Opens settings dialog and applies changes."""
        dialog = SettingsDialog(config=self.config, parent=self)
        if dialog.exec() == QDialog.Accepted:
            # Update config and notify running worker if active
            self.config = dialog.config
            if self.worker is not None and self.worker.isRunning():
                self.worker.update_config(self.config)

    def _open_help(self) -> None:
        """Displays informative Help and About dialog."""
        msg = (
            "<h3>Webcam Object Detector v0.1.0</h3>"
            "<p>A real-time desktop application built for Debian 13 GNOME using Python, PySide6, OpenCV, and YOLOv8.</p>"
            "<b>Key Features:</b>"
            "<ul>"
            "<li>Local CPU inference using YOLO pretrained nano model</li>"
            "<li>Live FPS and latency measurements</li>"
            "<li>Annotated bounding boxes, category labels, and confidence percentages</li>"
            "<li>High contrast screenshot capture</li>"
            "</ul>"
            "<b>Pretrained Categories:</b>"
            "<p>Recognizes 80 COCO categories (people, vehicles, animals, common household items, electronics, etc.).</p>"
            "<p><i>Note: The model recognizes only pretrained COCO classes.</i></p>"
        )
        QMessageBox.about(self, "About Webcam Object Detector", msg)

    def closeEvent(self, event) -> None:
        """Ensures worker thread is stopped before exiting application."""
        if self.worker is not None and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(2000)
        event.accept()
