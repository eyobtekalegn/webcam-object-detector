"""Application entry point and Qt Application initialization."""

import sys
from PySide6.QtWidgets import QApplication

from webcam_detector.logging_setup import setup_logging
from webcam_detector.ui.main_window import MainWindow


def create_app() -> QApplication:
    """Creates and configures QApplication instance."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    app.setApplicationName("Webcam Object Detector")
    app.setOrganizationName("WebcamDetector")
    return app


def run() -> None:
    """Runs the Webcam Object Detector application."""
    setup_logging()
    app = create_app()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
