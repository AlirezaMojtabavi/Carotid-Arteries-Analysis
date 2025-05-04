from PyQt5.QtWidgets import QWidget, QPushButton, QGroupBox, QHBoxLayout, QMenu, QAction, QVBoxLayout
from PyQt5.QtCore import pyqtSignal
from GUI.Styles import button_style, group_style, context_menu_style


class CenterlineWidget(QWidget):
    confirm_clicked_signal = pyqtSignal()
    left_try_again_signal = pyqtSignal(str)
    right_try_again_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.side = None
        self.centerline_menu = None
        self.confirm_centerline = QPushButton("Confirm")
        self.try_again_centerline = QPushButton("Try Again")
        self.initUI()

    def set_side(self, side):
        self.side = side

    def initUI(self):
        self.confirm_centerline.setStyleSheet(button_style)
        self.confirm_centerline.setFixedHeight(26)
        self.confirm_centerline.setFixedWidth(85)
        self.confirm_centerline.setEnabled(False)
        self.confirm_centerline.clicked.connect(self.confirm_centerline_pushed)
        self.try_again_centerline.setStyleSheet(button_style)
        self.try_again_centerline.setFixedHeight(26)
        self.try_again_centerline.setFixedWidth(85)
        self.try_again_centerline.setEnabled(False)
        self.try_again_centerline.clicked.connect(self.try_again_centerline_pushed)

        centerline_group = QGroupBox("Centerline")
        centerline_group.setStyleSheet(group_style)
        centerline_group.setFixedSize(210, 80)

        centerline_layout = QHBoxLayout(centerline_group)
        centerline_layout.addWidget(self.confirm_centerline)
        centerline_layout.addWidget(self.try_again_centerline)
        # centerline_layout.setContentsMargins(6, 8, 6, 6)
        centerline_layout.setSpacing(2)

        main_layout = QVBoxLayout()
        main_layout.addWidget(centerline_group)
        self.setLayout(main_layout)

    def confirm_centerline_pushed(self):
        self.confirm_clicked_signal.emit()
        self.confirm_centerline.setEnabled(False)
        self.try_again_centerline.setEnabled(False)

    def centerline_side_action(self):
        action = self.sender()
        side_chooser = action.text()
        if side_chooser == "Left Side":
            self.left_try_again_signal.emit("left")

        elif side_chooser == "Right Side":
            self.right_try_again_signal.emit("right")

    def try_again_centerline_pushed(self):
        if self.side == 2:
            self.centerline_menu = QMenu(self)
            self.centerline_menu.setStyleSheet(context_menu_style)
            left_action_centerline = QAction("Left Side", self)
            left_action_centerline.triggered.connect(self.centerline_side_action)
            right_action_centerline = QAction("Right Side", self)
            right_action_centerline.triggered.connect(self.centerline_side_action)
            self.centerline_menu.addAction(left_action_centerline)
            self.centerline_menu.addAction(right_action_centerline)

            self.centerline_menu.popup(
                self.try_again_centerline.mapToGlobal(self.try_again_centerline.rect().bottomLeft()))

        elif self.side == 0:
            self.left_try_again_signal.emit("left")
        elif self.side == 1:
            self.right_try_again_signal.emit("right")

    def reset_widget(self):
        self.side = None
        self.centerline_menu = None
        self.confirm_centerline.setEnabled(False)
        self.try_again_centerline.setEnabled(False)
