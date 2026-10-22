"""Frame rendering and overlay module."""

from typing import List, Tuple
import cv2
import numpy as np

from webcam_detector.detector import DetectionResult, FrameDetections


# Distinctive color palette (BGR) for categories with emerald green as primary accent
EMERALD_GREEN = (103, 209, 16)   # #10B981 in BGR: B=16, G=185, R=16 -> (103, 209, 16)
TEAL_CYAN     = (222, 187, 6)    # Teal accent
AMBER_ORANGE  = (21, 158, 245)   # Warm amber accent
VIOLET_PURPLE = (209, 88, 139)   # Violet accent
ELECTRIC_BLUE = (250, 164, 59)   # Light blue accent

COLOR_PALETTE = [
    EMERALD_GREEN,
    TEAL_CYAN,
    AMBER_ORANGE,
    VIOLET_PURPLE,
    ELECTRIC_BLUE,
]


def get_color_for_class(class_id: int) -> Tuple[int, int, int]:
    """Generates consistent BGR color for class ID."""
    return COLOR_PALETTE[class_id % len(COLOR_PALETTE)]


def clip_bbox(
    bbox: Tuple[int, int, int, int],
    frame_width: int,
    frame_height: int
) -> Tuple[int, int, int, int]:
    """Clips bounding box coordinates to frame boundary."""
    x1, y1, x2, y2 = bbox
    x1_c = max(0, min(x1, frame_width - 1))
    y1_c = max(0, min(y1, frame_height - 1))
    x2_c = max(0, min(x2, frame_width - 1))
    y2_c = max(0, min(y2, frame_height - 1))
    return x1_c, y1_c, x2_c, y2_c


def render_overlays(
    frame: np.ndarray,
    detections: FrameDetections,
    show_boxes: bool = True,
    show_labels: bool = True,
    show_confidence: bool = True
) -> np.ndarray:
    """Draws bounding boxes and class labels onto a frame.

    Args:
        frame: OpenCV BGR image array.
        detections: FrameDetections object containing detected objects.
        show_boxes: Whether to draw bounding box rectangles.
        show_labels: Whether to draw text class names.
        show_confidence: Whether to append confidence score to labels.

    Returns:
        Annotated BGR frame (np.ndarray).
    """
    if not show_boxes and not show_labels:
        return frame

    annotated = frame.copy()
    h, w = annotated.shape[:2]

    for det in detections.detections:
        x1, y1, x2, y2 = clip_bbox(det.bbox, w, h)
        color = get_color_for_class(det.class_id)

        # Draw bounding box
        if show_boxes:
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, thickness=2, lineType=cv2.LINE_AA)

        # Draw label header tag
        if show_labels:
            label_text = det.class_name
            if show_confidence:
                label_text += f" {det.confidence * 100:.1f}%"

            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            thickness = 1

            (text_w, text_h), baseline = cv2.getTextSize(label_text, font, font_scale, thickness)

            # Position text badge above bounding box if space allows, otherwise inside
            badge_y1 = max(0, y1 - text_h - 6)
            badge_y2 = badge_y1 + text_h + 6
            badge_x1 = x1
            badge_x2 = min(w, x1 + text_w + 8)

            # Draw label background box
            cv2.rectangle(
                annotated,
                (badge_x1, badge_y1),
                (badge_x2, badge_y2),
                color,
                thickness=-1  # Filled
            )

            # Text color (dark navy/black for high contrast on bright tag)
            text_color = (20, 24, 33)
            text_x = badge_x1 + 4
            text_y = badge_y2 - 4

            cv2.putText(
                annotated,
                label_text,
                (text_x, text_y),
                font,
                font_scale,
                text_color,
                thickness,
                lineType=cv2.LINE_AA
            )

    return annotated
