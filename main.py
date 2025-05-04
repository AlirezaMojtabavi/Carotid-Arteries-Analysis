from GUI.MainWindow import VTKPipelineGUI
from PyQt5.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VTKPipelineGUI()
    window.show()
    sys.exit(app.exec_())