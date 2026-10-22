"""Settings dialog widget for webcam and detection preferences."""

from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSlider, QCheckBox, QFileDialog, QGroupBox, QWidget, QMessageBox
)

from webcam_detector.camera import list_available_cameras
from webcam_detector.config import AppConfig, save_config


class SettingsDialog(QDialog):
    """Modal dialog allowing user to configure camera, resolution, threshold, overlays, and paths."""

    def __init__(self, config: AppConfig, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Application Settings - Webcam Object Detector")
        self.setFixedSize(480, 520)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # --- Section 1: Camera & Hardware ---
        cam_group = QGroupBox("Camera & Hardware", self)
        cam_layout = QVBoxLayout(cam_group)
        cam_layout.setSpacing(12)

        # Camera selection
        cam_row = QHBoxLayout()
        cam_label = QLabel("Camera Device:", self)
        self.cam_combo = QComboBox(self)

        # Scan available cameras
        avail_cams = list_available_cameras(5)
        if self.config.camera.index not in avail_cams:
            avail_cams.append(self.config.camera.index)
        avail_cams = sorted(list(set(avail_cams)))

        for idx in avail_cams:
            self.cam_combo.addItem(f"Camera Device #{idx}", idx)

        # Select current
        current_combo_idx = self.cam_combo.findData(self.config.camera.index)
        if current_combo_idx != -1:
            self.cam_combo.setCurrentIndex(current_combo_idx)

        cam_row.addWidget(cam_label)
        cam_row.addStretch()
        cam_row.addWidget(self.cam_combo)
        cam_layout.addLayout(cam_row)

        # Resolution selection
        res_row = QHBoxLayout()
        res_label = QLabel("Resolution:", self)
        self.res_combo = QComboBox(self)
        self.res_combo.addItem("640 x 480 (Recommended for CPU)", (640, 480))
        self.res_combo.addItem("800 x 600", (800, 600))
        self.res_combo.addItem("1280 x 720 (HD)", (1280, 720))

        cur_res = (self.config.camera.width, self.config.camera.height)
        res_idx = self.res_combo.findData(cur_res)
        if res_idx != -1:
            self.res_combo.setCurrentIndex(res_idx)
        else:
            self.res_combo.setCurrentIndex(0)

        res_row.addWidget(res_label)
        res_row.addStretch()
        res_row.addWidget(self.res_combo)
        cam_layout.addLayout(res_row)

        layout.addWidget(cam_group)

        # --- Section 2: Detection Settings ---
        det_group = QGroupBox("Detection Parameters", self)
        det_layout = QVBoxLayout(det_group)
        det_layout.setSpacing(12)

        # Confidence slider
        conf_row = QHBoxLayout()
        conf_label = QLabel("Confidence Threshold:", self)
        self.conf_value_label = QLabel(f"{int(self.config.detection.confidence_threshold * 100)}%", self)
        self.conf_value_label.setStyleSheet("color: #10B981; font-weight: bold;")
        conf_row.addWidget(conf_label)
        conf_row.addStretch()
        conf_row.addWidget(self.conf_value_label)
        det_layout.addLayout(conf_row)

        self.conf_slider = QSlider(Qt.Horizontal, self)
        self.conf_slider.setRange(5, 95)
        self.conf_slider.setValue(int(self.config.detection.confidence_threshold * 100))
        self.conf_slider.valueChanged.connect(
            lambda val: self.conf_value_label.setText(f"{val}%")
        )
        det_layout.addWidget(self.conf_slider)

        # Overlay toggles
        self.cb_boxes = QCheckBox("Show Bounding Boxes", self)
        self.cb_boxes.setChecked(self.config.detection.show_boxes)
        det_layout.addWidget(self.cb_boxes)

        self.cb_labels = QCheckBox("Show Class Labels", self)
        self.cb_labels.setChecked(self.config.detection.show_labels)
        det_layout.addWidget(self.cb_labels)

        self.cb_conf = QCheckBox("Show Confidence Scores", self)
        self.cb_conf.setChecked(self.config.detection.show_confidence)
        det_layout.addWidget(self.cb_conf)

        layout.addWidget(det_group)

        # --- Section 3: Storage & Paths ---
        path_group = QGroupBox("Storage & Paths", self)
        path_layout = QVBoxLayout(path_group)

        shot_row = QHBoxLayout()
        shot_label = QLabel("Screenshot Folder:", self)
        path_layout.addWidget(shot_label)

        shot_path_row = QHBoxLayout()
        self.shot_path_display = QLabel(self.config.paths.screenshot_dir, self)
        self.shot_path_display.setStyleSheet("color: #94A3B8; background-color: #0F172A; padding: 4px 8px; border-radius: 4px;")
        btn_browse = QPushButton("Browse...", self)
        btn_browse.clicked.connect(self._browse_screenshot_dir)

        shot_path_row.addWidget(self.shot_path_display, stretch=1)
        shot_path_row.addWidget(btn_browse)
        path_layout.addLayout(shot_path_row)

        layout.addWidget(path_group)

        # --- Buttons ---
        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Cancel", self)
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("Save Settings", self)
        btn_save.setProperty("class", "btn-primary")
        btn_save.setStyleSheet("background-color: #059669; color: white; font-weight: bold;")
        btn_save.clicked.connect(self._save_and_close)

        btn_row.addStretch()
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)

    def _browse_screenshot_dir(self) -> None:
        """Opens directory picker for screenshot location."""
        cur_path = str(Path(self.config.paths.screenshot_dir).expanduser())
        dir_path = QFileDialog.getExistingDirectory(self, "Select Screenshot Directory", cur_path)
        if dir_path:
            self.shot_path_display.setText(dir_path)

    def _save_and_close(self) -> None:
        """Applies UI choices to config object, persists to disk, and closes dialog."""
        # Camera
        selected_cam_idx = self.cam_combo.currentData()
        if selected_cam_idx is not None:
            self.config.camera.index = int(selected_cam_idx)

        res_tuple = self.res_combo.currentData()
        if res_tuple:
            self.config.camera.width = res_tuple[0]
            self.config.camera.height = res_tuple[1]

        # Detection
        self.config.detection.confidence_threshold = self.conf_slider.value() / 100.0
        self.config.detection.show_boxes = self.cb_boxes.isChecked()
        self.config.detection.show_labels = self.cb_labels.isChecked()
        self.config.detection.show_confidence = self.cb_conf.isChecked()

        # Paths
        self.config.paths.screenshot_dir = self.shot_path_display.text()

        # Persist
        save_config(self.config)
        self.accept()
