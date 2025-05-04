
button_style = """
            QPushButton {
                background-color: #424242;
                color: white;
                font-weight: bold;
                border: 1px solid #616161;
                border-radius: 6px;
                padding: 3px 6px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
            QPushButton:disabled {
                background-color: #757575;
                color: #bdbdbd;
            }
        """

group_style = """
                QGroupBox {
                    color: #ffffff;
                    font-size: 9.5pt;
                    font-weight: bold;
                    border: 1px solid #616161;
                    border-radius: 6px;
                    margin-top: 10px;
                    background-color: #2e2e2e;
                }
                QGroupBox:title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    top: -5px;
                    padding: 0 6px;
                }
             """
main_group_style = """
    QGroupBox {
        color: #bbbbbb;
        font-size: 11.5pt;
        font-weight: bold;
        border-top: 3px solid #226622;
        border-right: 3px solid #226622;
        border-bottom: none;
        border-left: 3px solid #226622;
        border-radius: 3px;
        margin-top: 10px;
        margin-bottom: 1px;
        background-color: #2e2e2e;
    }
    QGroupBox:title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        top: -5px;
        padding: 0 6px;
    }
"""

context_menu_style = ("""
        QMenu {
            background-color: #2e2e2e;
            border: 2px solid #555555;
            color: white;
            padding: 10px;
            font-weight: bold;
            font-size: 16px;
        }
        QMenu::item {
            padding: 8px 16px;
            background-color: transparent;
        }
        QMenu::item:selected {
            background-color: #2196F3;  /* or any highlight color */
            color: white;
        }
        """)

label_style = """
    QLabel {
        color: #ffffff;
        background-color: #3a3a3a;
        padding: 4px 8px;
        font-weight: bold;
        font-size: 14px;
        border-radius: 4px;
    }
    """
sheet_style = """
            QWidget {
                font-family: 'Segoe UI';
                font-size: 10pt;
            }

            QMainWindow {
                background-color: #2e2e2e;
            }

            QFrame#centerlineViewer {
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 5px;
            }

            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
                padding: 6px;
                border-radius: 4px;
            }

            QMenuBar {
                background-color: #e0e0e0;
            }

            QMenuBar::item:selected {
                background: #dcdcdc;
            }

            QToolBar {
                background-color: #fafafa;
                border: 1px solid #ddd;
            }

            QToolButton {
                padding: 4px 8px;
            }

            QToolButton:hover {
                background-color: #e6e6e6;
            }
        """

brindled_text_label_style = """
    QLabel {
        font-size: 54px;
        font-weight: bold;
        color: #771111; /* Dark green */
    }
"""