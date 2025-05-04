from PyQt5.QtWidgets import QWidget, QPushButton, QGroupBox, QHBoxLayout, QLineEdit, QFormLayout, QDialog, QVBoxLayout
from PyQt5.QtCore import pyqtSignal
from GUI.Styles import button_style, group_style


class ClippedSurfaceWidget(QWidget):
    confirm_clicked_signal = pyqtSignal(float)
    update_parameters_signal = pyqtSignal(float, float)

    def __init__(self):
        super().__init__()
        self.sphere_radius_coef = None
        self.variation_rate = None
        self.cutplane_size_coef = None
        self.confirm_clipped = QPushButton("Confirm")
        self.try_again_clipped = QPushButton("Modify")

        self.initUI()

    def initUI(self):
        self.confirm_clipped.setStyleSheet(button_style)
        self.confirm_clipped.setFixedHeight(26)
        self.confirm_clipped.setFixedWidth(85)
        self.confirm_clipped.setEnabled(False)
        self.confirm_clipped.clicked.connect(self.confirm_clipped_pushed)

        self.try_again_clipped = QPushButton("Modify")
        self.try_again_clipped.setEnabled(False)
        self.try_again_clipped.setStyleSheet(button_style)
        self.try_again_clipped.setFixedHeight(26)
        self.try_again_clipped.setFixedWidth(85)
        self.try_again_clipped.clicked.connect(self.try_again_clipped_pushed)

        clipped_group = QGroupBox("Clipped Surface")
        clipped_group.setStyleSheet(group_style)
        clipped_group.setFixedSize(210, 80)
        clipped_layout = QHBoxLayout(clipped_group)
        clipped_layout.addWidget(self.confirm_clipped)
        clipped_layout.addWidget(self.try_again_clipped)
        clipped_layout.setContentsMargins(10, 18, 10, 10)
        clipped_layout.setSpacing(5)

        main_layout = QVBoxLayout()
        main_layout.addWidget(clipped_group)
        self.setLayout(main_layout)

    def set_parameters(self, variation_rate, sphere_radius_coef, cutplane_size_coef):
        self.variation_rate = variation_rate
        self.sphere_radius_coef = sphere_radius_coef
        self.cutplane_size_coef = cutplane_size_coef

    def enable_buttons(self):
        self.confirm_clipped.setEnabled(True)
        self.try_again_clipped.setEnabled(True)

    def confirm_clipped_pushed(self):
        self.confirm_clicked_signal.emit(self.cutplane_size_coef)
        self.confirm_clipped.setEnabled(False)
        self.try_again_clipped.setEnabled(False)

    def try_again_clipped_pushed(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Modify Parameters")
        dialog.setModal(True)  # Block other actions until the dialog is closed
        dialog.setGeometry(95, 540, 300, 140)

        layout = QFormLayout()
        self.variation_rate_input = QLineEdit(str(self.variation_rate))
        self.sphere_radius_coef_input = QLineEdit(str(self.sphere_radius_coef))
        self.cutplane_size_coef_input = QLineEdit(str(self.cutplane_size_coef))

        layout.addRow("Variation Rate:", self.variation_rate_input)
        layout.addRow("Sphere Radius Coefficient", self.sphere_radius_coef_input)
        layout.addRow("Cut Planes Size Coefficient", self.cutplane_size_coef_input)

        btn_layout = QHBoxLayout()
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(lambda: self.apply_clipped_changes(dialog))

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)

        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

        dialog.setLayout(layout)
        dialog.exec_()

    def apply_clipped_changes(self, dialog):
        try:
            self.variation_rate = float(self.variation_rate_input.text())
        except ValueError:
            self.variation_rate_input.clear()
            return
        try:
            self.sphere_radius_coef = float(self.sphere_radius_coef_input.text())
        except ValueError:
            self.sphere_radius_coef_input.clear()
            return
        try:
            self.cutplane_size_coef = float(self.cutplane_size_coef_input.text())
        except ValueError:
            self.cutplane_size_coef_input.clear()
            return

        dialog.accept()
        self.update_parameters_signal.emit(self.variation_rate, self.sphere_radius_coef)

    def disable_buttons(self):
        self.confirm_clipped.setEnabled(False)
        self.try_again_clipped.setEnabled(False)

    def reset_widget(self):
        self.disable_buttons()
        self.sphere_radius_coef = None
        self.variation_rate = None
        self.cutplane_size_coef = None
