"""Multithreaded detection worker for PySide6 integration."""

import logging
import time
from typing import Optional
import numpy as np

from PySide6.QtCore import QThread, Signal

from webcam_detector.camera import CameraManager
from webcam_detector.config import AppConfig
from webcam_detector.detector import ObjectDetector, FrameDetections
from webcam_detector.rendering import render_overlays

logger = logging.getLogger("webcam_detector.worker")


class DetectionWorker(QThread):
    """Worker thread running webcam capture and YOLO inference outside main GUI thread.

    Emits thread-safe signals with annotated frames, raw frames, detection results, and stats.
    """

    # Signals
    # (annotated_frame_bgr, raw_frame_bgr, FrameDetections)
    frame_processed = Signal(np.ndarray, np.ndarray, object)
    # Error message
    error_occurred = Signal(str)
    # Model load status
    model_loaded = Signal(bool, str)
    # Worker stopped signal
    stopped = Signal()

    def __init__(self, config: AppConfig, parent: Optional[QThread] = None) -> None:
        super().__init__(parent)
        self.config = config
        self._running = False
        self._camera_manager = CameraManager()
        self._detector = ObjectDetector(
            model_name=config.detection.model_name,
            model_dir=config.get_resolved_model_dir()
        )

    def update_config(self, new_config: AppConfig) -> None:
        """Updates runtime configuration (e.g. thresholds or visual toggles)."""
        self.config = new_config

    def stop(self) -> None:
        """Signals thread loop to stop gracefully."""
        self._running = False

    def run(self) -> None:
        """Main thread loop."""
        self._running = True
        logger.info("DetectionWorker thread starting...")

        # 1. Load Object Detector
        if not self._detector.is_loaded():
            logger.info("Worker loading YOLO model...")
            success = self._detector.load_model()
            if not success:
                self.model_loaded.emit(False, "Failed to load YOLO model.")
                self.error_occurred.emit("Model Initialization Error: Could not load YOLO weights.")
                self._running = False
                self.stopped.emit()
                return
            self.model_loaded.emit(True, f"Loaded {self.config.detection.model_name}")

        # 2. Open Camera
        cam_cfg = self.config.camera
        opened = self._camera_manager.open_camera(
            index=cam_cfg.index,
            width=cam_cfg.width,
            height=cam_cfg.height,
            fps=cam_cfg.fps
        )

        if not opened:
            msg = (
                f"Camera Error: Could not open camera at index {cam_cfg.index}. "
                "Ensure camera is plugged in and not in use by another application."
            )
            logger.error(msg)
            self.error_occurred.emit(msg)
            self._running = False
            self.stopped.emit()
            return

        logger.info("Camera opened successfully. Starting capture loop.")

        # Main processing loop
        consecutive_read_failures = 0
        max_read_failures = 10

        try:
            while self._running:
                # Read raw frame from camera
                success, raw_frame = self._camera_manager.read_frame()

                if not success or raw_frame is None:
                    consecutive_read_failures += 1
                    logger.warning(f"Frame read failure ({consecutive_read_failures}/{max_read_failures})")
                    if consecutive_read_failures >= max_read_failures:
                        err_msg = "Camera disconnected or failed to supply valid frames."
                        logger.error(err_msg)
                        self.error_occurred.emit(err_msg)
                        break
                    time.sleep(0.03)
                    continue

                consecutive_read_failures = 0

                # Run local CPU inference
                det_cfg = self.config.detection
                detections = self._detector.detect(
                    frame=raw_frame,
                    confidence_threshold=det_cfg.confidence_threshold
                )

                # Render overlays
                annotated_frame = render_overlays(
                    frame=raw_frame,
                    detections=detections,
                    show_boxes=det_cfg.show_boxes,
                    show_labels=det_cfg.show_labels,
                    show_confidence=det_cfg.show_confidence
                )

                # Emit result signal
                if self._running:
                    self.frame_processed.emit(annotated_frame, raw_frame, detections)

                # Brief sleep to yield CPU if running faster than requested FPS
                time.sleep(0.001)

        except Exception as e:
            logger.error(f"Unexpected error in DetectionWorker loop: {e}", exc_info=True)
            self.error_occurred.emit(f"Unexpected processing error: {e}")

        finally:
            logger.info("Cleaning up camera and finishing worker thread...")
            self._camera_manager.release()
            self._running = False
            self.stopped.emit()
            logger.info("DetectionWorker thread stopped.")
