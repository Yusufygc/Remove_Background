"""Background removal worker thread using Observer pattern."""

from io import BytesIO
from PyQt5.QtCore import QThread, pyqtSignal
from PIL import Image

from models.image_processor import ImageProcessor


class BackgroundRemoverWorker(QThread):
    """
    Worker thread for background removal processing.
    Uses Observer pattern via pyqtSignal for communication with UI.
    Implements Single Responsibility Principle - only handles background removal.
    """
    
    finished = pyqtSignal(BytesIO)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(self, input_path: str, model_session: any, processor: ImageProcessor = None):
        """
        Initialize worker.
        
        Args:
            input_path: Path to input image
            model_session: rembg model session
            processor: Image processor instance (default: creates new one)
        """
        super().__init__()
        self._input_path = input_path
        self._model_session = model_session
        self._processor = processor or ImageProcessor()
    
    def run(self):
        """Execute background removal in background thread."""
        try:
            # Load image
            input_image = Image.open(self._input_path)
            
            # Process image
            output_image = self._processor.process(
                input_image,
                self._model_session,
                progress_callback=self.progress.emit
            )
            
            # Convert to bytes
            output_bytes = BytesIO()
            output_image.save(
                output_bytes,
                format="PNG",
                optimize=False,
                compress_level=1
            )
            output_bytes.seek(0)
            
            # Emit success signal
            self.finished.emit(output_bytes)
            
        except Exception as e:
            # Emit error signal
            self.error.emit(str(e))
