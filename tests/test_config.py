"""Unit tests for configuration loading, validation, saving, and defaults."""

import json
from pathlib import Path
import tempfile
import pytest

from webcam_detector.config import (
    AppConfig, CameraConfig, DetectionConfig, PathsConfig,
    load_config, save_config, parse_config_dict
)


def test_default_config_values():
    cfg = AppConfig()
    assert cfg.camera.index == 0
    assert cfg.camera.width == 640
    assert cfg.camera.height == 480
    assert cfg.detection.model_name == "yolov8n.pt"
    assert cfg.detection.confidence_threshold == 0.45
    assert cfg.detection.show_boxes is True


def test_parse_config_dict_bounds():
    data = {
        "camera": {
            "index": -5,
            "width": 10000,
            "height": 10,
            "fps": 500
        },
        "detection": {
            "confidence_threshold": 1.5,
            "show_boxes": False
        }
    }
    cfg = parse_config_dict(data)
    assert cfg.camera.index == 0  # Invalid negative clamped to 0
    assert cfg.camera.width == 640  # Out of bounds reset to default 640
    assert cfg.camera.height == 480  # Out of bounds reset to default 480
    assert cfg.camera.fps == 30  # Out of bounds reset to 30
    assert cfg.detection.confidence_threshold == 0.99  # Clamped to 0.99
    assert cfg.detection.show_boxes is False


def test_save_and_load_config():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_file = Path(tmpdir) / "user_config.json"

        cfg = AppConfig()
        cfg.camera.width = 1280
        cfg.camera.height = 720
        cfg.detection.confidence_threshold = 0.60

        saved = save_config(cfg, user_config_file=tmp_file)
        assert saved is True
        assert tmp_file.is_file()

        loaded_cfg = load_config(user_config_file=tmp_file)
        assert loaded_cfg.camera.width == 1280
        assert loaded_cfg.camera.height == 720
        assert loaded_cfg.detection.confidence_threshold == 0.60
