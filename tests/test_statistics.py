"""Unit tests for performance metrics tracker and class counting."""

import time
import pytest

from webcam_detector.statistics import PerformanceTracker, format_class_counts


def test_performance_tracker_calculation():
    tracker = PerformanceTracker(window_size=10)
    assert tracker.get_fps() == 0.0
    assert tracker.get_average_latency_ms() == 0.0

    # Simulate 5 frames
    for i in range(5):
        tracker.update(inference_ms=10.0 + i)
        time.sleep(0.01)

    assert tracker.get_fps() > 0.0
    assert 10.0 <= tracker.get_average_latency_ms() <= 14.0


def test_performance_tracker_reset():
    tracker = PerformanceTracker(window_size=10)
    tracker.update(15.0)
    tracker.reset()

    assert tracker.get_fps() == 0.0
    assert tracker.get_average_latency_ms() == 0.0


def test_format_class_counts():
    assert format_class_counts({}) == "No objects detected"
    counts = {"person": 2, "car": 1}
    formatted = format_class_counts(counts)
    assert "car: 1" in formatted
    assert "person: 2" in formatted
