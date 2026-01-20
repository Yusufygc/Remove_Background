"""Main entry point for Background Remover application."""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui.main_window import BackgroundRemoverApp


def main():
    """Application entry point."""
    try:
        app = QApplication(sys.argv)
        app.setAttribute(Qt.AA_EnableHighDpiScaling)
        
        # Set application font
        font = QFont("Segoe UI", 10)
        app.setFont(font)
        
        # Create and show main window
        window = BackgroundRemoverApp()
        window.show()
        
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"Application startup error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
