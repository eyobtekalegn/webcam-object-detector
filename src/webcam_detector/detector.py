"""Object detection engine module using YOLO via ultralytics."""

from dataclasses import dataclass, field
import logging
from pathlib import Path
import time
from typing import List, Dict, Tuple, Optional
import numpy as np

logger = logging.getLogger("webcam_detector.detector")


@dataclass
class DetectionResult:
    """Class representing a single object detection."""
    class_id: int
    class_name: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)


@dataclass
class FrameDetections:
    """Class representing all detections and performance metadata for a frame."""
    detections: List[DetectionResult] = field(default_factory=list)
    inference_time_ms: float = 0.0
    class_counts: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        if not self.class_counts and self.detections:
            counts: Dict[str, int] = {}
            for d in self.detections:
                counts[d.class_name] = counts.get(d.class_name, 0) + 1
            self.class_counts = counts


class ObjectDetector:
    """Loads pretrained YOLO nano model and performs CPU-based inference."""

    def __init__(self, model_name: str = "yolov8n.pt", model_dir: Optional[Path] = None) -> None:
        self.model_name = model_name
        self.model_dir = model_dir or (Path.home() / ".cache" / "webcam_detector" / "models")
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self._model = None
        self._names: Dict[int, str] = {}

    def load_model(self) -> bool:
        """Loads YOLO model onto CPU.

        Downloads weights to model_dir if not present locally.
        """
        try:
            from ultralytics import YOLO

            target_model_path = self.model_dir / self.model_name
            if target_model_path.is_file():
                load_target = str(target_model_path)
                logger.info(f"Loading YOLO model from local cache: {load_target}")
            else:
                load_target = self.model_name
                logger.info(f"Local weight {target_model_path} not found. Loading/downloading {self.model_name}")

            # Instantiate model
            model = YOLO(load_target)

            # Save downloaded weights to cache directory if downloaded to current working dir
            if not target_model_path.is_file() and Path(self.model_name).is_file():
                try:
                    Path(self.model_name).rename(target_model_path)
                    model = YOLO(str(target_model_path))
                except Exception as err:
                    logger.warning(f"Could not relocate model weights to {target_model_path}: {err}")

            self._model = model
            self._names = model.names if hasattr(model, "names") else {}
            logger.info("YOLO model loaded successfully on CPU.")
            return True
        except Exception as e:
            logger.error(f"Failed to load YOLO model {self.model_name}: {e}")
            self._model = None
            return False

    def is_loaded(self) -> bool:
        """Returns True if model is initialized and ready."""
        return self._model is not None

    def detect(self, frame: np.ndarray, confidence_threshold: float = 0.45) -> FrameDetections:
        """Runs object detection on a single frame.

        Args:
            frame: OpenCV BGR image (np.ndarray).
            confidence_threshold: Confidence filtering threshold (0.0 to 1.0).

        Returns:
            FrameDetections containing list of DetectionResult objects and latency.
        """
        if self._model is None:
            return FrameDetections()

        start_time = time.perf_counter()
        try:
            # Perform inference on CPU explicitly
            results = self._model.predict(
                source=frame,
                conf=confidence_threshold,
                device="cpu",
                verbose=False
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            detections: List[DetectionResult] = []
            class_counts: Dict[str, int] = {}

            if results and len(results) > 0:
                boxes = results[0].boxes
                if boxes is not None and len(boxes) > 0:
                    xyxy_coords = boxes.xyxy.cpu().numpy()
                    confs = boxes.conf.cpu().numpy()
                    cls_ids = boxes.cls.cpu().numpy().astype(int)

                    for bbox, conf, cls_id in zip(xyxy_coords, confs, cls_ids):
                        x1, y1, x2, y2 = map(int, bbox)
                        c_val = float(conf)
                        c_id = int(cls_id)
                        c_name = self._names.get(c_id, f"class_{c_id}")

                        det = DetectionResult(
                            class_id=c_id,
                            class_name=c_name,
                            confidence=c_val,
                            bbox=(x1, y1, x2, y2)
                        )
                        detections.append(det)
                        class_counts[c_name] = class_counts.get(c_name, 0) + 1

            return FrameDetections(
                detections=detections,
                inference_time_ms=elapsed_ms,
                class_counts=class_counts
            )
        except Exception as e:
            logger.error(f"Inference error during detect(): {e}")
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return FrameDetections(inference_time_ms=elapsed_ms)
