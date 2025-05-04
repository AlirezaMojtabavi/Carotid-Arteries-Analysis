from PyQt5.QtWidgets import QWidget, QPushButton, QGroupBox, QHBoxLayout, QLabel, QFormLayout, QDialog, QVBoxLayout
from PyQt5.QtCore import pyqtSignal, Qt
from GUI.Styles import button_style, group_style
from GUI.LedIndicator import LedIndicator


class VolumeProcessingWidget(QWidget):
    confirm_registration_signal = pyqtSignal()
    update_parameters_signal = pyqtSignal(float, float)

    def __init__(self):
        super().__init__()
        self.confirm_registration = QPushButton("Confirm")
        self.modify_registration = QPushButton("Modify")
        self.calculating_led = LedIndicator(Qt.gray)
        self.done_led = LedIndicator(Qt.gray)

        self.initUI()

    def initUI(self):
        self.confirm_registration.setStyleSheet(button_style)
        self.confirm_registration.setFixedHeight(26)
        self.confirm_registration.setFixedWidth(85)
        self.confirm_registration.setEnabled(False)
        self.confirm_registration.clicked.connect(self.confirm_registration_pushed)

        self.modify_registration.setStyleSheet(button_style)
        self.modify_registration.setFixedHeight(26)
        self.modify_registration.setFixedWidth(85)
        self.modify_registration.setEnabled(False)
        self.modify_registration.clicked.connect(self.modify_registration_pushed)

        registration_layout = QHBoxLayout()
        registration_layout.addWidget(self.confirm_registration)
        registration_layout.addWidget(self.modify_registration)
        registration_layout.setSpacing(9)

        calculation_layout = QHBoxLayout()
        calculation_label = QLabel("Calculating Flow ...")
        calculation_label.setStyleSheet("color: white; font-size: 12px;")
        calculation_layout.addWidget(self.calculating_led)
        calculation_layout.addWidget(calculation_label)
        calculation_layout.setAlignment(Qt.AlignLeft)
        calculation_layout.setSpacing(6)

        done_layout = QHBoxLayout()
        done_label = QLabel("Calculation Done")
        done_label.setStyleSheet("color: white; font-size: 12px;")
        done_layout.addWidget(self.done_led)
        done_layout.addWidget(done_label)
        done_layout.setAlignment(Qt.AlignLeft)
        done_layout.setSpacing(6)

        led_layout = QVBoxLayout()
        led_layout.addLayout(calculation_layout)
        led_layout.addLayout(done_layout)
        led_layout.setSpacing(4)

        boundary_conditions_group = QGroupBox("Volume Processing")
        boundary_conditions_group.setFixedSize(210, 120)
        boundary_conditions_group.setStyleSheet(group_style)

        group_layout = QVBoxLayout()
        group_layout.addLayout(registration_layout)
        group_layout.addSpacing(4)
        group_layout.addLayout(led_layout)
        group_layout.setContentsMargins(5, 5, 5, 5)
        boundary_conditions_group.setLayout(group_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(boundary_conditions_group)
        self.setLayout(main_layout)

    def enable_buttons(self):
        self.confirm_registration.setEnabled(True)
        self.modify_registration.setEnabled(True)

    def disable_buttons(self):
        self.confirm_registration.setEnabled(False)
        self.modify_registration.setEnabled(False)

    def confirm_registration_pushed(self):
        self.confirm_registration_signal.emit()
        self.confirm_registration.setEnabled(False)
        self.modify_registration.setEnabled(False)
        self.calculating_led.activate()

    def modify_registration_pushed(self):
        pass

    def reset_widget(self):
        self.disable_buttons()
        self.calculating_led.deactivate()
        self.calculating_led.deactivate()
