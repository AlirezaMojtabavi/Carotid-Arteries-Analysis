from PyQt5.QtWidgets import QWidget, QPushButton, QGroupBox, QHBoxLayout, QLineEdit, QFormLayout, QDialog, QVBoxLayout
from PyQt5.QtCore import pyqtSignal
from GUI.Styles import button_style, group_style


class RegistrationWidget(QWidget):
    confirm_clicked_signal = pyqtSignal()
    update_parameters_signal = pyqtSignal(float, float)

    def __init__(self):
        super().__init__()
        self.confirm_registration = QPushButton("Confirm")
        self.try_again_registration = QPushButton("Modify")

        self.initUI()

    def initUI(self):
        self.confirm_registration.setStyleSheet(button_style)
        self.confirm_registration.setFixedHeight(26)
        self.confirm_registration.setFixedWidth(100)
        self.confirm_registration.setEnabled(False)
        self.confirm_registration.clicked.connect(self.confirm_registration_pushed)

        self.try_again_registration = QPushButton("Customize")
        self.try_again_registration.setStyleSheet(button_style)
        self.try_again_registration.setStyleSheet(button_style)
        self.try_again_registration.setFixedHeight(26)
        self.try_again_registration.setFixedWidth(100)
        self.try_again_registration.setEnabled(False)
        self.try_again_registration.clicked.connect(self.try_again_registration_pushed)

        registration_group = QGroupBox("Registration")
        registration_group.setStyleSheet(group_style)
        registration_group.setFixedSize(250, 90)
        registration_layout = QHBoxLayout(registration_group)
        registration_layout.addWidget(self.confirm_registration)
        registration_layout.addWidget(self.try_again_registration)
        registration_layout.setContentsMargins(10, 18, 10, 10)
        registration_layout.setSpacing(20)

        main_layout = QVBoxLayout()
        main_layout.addWidget(registration_group)
        self.setLayout(main_layout)

    def confirm_registration_pushed(self):
        self.confirm_clicked_signal.emit()
        self.confirm_registration.setEnabled(False)
        self.try_again_registration.setEnabled(False)

    def try_again_registration_pushed(self):
        pass
