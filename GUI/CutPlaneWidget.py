from PyQt5.QtWidgets import QFileDialog, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QPlainTextEdit, \
    QGroupBox, QMenu, QAction, QDialog
from PyQt5.QtCore import QPoint, pyqtSignal
from functools import partial
from GUI.Styles import button_style, group_style, context_menu_style


class CutPlaneWidget(QWidget):
    confirm_signal = pyqtSignal()
    toggled_name_signal = pyqtSignal(str, bool, str)

    def __init__(self):
        super().__init__()
        self.confirm_cut_plane = QPushButton("Confirm")
        self.customize_cut_plane = QPushButton("Customize")
        self.cutplanes_menu = None
        self.side_chooser = None
        self.actor_names = None

        self.initUI()

    def initUI(self):
        self.confirm_cut_plane.setStyleSheet(button_style)
        self.confirm_cut_plane.setFixedHeight(26)
        self.confirm_cut_plane.setFixedWidth(85)
        self.confirm_cut_plane.setEnabled(False)
        self.confirm_cut_plane.clicked.connect(self.confirm_cut_plane_pushed)

        self.customize_cut_plane.setStyleSheet(button_style)
        self.customize_cut_plane.setFixedHeight(26)
        self.customize_cut_plane.setFixedWidth(85)
        self.customize_cut_plane.setEnabled(False)
        self.customize_cut_plane.clicked.connect(self.customize_cut_plane_pushed)

        cut_plane_group = QGroupBox("Cut Planes")
        cut_plane_group.setStyleSheet(group_style)
        cut_plane_group.setFixedSize(210, 80)
        cut_plane_layout = QHBoxLayout(cut_plane_group)
        cut_plane_layout.addWidget(self.confirm_cut_plane)
        cut_plane_layout.addWidget(self.customize_cut_plane)
        cut_plane_layout.setContentsMargins(10, 18, 10, 10)
        cut_plane_layout.setSpacing(3)

        main_layout = QVBoxLayout()
        main_layout.addWidget(cut_plane_group)
        self.setLayout(main_layout)

    def enable_buttons(self):
        self.confirm_cut_plane.setEnabled(True)
        self.customize_cut_plane.setEnabled(True)

    def disable_buttons(self):
        self.confirm_cut_plane.setEnabled(False)
        self.customize_cut_plane.setEnabled(False)

    def set_actor_names(self, actor_names):
        self.actor_names = actor_names

    def set_side(self, side):
        self.side_chooser = side

    def confirm_cut_plane_pushed(self):
        self.confirm_signal.emit()
        self.confirm_cut_plane.setEnabled(False)
        self.customize_cut_plane.setEnabled(False)

    def customize_cut_plane_pushed(self):
        if self.cutplanes_menu is None:
            self.cutplanes_menu = QMenu(self)
            self.cutplanes_menu.setToolTipsVisible(True)
            self.cutplanes_menu.setStyleSheet(context_menu_style)
            if self.side_chooser == 2:
                left_action = QAction("Left", self)
                left_child_menu = QMenu("Left", self)
                left_child_menu.setStyleSheet(context_menu_style)
                right_action = QAction("Right", self)
                right_child_menu = QMenu("Right", self)
                right_child_menu.setStyleSheet(context_menu_style)

                for k in self.actor_names:
                    if k in {"Artery", "Centerline", "cca", "ica", "eca"}:
                        continue
                    child_action = QAction(k, self.cutplanes_menu)
                    child_action.setCheckable(True)
                    child_action.setChecked(True)  # Default checked

                    child_action.triggered.connect(partial(self.on_cut_plane_toggled, k, child_action, "left"))
                    left_child_menu.addAction(child_action)
                left_action.setMenu(left_child_menu)
                self.cutplanes_menu.addAction(left_action)

                for k in self.actor_names:
                    if k in {"Artery", "Centerline", "cca", "ica", "eca"}:
                        continue
                    right_child_action = QAction(k, self.cutplanes_menu)
                    right_child_action.setCheckable(True)
                    right_child_action.setChecked(True)  # Default checked

                    right_child_action.triggered.connect(
                        partial(self.on_cut_plane_toggled, k, right_child_action, "right"))
                    right_child_menu.addAction(right_child_action)
                right_action.setMenu(right_child_menu)
                self.cutplanes_menu.addAction(right_action)

            else:
                for k in self.actor_names:
                    if k in {"Artery", "Centerline", "cca", "ica", "eca"}:
                        continue
                    action = QAction(k, self.cutplanes_menu)
                    action.setCheckable(True)
                    action.setChecked(True)  # Default checked
                    action.triggered.connect(partial(self.on_cut_plane_toggled, k, action))
                    self.cutplanes_menu.addAction(action)

        self.cutplanes_menu.popup(
            self.customize_cut_plane.mapToGlobal(self.customize_cut_plane.rect().bottomLeft()))

    def on_cut_plane_toggled(self, name, action, side=None):
        new_state = action.isChecked()  # Get current state after toggle
        if side in ("left", "right"):
            self.toggled_name_signal.emit(name, new_state, side)
        else:
            self.toggled_name_signal.emit(name, new_state, "")

    def reset_widget(self):
        self.disable_buttons()
        self.cutplanes_menu = None
        self.side_chooser = None
        self.actor_names = None
