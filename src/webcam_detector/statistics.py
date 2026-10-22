"""Performance statistics and metrics calculator."""

import collections
import time
from typing import Dict, Deque


class PerformanceTracker:
    """Calculates smoothed real-time FPS and latency metrics using a sliding window."""

    def __init__(self, window_size: int = 30) -> None:
        self.window_size = window_size
        self._frame_timestamps: Deque[float] = collections.deque(maxlen=window_size)
        self._inference_latencies: Deque[float] = collections.deque(maxlen=window_size)
        self._fps: float = 0.0

    def update(self, inference_ms: float) -> None:
        """Records a new frame processing event and updates metrics.

        Args:
            inference_ms: Inference duration in milliseconds for the current frame.
        """
        now = time.perf_counter()
        self._frame_timestamps.append(now)
        self._inference_latencies.append(inference_ms)

        if len(self._frame_timestamps) > 1:
            duration = self._frame_timestamps[-1] - self._frame_timestamps[0]
            if duration > 0:
                self._fps = (len(self._frame_timestamps) - 1) / duration
            else:
                self._fps = 0.0
        else:
            self._fps = 0.0

    def get_fps(self) -> float:
        """Returns calculated frames per second."""
        return self._fps

    def get_average_latency_ms(self) -> float:
        """Returns average inference latency in milliseconds over window."""
        if not self._inference_latencies:
            return 0.0
        return sum(self._inference_latencies) / len(self._inference_latencies)

    def reset(self) -> None:
        """Clears all historical statistics."""
        self._frame_timestamps.clear()
        self._inference_latencies.clear()
        self._fps = 0.0


def format_class_counts(class_counts: Dict[str, int]) -> str:
    """Formats class counts dictionary into a readable summary string."""
    if not class_counts:
        return "No objects detected"
    items = [f"{cls}: {count}" for cls, count in sorted(class_counts.items())]
    return ", ".join(items)
