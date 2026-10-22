"""Unit tests for frame rendering and coordinate clipping."""

import numpy as np
import pytest

from webcam_detector.detector import DetectionResult, FrameDetections
from webcam_detector.rendering import clip_bbox, get_color_for_class, render_overlays


def test_clip_bbox():
    w, h = 640, 480
    # Inside bounds
    assert clip_bbox((10, 20, 100, 200), w, h) == (10, 20, 100, 200)
    # Out of bounds left/top
    assert clip_bbox((-50, -10, 100, 200), w, h) == (0, 0, 100, 200)
    # Out of bounds right/bottom
    assert clip_bbox((10, 20, 800, 600), w, h) == (10, 20, 639, 479)


def test_get_color_for_class():
    c0 = get_color_for_class(0)
    c1 = get_color_for_class(1)
    assert len(c0) == 3
    assert isinstance(c0, tuple)


def test_render_overlays_drawing():
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    det = DetectionResult(
        class_id=0,
        class_name="person",
        confidence=0.85,
        bbox=(50, 50, 200, 300)
    )
    frame_dets = FrameDetections(detections=[det])

    annotated = render_overlays(
        frame,
        frame_dets,
        show_boxes=True,
        show_labels=True,
        show_confidence=True
    )

    assert annotated.shape == frame.shape
    # Frame was modified by drawing
    assert not np.array_equal(frame, annotated)


def test_render_overlays_disabled():
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    det = DetectionResult(
        class_id=0,
        class_name="person",
        confidence=0.85,
        bbox=(50, 50, 200, 300)
    )
    frame_dets = FrameDetections(detections=[det])

    annotated = render_overlays(
        frame,
        frame_dets,
        show_boxes=False,
        show_labels=False,
        show_confidence=False
    )

    # When toggles are False, returns unchanged frame
    assert np.array_equal(frame, annotated)
