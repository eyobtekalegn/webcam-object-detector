"""Camera access and frame acquisition module."""

import logging
from typing import List, Tuple, Optional
import cv2
import numpy as np

logger = logging.getLogger("webcam_detector.camera")


def list_available_cameras(max_tested: int = 5) -> List[int]:
    """Scans indices 0 to max_tested-1 to find accessible camera devices.

    Returns a list of integer camera indices that can be successfully opened.
    """
    available = []
    for idx in range(max_tested):
        cap = cv2.VideoCapture(idx)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                available.append(idx)
            cap.release()
    return available


class CameraManager:
    """Manages OpenCV VideoCapture lifecycle safely and predictably."""

    def __init__(self) -> None:
        self._cap: Optional[cv2.VideoCapture] = None
        self._current_index: Optional[int] = None
        self._width: int = 640
        self._height: int = 480

    def open_camera(self, index: int = 0, width: int = 640, height: int = 480, fps: int = 30) -> bool:
        """Opens specified camera and configures resolution.

        Args:
            index: Camera index (e.g. 0).
            width: Preferred frame width.
            height: Preferred frame height.
            fps: Target FPS limit.

        Returns:
            True if camera opened successfully, False otherwise.
        """
        self.release()

        try:
            logger.info(f"Attempting to open camera index {index} with resolution {width}x{height} @ {fps}fps")
            cap = cv2.VideoCapture(index)
            if not cap.isOpened():
                logger.error(f"Failed to open camera index {index}")
                return False

            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            cap.set(cv2.CAP_PROP_FPS, fps)

            # Test frame read
            ret, frame = cap.read()
            if not ret or frame is None or frame.size == 0:
                logger.error(f"Camera index {index} opened but failed to read initial frame")
                cap.release()
                return False

            actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            logger.info(f"Camera {index} opened successfully (Actual resolution: {actual_w}x{actual_h})")

            self._cap = cap
            self._current_index = index
            self._width = actual_w if actual_w > 0 else width
            self._height = actual_h if actual_h > 0 else height
            return True
        except Exception as e:
            logger.error(f"Unexpected exception while opening camera index {index}: {e}")
            self.release()
            return False

    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Reads a frame from the opened camera.

        Returns:
            Tuple (success: bool, frame: Optional[np.ndarray])
        """
        if self._cap is None or not self._cap.isOpened():
            return False, None

        try:
            ret, frame = self._cap.read()
            if not ret or frame is None or frame.size == 0:
                logger.warning("Failed to read frame from camera")
                return False, None
            return True, frame
        except Exception as e:
            logger.error(f"Exception during frame read: {e}")
            return False, None

    def is_opened(self) -> bool:
        """Returns True if a camera is currently open and active."""
        return self._cap is not None and self._cap.isOpened()

    def get_resolution(self) -> Tuple[int, int]:
        """Returns (width, height) of current camera feed."""
        return self._width, self._height

    def get_current_index(self) -> Optional[int]:
        """Returns index of current active camera or None."""
        return self._current_index

    def release(self) -> None:
        """Safely releases the camera resource."""
        if self._cap is not None:
            try:
                logger.info(f"Releasing camera resource (index {self._current_index})")
                self._cap.release()
            except Exception as e:
                logger.warning(f"Error releasing camera: {e}")
            finally:
                self._cap = None
                self._current_index = None
