"""Unit tests for ObjectDetector normalization and error handling with mocks."""

from pathlib import Path
from unittest.mock import MagicMock, patch
import numpy as np
import pytest

from webcam_detector.detector import ObjectDetector, FrameDetections, DetectionResult


def test_detector_initialization():
    detector = ObjectDetector(model_name="yolov8n.pt")
    assert detector.model_name == "yolov8n.pt"
    assert not detector.is_loaded()


@patch("ultralytics.YOLO")
def test_detector_load_model(mock_yolo):
    mock_model_instance = MagicMock()
    mock_model_instance.names = {0: "person", 1: "bicycle"}
    mock_yolo.return_value = mock_model_instance

    detector = ObjectDetector(model_name="yolov8n.pt")
    success = detector.load_model()

    assert success is True
    assert detector.is_loaded() is True


@patch("ultralytics.YOLO")
def test_detector_detect_mock_output(mock_yolo):
    mock_model_instance = MagicMock()
    mock_model_instance.names = {0: "person", 1: "chair"}

    # Mock Ultralytics result format
    mock_boxes = MagicMock()
    mock_boxes.__len__.return_value = 1
    mock_boxes.xyxy.cpu().numpy.return_value = np.array([[10, 20, 100, 200]])
    mock_boxes.conf.cpu().numpy.return_value = np.array([0.92])
    mock_boxes.cls.cpu().numpy.return_value = np.array([0])

    mock_result = MagicMock()
    mock_result.boxes = mock_boxes

    mock_model_instance.predict.return_value = [mock_result]
    mock_yolo.return_value = mock_model_instance

    detector = ObjectDetector(model_name="yolov8n.pt")
    detector.load_model()

    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    res = detector.detect(frame, confidence_threshold=0.5)

    assert isinstance(res, FrameDetections)
    assert len(res.detections) == 1
    assert res.detections[0].class_name == "person"
    assert res.detections[0].confidence == 0.92
    assert res.class_counts == {"person": 1}
    assert res.inference_time_ms >= 0.0
