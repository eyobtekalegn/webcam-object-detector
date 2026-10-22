"""UI Stylesheet and visual theme definition (Dark Navy/Charcoal + Emerald Green)."""

DARK_THEME_QSS = """
QMainWindow, QDialog {
    background-color: #0F172A;
    color: #F8FAFC;
    font-family: 'Segoe UI', 'Ubuntu', 'Roboto', sans-serif;
    font-size: 13px;
}

QWidget {
    background-color: transparent;
    color: #F8FAFC;
}

/* Panels and GroupBoxes */
QFrame.panel {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 8px;
}

QGroupBox {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 8px;
    margin-top: 24px;
    font-weight: bold;
    color: #10B981;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 8px;
    background-color: #0F172A;
    border: 1px solid #334155;
    border-radius: 4px;
    color: #10B981;
}

/* Labels */
QLabel {
    color: #E2E8F0;
}

QLabel.title-label {
    font-size: 18px;
    font-weight: bold;
    color: #F8FAFC;
}

QLabel.status-active {
    color: #10B981;
    font-weight: bold;
}

QLabel.status-inactive {
    color: #94A3B8;
}

QLabel.status-error {
    color: #F43F5E;
    font-weight: bold;
}

QLabel.metric-value {
    font-size: 16px;
    font-weight: bold;
    color: #10B981;
}

/* Push Buttons */
QPushButton {
    background-color: #334155;
    color: #F8FAFC;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #475569;
    border-color: #64748B;
}

QPushButton:pressed {
    background-color: #1E293B;
}

QPushButton:disabled {
    background-color: #1E293B;
    color: #64748B;
    border-color: #334155;
}

/* Primary Action Button (Start) */
QPushButton.btn-primary {
    background-color: #059669;
    border: 1px solid #10B981;
    color: #FFFFFF;
}

QPushButton.btn-primary:hover {
    background-color: #10B981;
    border-color: #34D399;
}

QPushButton.btn-primary:pressed {
    background-color: #047857;
}

/* Danger Action Button (Stop) */
QPushButton.btn-danger {
    background-color: #BE123C;
    border: 1px solid #F43F5E;
    color: #FFFFFF;
}

QPushButton.btn-danger:hover {
    background-color: #E11D48;
}

QPushButton.btn-danger:pressed {
    background-color: #9F1239;
}

/* Inputs & ComboBoxes */
QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit {
    background-color: #0F172A;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 12px;
    color: #F8FAFC;
    selection-background-color: #059669;
}

QComboBox:hover, QSpinBox:hover, QLineEdit:hover {
    border-color: #10B981;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left-width: 0px;
}

QComboBox QAbstractItemView {
    background-color: #1E293B;
    border: 1px solid #334155;
    selection-background-color: #059669;
    color: #F8FAFC;
}

/* Checkboxes */
QCheckBox {
    spacing: 8px;
    color: #E2E8F0;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #475569;
    background-color: #0F172A;
}

QCheckBox::indicator:checked {
    background-color: #10B981;
    border-color: #34D399;
}

/* Sliders */
QSlider::groove:horizontal {
    height: 6px;
    background: #334155;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #10B981;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #F8FAFC;
    border: 1px solid #10B981;
    width: 16px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background: #34D399;
}

/* List Widgets */
QListWidget {
    background-color: #0F172A;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 4px;
}

QListWidget::item {
    padding: 6px;
    border-radius: 4px;
}

QListWidget::item:alternate {
    background-color: #1E293B;
}

/* Scrollbars */
QScrollBar:vertical {
    background: #0F172A;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #334155;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #475569;
}
"""
