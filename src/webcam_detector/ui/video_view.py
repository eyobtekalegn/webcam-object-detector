"""Video preview display widget with aspect ratio scaling, placeholder, and overlays."""

import numpy as np
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QImage, QPixmap, QPainter, QColor, QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame


class VideoViewWidget(QFrame):
    """Displays webcam frames cleanly, scaling aspect ratio and showing helpful empty/error states."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("videoFrame")
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame#videoFrame {
                background-color: #0B1120;
                border: 1px solid #334155;
                border-radius: 8px;
            }
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("Camera Offline\n\nClick 'Start Camera' to begin object detection.")
        self.image_label.setStyleSheet("color: #64748B; font-size: 15px; font-weight: 500;")
        self.layout.addWidget(self.image_label)

        self._current_pixmap: QPixmap | None = None

    def update_frame(self, frame_bgr: np.ndarray) -> None:
        """Converts OpenCV BGR numpy array to QPixmap and displays it centered."""
        h, w, ch = frame_bgr.shape
        bytes_per_line = ch * w

        # BGR to RGB conversion
        rgb_frame = frame_bgr[:, :, ::-1].copy()

        q_img = QImage(
            rgb_frame.data,
            w,
            h,
            bytes_per_line,
            QImage.Format_RGB888
        )
        pixmap = QPixmap.fromImage(q_img)
        self._current_pixmap = pixmap
        self._render_pixmap()

    def show_placeholder(self, message: str = "Camera Offline\n\nClick 'Start Camera' to begin.") -> None:
        """Resets view to dark placeholder state with text message."""
        self._current_pixmap = None
        self.image_label.setPixmap(QPixmap())
        self.image_label.setText(message)
        self.image_label.setStyleSheet("color: #64748B; font-size: 15px; font-weight: 500;")

    def show_error(self, message: str) -> None:
        """Displays error message on video panel."""
        self._current_pixmap = None
        self.image_label.setPixmap(QPixmap())
        self.image_label.setText(f"⚠️ {message}")
        self.image_label.setStyleSheet("color: #F43F5E; font-size: 14px; font-weight: 600; padding: 16px;")

    def _render_pixmap(self) -> None:
        """Scales current pixmap maintaining aspect ratio to fit label size."""
        if self._current_pixmap is None or self._current_pixmap.isNull():
            return

        target_size = self.image_label.size()
        if target_size.width() <= 0 or target_size.height() <= 0:
            return

        scaled_pixmap = self._current_pixmap.scaled(
            target_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)

    def resizeEvent(self, event) -> None:
        """Handles widget resize events by rescaling video preview."""
        super().resizeEvent(event)
        self._render_pixmap()
