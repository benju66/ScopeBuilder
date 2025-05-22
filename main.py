import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout
from ui.main_window import MainWindow

def main():
    # Create the Qt Application
    app = QApplication(sys.argv)

    # Create and show the main window
    window = MainWindow()
    window.setWindowTitle("ScopeBuilder")
    window.resize(1200, 800)
    window.show()

    # Run the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
