"""Detection and performance information panel widget."""

from typing import Dict, Tuple
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QListWidget, QListWidgetItem
)

from webcam_detector.detector import FrameDetections


class DetectionPanelWidget(QFrame):
    """Side panel displaying detected objects breakdown and live performance stats."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedWidth(280)
        self.setStyleSheet("""
            QFrame {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # --- Section 1: Performance Stats ---
        perf_title = QLabel("PERFORMANCE METRICS", self)
        perf_title.setStyleSheet("color: #10B981; font-weight: bold; font-size: 11px; letter-spacing: 1px;")
        layout.addWidget(perf_title)

        perf_grid = QVBoxLayout()
        perf_grid.setSpacing(8)

        # FPS Row
        fps_box = QHBoxLayout()
        fps_label = QLabel("Frame Rate:", self)
        fps_label.setStyleSheet("color: #94A3B8; font-size: 13px;")
        self.fps_value = QLabel("0.0 FPS", self)
        self.fps_value.setStyleSheet("color: #10B981; font-weight: bold; font-size: 14px;")
        fps_box.addWidget(fps_label)
        fps_box.addStretch()
        fps_box.addWidget(self.fps_value)
        perf_grid.addLayout(fps_box)

        # Latency Row
        lat_box = QHBoxLayout()
        lat_label = QLabel("Inference Time:", self)
        lat_label.setStyleSheet("color: #94A3B8; font-size: 13px;")
        self.lat_value = QLabel("0.0 ms", self)
        self.lat_value.setStyleSheet("color: #38BDF8; font-weight: bold; font-size: 14px;")
        lat_box.addWidget(lat_label)
        lat_box.addStretch()
        lat_box.addWidget(self.lat_value)
        perf_grid.addLayout(lat_box)

        # Resolution Row
        res_box = QHBoxLayout()
        res_label = QLabel("Input Resolution:", self)
        res_label.setStyleSheet("color: #94A3B8; font-size: 13px;")
        self.res_value = QLabel("640x480", self)
        self.res_value.setStyleSheet("color: #F8FAFC; font-size: 13px;")
        res_box.addWidget(res_label)
        res_box.addStretch()
        res_box.addWidget(self.res_value)
        perf_grid.addLayout(res_box)

        # Device Row
        dev_box = QHBoxLayout()
        dev_label = QLabel("Engine / Device:", self)
        dev_label.setStyleSheet("color: #94A3B8; font-size: 13px;")
        self.dev_value = QLabel("YOLOv8n (CPU)", self)
        self.dev_value.setStyleSheet("color: #F8FAFC; font-size: 13px;")
        dev_box.addWidget(dev_label)
        dev_box.addStretch()
        dev_box.addWidget(self.dev_value)
        perf_grid.addLayout(dev_box)

        layout.addLayout(perf_grid)

        # Divider
        divider = QFrame(self)
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("background-color: #334155; max-height: 1px;")
        layout.addWidget(divider)

        # --- Section 2: Detections Breakdown ---
        det_title = QLabel("DETECTED OBJECTS", self)
        det_title.setStyleSheet("color: #10B981; font-weight: bold; font-size: 11px; letter-spacing: 1px;")
        layout.addWidget(det_title)

        # Total Count
        count_box = QHBoxLayout()
        total_label = QLabel("Total Objects:", self)
        total_label.setStyleSheet("color: #E2E8F0; font-size: 14px; font-weight: 600;")
        self.total_value = QLabel("0", self)
        self.total_value.setStyleSheet("color: #10B981; font-weight: bold; font-size: 18px;")
        count_box.addWidget(total_label)
        count_box.addStretch()
        count_box.addWidget(self.total_value)
        layout.addLayout(count_box)

        # Class list widget
        self.class_list = QListWidget(self)
        self.class_list.setStyleSheet("""
            QListWidget {
                background-color: #0F172A;
                border: 1px solid #334155;
                border-radius: 6px;
                color: #F8FAFC;
                padding: 4px;
            }
            QListWidget::item {
                padding: 6px;
                border-bottom: 1px solid #1E293B;
            }
        """)
        layout.addWidget(self.class_list)

        # Empty state label
        self.empty_label = QLabel("No objects currently detected", self)
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("color: #64748B; font-style: italic; font-size: 12px; margin-top: 10px;")
        layout.addWidget(self.empty_label)

        layout.addStretch()

    def update_metrics(
        self,
        fps: float,
        latency_ms: float,
        resolution: Tuple[int, int],
        detections: FrameDetections
    ) -> None:
        """Updates display labels with live data."""
        self.fps_value.setText(f"{fps:.1f} FPS")
        self.lat_value.setText(f"{latency_ms:.1f} ms")
        self.res_value.setText(f"{resolution[0]}x{resolution[1]}")

        total = len(detections.detections)
        self.total_value.setText(str(total))

        self.class_list.clear()

        if total == 0:
            self.class_list.hide()
            self.empty_label.show()
        else:
            self.empty_label.hide()
            self.class_list.show()

            for cls_name, count in sorted(detections.class_counts.items()):
                item_str = f"•  {cls_name}: {count}"
                item = QListWidgetItem(item_str)
                item.setForeground(Qt.white)
                self.class_list.addItem(item)

    def reset(self) -> None:
        """Resets panel to zero metrics state."""
        self.fps_value.setText("0.0 FPS")
        self.lat_value.setText("0.0 ms")
        self.total_value.setText("0")
        self.class_list.clear()
        self.class_list.hide()
        self.empty_label.show()
