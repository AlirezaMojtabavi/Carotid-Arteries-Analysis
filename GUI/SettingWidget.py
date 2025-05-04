from PyQt5.QtWidgets import QFileDialog, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, \
    QGroupBox, QMenu, QAction
from PyQt5.QtCore import QPoint, pyqtSignal, Qt
from FilesConfiguraiton import FilesConfiguration
from GUI.Styles import button_style, group_style, context_menu_style


class SettingWidget(QWidget):
    config_selected = pyqtSignal(str, int)
    start_clicked_signal = pyqtSignal()
    stop_clicked_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.load_button = QPushButton("Load Data")
        self.side_chooser_bttn = QPushButton("Choose Side", self)
        self.start_bttn = QPushButton("Start", self)
        self.stop_bttn = QPushButton("Stop", self)
        self.case_code = None
        self.side_chooser = None
        self.context_menu = None
        self.initUI()

    def initUI(self):
        self.load_button.clicked.connect(self.load_data)
        self.load_button.setStyleSheet(button_style)
        self.load_button.setFixedHeight(26)
        self.load_button.setFixedWidth(90)
        self.side_chooser_bttn.setStyleSheet(button_style)
        self.side_chooser_bttn.setFixedHeight(26)
        self.side_chooser_bttn.setFixedWidth(90)
        self.side_chooser_bttn.clicked.connect(self.show_side_choices)
        self.start_bttn.clicked.connect(self.start_clicked)
        self.stop_bttn.clicked.connect(self.stop)
        self.side_chooser_bttn.setEnabled(False)
        self.start_bttn.setEnabled(False)
        self.stop_bttn.setEnabled(True)

        self.start_bttn.setText("▶ Start")
        self.start_bttn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 10px;
                padding: 3px 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #43a047;
            }
            QPushButton:disabled {
                background-color: #a5d6a7;
                color: #eeeeee;
            }
        """)
        self.start_bttn.setFixedHeight(30)
        self.start_bttn.setFixedWidth(75)
        self.stop_bttn.setText("Stop")
        self.stop_bttn.setStyleSheet("""
            QPushButton {
                background-color: #e53935;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 20px;  /* Makes it circular */
                padding: 3px 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:disabled {
                background-color: #ef9a9a;
                color: #eeeeee;
            }
        """)
        start_layout = QHBoxLayout()
        start_layout.addWidget(self.start_bttn, alignment=Qt.AlignHCenter)

        self.stop_bttn.setFixedHeight(30)
        self.stop_bttn.setFixedWidth(45)
        stop_layout = QHBoxLayout()
        stop_layout.addWidget(self.stop_bttn, alignment=Qt.AlignHCenter)

        setting_group = QGroupBox("Configuration")
        setting_group.setStyleSheet(group_style)
        # First row: Load + Choose Side
        left_layout = QVBoxLayout()

        left_layout.addWidget(self.load_button)
        left_layout.addWidget(self.side_chooser_bttn)

        # Second row: Start + Stop
        right_layout = QVBoxLayout()
        right_layout.addLayout(start_layout)
        right_layout.addLayout(stop_layout)

        # Wrap both rows into the group
        group_layout = QHBoxLayout()
        group_layout.addLayout(left_layout)
        group_layout.addLayout(right_layout)
        setting_group.setFixedSize(210, 120)
        setting_group.setLayout(group_layout)
        group_layout.setContentsMargins(10, 18, 10, 10)
        group_layout.setSpacing(2)
        left_layout.setSpacing(10)
        right_layout.setSpacing(10)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(setting_group)
        self.setLayout(main_layout)

    def load_data(self):
        initial_dir = FilesConfiguration.get_initial_dir()  # Change this to your preferred starting directory
        folder_path = QFileDialog.getExistingDirectory(self, "Select Data Folder", initial_dir)
        if folder_path:  # If user selected a folder
            parts = folder_path.split('/')
            self.case_code = parts[-1]
            # print(f"Selected Folder: {self.selected_folder}")

        self.side_chooser_bttn.setEnabled(True)

    def show_side_choices(self):
        self.context_menu = QMenu(self)
        left_action = QAction("Left Side", self)
        left_action.triggered.connect(self.choose_side)
        right_action = QAction("Right Side", self)
        right_action.triggered.connect(self.choose_side)
        both_action = QAction("Both Side", self)
        both_action.triggered.connect(self.choose_side)

        self.context_menu.addAction(left_action)
        self.context_menu.addAction(right_action)
        self.context_menu.addAction(both_action)

        self.context_menu.popup(
            self.mapToGlobal(QPoint(self.side_chooser_bttn.x(),
                                    self.side_chooser_bttn.y() + self.side_chooser_bttn.height() + 20)))
        self.context_menu.setStyleSheet(context_menu_style)

    def choose_side(self):
        action = self.sender()
        side_chooser = action.text()
        if side_chooser == "Left Side":
            self.side_chooser = 0
            print("Only Left Side")
        elif side_chooser == "Right Side":
            self.side_chooser = 1
            print("Only Right Side")
        else:
            self.side_chooser = 2
            print("Both Side")

        self.load_button.setEnabled(False)
        self.side_chooser_bttn.setEnabled(False)
        self.start_bttn.setEnabled(True)
        self.config_selected.emit(self.case_code, self.side_chooser)

    def start_clicked(self):
        self.start_bttn.setEnabled(False)
        self.start_clicked_signal.emit()

    def stop(self):
        print("Stopping all actions...")
        self.load_button.setEnabled(True)
        self.side_chooser_bttn.setEnabled(False)
        self.start_bttn.setEnabled(False)
        self.stop_clicked_signal.emit()

    def reset_widget(self):
        self.case_code = None
        self.side_chooser = None
        self.context_menu = None
