"""Main entry point for Background Remover application (PySide6 + QML)."""

import os
import sys

# onnxruntime (rembg dependency) must be imported before any Qt module: on
# Windows, Qt's DLL search path changes can break onnxruntime's native DLL
# loading if Qt loads first (see docs/wiki/code-review-2026-09-24.md, bulgu 8).
import onnxruntime  # noqa: F401

from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl
from PySide6.QtQuickControls2 import QQuickStyle

from backend.app_backend import Backend


def resource_path(*parts: str) -> str:
    """
    Resolve a path to a bundled resource (qml/, icons/), working both when
    run from source and when frozen into an .exe (PyInstaller extracts
    bundled data files to sys._MEIPASS at runtime).
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, *parts)


def main():
    """Application entry point."""
    try:
        # "Basic" style supports Control customization (background/contentItem
        # overrides used in qml/ControlPanel.qml); the default native style doesn't.
        QQuickStyle.setStyle("Basic")

        app = QGuiApplication(sys.argv)
        app.setWindowIcon(QIcon(resource_path("icons", "app_icon.ico")))

        backend = Backend()
        engine = QQmlApplicationEngine()
        engine.rootContext().setContextProperty("backend", backend)

        qml_path = resource_path("qml", "Main.qml")
        engine.load(QUrl.fromLocalFile(qml_path))

        if not engine.rootObjects():
            sys.exit(-1)

        app.aboutToQuit.connect(backend.cleanup)

        exit_code = app.exec()

        # Destroy the QML engine (window, components, property bindings)
        # before backend is garbage-collected. Otherwise Python may free
        # `backend` first, and QML's own teardown - still re-evaluating
        # bindings against the now-dead C++ object - prints a "Cannot read
        # property of null" TypeError per binding after the window closes.
        del engine
        del backend

        sys.exit(exit_code)

    except Exception as e:
        print(f"Application startup error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
