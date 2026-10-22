"""Configuration management for Webcam Object Detector."""

from dataclasses import dataclass, field, asdict
import json
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger("webcam_detector.config")


@dataclass
class CameraConfig:
    index: int = 0
    width: int = 640
    height: int = 480
    fps: int = 30


@dataclass
class DetectionConfig:
    model_name: str = "yolov8n.pt"
    confidence_threshold: float = 0.45
    show_boxes: bool = True
    show_labels: bool = True
    show_confidence: bool = True


@dataclass
class PathsConfig:
    screenshot_dir: str = "~/Pictures/WebcamDetector"
    model_dir: str = "~/.cache/webcam_detector/models"


@dataclass
class AppConfig:
    camera: CameraConfig = field(default_factory=CameraConfig)
    detection: DetectionConfig = field(default_factory=DetectionConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)

    def get_resolved_screenshot_dir(self) -> Path:
        """Returns screenshot directory path expanded and created if needed."""
        p = Path(self.paths.screenshot_dir).expanduser().resolve()
        p.mkdir(parents=True, exist_ok=True)
        return p

    def get_resolved_model_dir(self) -> Path:
        """Returns model directory path expanded and created if needed."""
        p = Path(self.paths.model_dir).expanduser().resolve()
        p.mkdir(parents=True, exist_ok=True)
        return p


def get_user_config_path() -> Path:
    """Returns path to user configuration file (~/.config/webcam_detector/config.json)."""
    user_config_dir = Path.home() / ".config" / "webcam_detector"
    user_config_dir.mkdir(parents=True, exist_ok=True)
    return user_config_dir / "config.json"


def get_default_config_path() -> Path:
    """Returns path to repository default configuration file if present."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    return base_dir / "configs" / "default.json"


def load_config(user_config_file: Path | None = None) -> AppConfig:
    """Loads configuration from user config file or default config file.

    Validates schema and fallback to safe defaults if malformed.
    """
    config_data: Dict[str, Any] = {}

    # Load project defaults first
    default_path = get_default_config_path()
    if default_path.is_file():
        try:
            with open(default_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except Exception as e:
            logger.warning(f"Error reading default config at {default_path}: {e}")

    # Override with user config if present
    target_user_path = user_config_file or get_user_config_path()
    if target_user_path.is_file():
        try:
            with open(target_user_path, "r", encoding="utf-8") as f:
                user_data = json.load(f)
                _deep_update(config_data, user_data)
        except Exception as e:
            logger.warning(f"Error reading user config at {target_user_path}, falling back: {e}")

    # Build AppConfig with validation
    return parse_config_dict(config_data)


def parse_config_dict(data: Dict[str, Any]) -> AppConfig:
    """Parses a dictionary into AppConfig with bounds/type checking."""
    cam_data = data.get("camera", {})
    det_data = data.get("detection", {})
    path_data = data.get("paths", {})

    # Camera validation
    try:
        cam_index = int(cam_data.get("index", 0))
        if cam_index < 0:
            cam_index = 0
    except (ValueError, TypeError):
        cam_index = 0

    try:
        width = int(cam_data.get("width", 640))
        if width < 160 or width > 3840:
            width = 640
    except (ValueError, TypeError):
        width = 640

    try:
        height = int(cam_data.get("height", 480))
        if height < 120 or height > 2160:
            height = 480
    except (ValueError, TypeError):
        height = 480

    try:
        fps = int(cam_data.get("fps", 30))
        if fps < 1 or fps > 120:
            fps = 30
    except (ValueError, TypeError):
        fps = 30

    camera_cfg = CameraConfig(index=cam_index, width=width, height=height, fps=fps)

    # Detection validation
    model_name = str(det_data.get("model_name", "yolov8n.pt"))
    try:
        conf_thresh = float(det_data.get("confidence_threshold", 0.45))
        conf_thresh = max(0.01, min(0.99, conf_thresh))
    except (ValueError, TypeError):
        conf_thresh = 0.45

    show_boxes = bool(det_data.get("show_boxes", True))
    show_labels = bool(det_data.get("show_labels", True))
    show_confidence = bool(det_data.get("show_confidence", True))

    detection_cfg = DetectionConfig(
        model_name=model_name,
        confidence_threshold=conf_thresh,
        show_boxes=show_boxes,
        show_labels=show_labels,
        show_confidence=show_confidence
    )

    # Paths validation
    screenshot_dir = str(path_data.get("screenshot_dir", "~/Pictures/WebcamDetector"))
    model_dir = str(path_data.get("model_dir", "~/.cache/webcam_detector/models"))
    paths_cfg = PathsConfig(screenshot_dir=screenshot_dir, model_dir=model_dir)

    return AppConfig(camera=camera_cfg, detection=detection_cfg, paths=paths_cfg)


def save_config(config: AppConfig, user_config_file: Path | None = None) -> bool:
    """Saves AppConfig to user configuration file."""
    target_path = user_config_file or get_user_config_path()
    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        config_dict = asdict(config)
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, indent=2)
        logger.info(f"Saved configuration to {target_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save configuration to {target_path}: {e}")
        return False


def _deep_update(source: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively updates source dict with overrides."""
    for key, value in overrides.items():
        if isinstance(value, dict) and key in source and isinstance(source[key], dict):
            _deep_update(source[key], value)
        else:
            source[key] = value
    return source
