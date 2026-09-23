"""Backend bridge exposing the application's domain layer to QML."""

import os
import tempfile
from io import BytesIO
from typing import Optional

from PySide6.QtCore import QObject, Signal, Slot, Property, QUrl

from models.model_manager import ModelManager
from models.image_processor import ImageProcessor
from workers.background_remover_worker import BackgroundRemoverWorker
from utils.constants import (
    COLORS, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, WINDOW_DEFAULT_WIDTH,
    WINDOW_DEFAULT_HEIGHT, AVAILABLE_MODELS,
    CONTROL_PANEL_MIN_WIDTH, CONTROL_PANEL_MAX_WIDTH,
)
from utils import icons as ic
from utils import strings as ui_text


def _to_file_url(path: str) -> str:
    """Convert a local filesystem path to a file:// URL QML can load."""
    if not path:
        return ""
    return QUrl.fromLocalFile(path).toString()


def _from_file_url(url: str) -> str:
    """Convert a file:// URL (from QML dialogs/drops) to a local path."""
    if url.startswith("file:"):
        return QUrl(url).toLocalFile()
    return url


class Backend(QObject):
    """
    Single Python <-> QML bridge.
    Wraps ModelManager (Factory+Repository) and ImageProcessor (Strategy)
    unchanged; exposes their results, plus the app's theme/icon/string
    registries (utils/constants.py, utils/icons.py, utils/strings.py), as
    Qt properties/signals — QML never hardcodes a color, icon path or label.
    """

    statusChanged = Signal()
    inputImageChanged = Signal()
    outputImageChanged = Signal()
    processingStateChanged = Signal()
    currentModelChanged = Signal()
    errorOccurred = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model_manager = ModelManager()
        self._image_processor = ImageProcessor()
        self._worker: Optional[BackgroundRemoverWorker] = None

        self._model_manager.model_loaded.connect(self._on_model_loaded)
        self._model_manager.all_models_loaded.connect(self._on_all_models_loaded)
        self._model_manager.error_occurred.connect(self._on_model_error)

        self._status_text = ui_text.STATUS_INITIALIZING
        self._status_type = "warning"
        self._input_image_path: Optional[str] = None
        self._output_image_path: Optional[str] = None
        self._output_bytes: Optional[BytesIO] = None
        self._is_processing = False
        self._current_model = AVAILABLE_MODELS[0]

    # ---- theme properties: single source of truth is utils/constants.py ----

    colorPrimary = Property(str, lambda self: COLORS['primary'], constant=True)
    colorSuccess = Property(str, lambda self: COLORS['success'], constant=True)
    colorWarning = Property(str, lambda self: COLORS['warning'], constant=True)
    colorError = Property(str, lambda self: COLORS['error'], constant=True)
    colorBackground = Property(str, lambda self: COLORS['background'], constant=True)
    colorSurface = Property(str, lambda self: COLORS['surface'], constant=True)
    colorSurfaceLight = Property(str, lambda self: COLORS['surface_light'], constant=True)
    colorSurfaceDark = Property(str, lambda self: COLORS['surface_dark'], constant=True)
    colorText = Property(str, lambda self: COLORS['text'], constant=True)
    colorTextSecondary = Property(str, lambda self: COLORS['text_secondary'], constant=True)
    colorBorder = Property(str, lambda self: COLORS['border'], constant=True)
    colorAccent = Property(str, lambda self: COLORS['accent'], constant=True)
    colorTipsBackground = Property(str, lambda self: COLORS['tips_background'], constant=True)
    colorTipsBorder = Property(str, lambda self: COLORS['tips_border'], constant=True)
    colorButtonShadow = Property(str, lambda self: COLORS['button_shadow'], constant=True)
    colorPanelShadow = Property(str, lambda self: COLORS['panel_shadow'], constant=True)

    def _get_status_color(self) -> str:
        return {
            "success": COLORS['success'],
            "warning": COLORS['warning'],
            "error": COLORS['error'],
        }.get(self._status_type, COLORS['primary'])

    statusColor = Property(str, _get_status_color, notify=statusChanged)

    # ---- icon properties: single source of truth is utils/icons.py --------

    iconApp = Property(str, lambda self: ic.ICON_APP, constant=True)
    iconUpload = Property(str, lambda self: ic.ICON_UPLOAD, constant=True)
    iconRemoveBg = Property(str, lambda self: ic.ICON_REMOVE_BG, constant=True)
    iconSave = Property(str, lambda self: ic.ICON_SAVE, constant=True)
    iconTip = Property(str, lambda self: ic.ICON_TIP, constant=True)
    iconOriginal = Property(str, lambda self: ic.ICON_ORIGINAL, constant=True)
    iconResult = Property(str, lambda self: ic.ICON_RESULT, constant=True)

    # ---- string properties: single source of truth is utils/strings.py ----

    windowTitle = Property(str, lambda self: ui_text.WINDOW_TITLE, constant=True)
    stringAppTitle = Property(str, lambda self: ui_text.APP_TITLE, constant=True)
    stringAppSubtitle = Property(str, lambda self: ui_text.APP_SUBTITLE, constant=True)
    stringModelLabel = Property(str, lambda self: ui_text.MODEL_LABEL, constant=True)
    stringButtonUpload = Property(str, lambda self: ui_text.BUTTON_UPLOAD, constant=True)
    stringButtonRemoveBg = Property(str, lambda self: ui_text.BUTTON_REMOVE_BG, constant=True)
    stringButtonSave = Property(str, lambda self: ui_text.BUTTON_SAVE, constant=True)
    stringTipsTitle = Property(str, lambda self: ui_text.TIPS_TITLE, constant=True)
    stringTipsText = Property(str, lambda self: ui_text.TIPS_TEXT, constant=True)
    stringHeaderOriginal = Property(str, lambda self: ui_text.HEADER_ORIGINAL, constant=True)
    stringHeaderResult = Property(str, lambda self: ui_text.HEADER_RESULT, constant=True)
    stringPlaceholderInput = Property(str, lambda self: ui_text.PLACEHOLDER_INPUT, constant=True)
    stringPlaceholderOutput = Property(str, lambda self: ui_text.PLACEHOLDER_OUTPUT, constant=True)
    dialogOpenTitle = Property(str, lambda self: ui_text.DIALOG_OPEN_TITLE, constant=True)
    dialogSaveTitle = Property(str, lambda self: ui_text.DIALOG_SAVE_TITLE, constant=True)
    dialogErrorTitle = Property(str, lambda self: ui_text.DIALOG_ERROR_TITLE, constant=True)
    imageFileFilter = Property(str, lambda self: ui_text.IMAGE_FILE_FILTER, constant=True)
    pngFileFilter = Property(str, lambda self: ui_text.PNG_FILE_FILTER, constant=True)

    # ---- layout/config properties -------------------------------------

    availableModels = Property(list, lambda self: list(AVAILABLE_MODELS), constant=True)
    windowDefaultWidth = Property(int, lambda self: WINDOW_DEFAULT_WIDTH, constant=True)
    windowDefaultHeight = Property(int, lambda self: WINDOW_DEFAULT_HEIGHT, constant=True)
    windowMinWidth = Property(int, lambda self: WINDOW_MIN_WIDTH, constant=True)
    windowMinHeight = Property(int, lambda self: WINDOW_MIN_HEIGHT, constant=True)
    controlPanelMinWidth = Property(int, lambda self: CONTROL_PANEL_MIN_WIDTH, constant=True)
    controlPanelMaxWidth = Property(int, lambda self: CONTROL_PANEL_MAX_WIDTH, constant=True)

    # ---- dynamic properties ------------------------------------------------

    statusText = Property(str, lambda self: self._status_text, notify=statusChanged)
    statusType = Property(str, lambda self: self._status_type, notify=statusChanged)

    inputImagePath = Property(
        str,
        lambda self: _to_file_url(self._input_image_path) if self._input_image_path else "",
        notify=inputImageChanged,
    )
    outputImagePath = Property(
        str,
        lambda self: _to_file_url(self._output_image_path) if self._output_image_path else "",
        notify=outputImageChanged,
    )

    isProcessing = Property(bool, lambda self: self._is_processing, notify=processingStateChanged)
    canProcess = Property(
        bool,
        lambda self: bool(self._input_image_path) and not self._is_processing,
        notify=processingStateChanged,
    )
    canSave = Property(bool, lambda self: self._output_bytes is not None, notify=outputImageChanged)
    currentModel = Property(str, lambda self: self._current_model, notify=currentModelChanged)

    def _get_suggested_save_name(self) -> str:
        if not self._input_image_path:
            return "output.png"
        base_name = os.path.basename(self._input_image_path).split('.')[0]
        model_name = self._current_model.replace('-', '_')
        return f"{base_name}_no_bg_{model_name}.png"

    suggestedSaveName = Property(str, _get_suggested_save_name, notify=inputImageChanged)

    # ---- slots (callable from QML) -----------------------------------------

    @Slot()
    def loadModels(self):
        """Load all AI models (mirrors previous _load_models flow)."""
        self._set_status(ui_text.STATUS_INITIALIZING, "warning")
        if not self._model_manager.load_all_models():
            self._set_status(ui_text.STATUS_MODELS_FAILED, "error")
            self.errorOccurred.emit(ui_text.ERROR_MODELS_FAILED)

    @Slot(str)
    def setCurrentModel(self, name: str):
        if name and name != self._current_model:
            self._current_model = name
            self.currentModelChanged.emit()
            self.inputImageChanged.emit()  # refresh suggestedSaveName binding

    @Slot(str)
    def setInputImage(self, path: str):
        """Set input image from a file dialog result or a dropped file URL."""
        local_path = _from_file_url(path)
        if not os.path.isfile(local_path):
            return

        self._input_image_path = local_path
        self._output_bytes = None
        self._clear_output_file()
        self.inputImageChanged.emit()
        self.outputImageChanged.emit()
        self.processingStateChanged.emit()

        self._set_status(os.path.basename(local_path), "primary")

    @Slot()
    def processImage(self):
        if not self._input_image_path:
            self.errorOccurred.emit(ui_text.ERROR_NO_INPUT)
            return
        if not self._model_manager.has_session(self._current_model):
            self.errorOccurred.emit(ui_text.ERROR_NO_MODEL_SESSION)
            return

        session = self._model_manager.get_session(self._current_model)

        self._is_processing = True
        self.processingStateChanged.emit()
        self._set_status(ui_text.STATUS_PROCESSING.format(model=self._current_model), "warning")

        self._worker = BackgroundRemoverWorker(
            self._input_image_path, session, self._image_processor
        )
        self._worker.finished.connect(self._on_processing_finished)
        self._worker.error.connect(self._on_processing_error)
        self._worker.progress.connect(lambda msg: self._set_status(msg, "warning"))
        self._worker.start()

    @Slot(str)
    def saveImage(self, dest_path: str):
        if not self._output_bytes:
            self.errorOccurred.emit(ui_text.ERROR_NO_OUTPUT)
            return

        local_path = _from_file_url(dest_path)
        try:
            with open(local_path, 'wb') as f:
                f.write(self._output_bytes.getvalue())
            self._set_status(
                ui_text.STATUS_SAVED.format(filename=os.path.basename(local_path)), "success"
            )
        except OSError as e:
            self.errorOccurred.emit(ui_text.ERROR_SAVE_FAILED.format(error=e))

    @Slot()
    def cleanup(self):
        """Remove the temp output PNG on app shutdown (connected to aboutToQuit)."""
        self._clear_output_file()

    # ---- internal helpers ---------------------------------------------------

    def _set_status(self, text: str, status_type: str):
        self._status_text = text
        self._status_type = status_type
        self.statusChanged.emit()

    def _clear_output_file(self):
        if self._output_image_path and os.path.isfile(self._output_image_path):
            try:
                os.remove(self._output_image_path)
            except OSError:
                pass
        self._output_image_path = None

    def _on_model_loaded(self, model_name: str):
        self._set_status(ui_text.STATUS_MODEL_LOADED.format(model=model_name), "warning")

    def _on_all_models_loaded(self):
        self._set_status(ui_text.STATUS_READY, "success")

    def _on_model_error(self, error_message: str):
        self._set_status(ui_text.STATUS_MODEL_ERROR, "error")
        self.errorOccurred.emit(error_message)

    def _on_processing_finished(self, output_bytes: BytesIO):
        self._output_bytes = output_bytes
        self._clear_output_file()

        # New filename each time: QML Image caches by URL, so reusing the same
        # path would keep showing the previous result.
        fd, path = tempfile.mkstemp(suffix=".png", prefix="removebg_")
        with os.fdopen(fd, 'wb') as f:
            f.write(output_bytes.getvalue())
        self._output_image_path = path

        self._is_processing = False
        self.outputImageChanged.emit()
        self.processingStateChanged.emit()
        self._set_status(ui_text.STATUS_SUCCESS, "success")

    def _on_processing_error(self, error_message: str):
        self._is_processing = False
        self.processingStateChanged.emit()
        self._set_status(ui_text.STATUS_ERROR, "error")
        self.errorOccurred.emit(ui_text.ERROR_PROCESSING_FAILED.format(error=error_message))
