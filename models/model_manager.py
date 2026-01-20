"""Model Manager using Factory and Repository patterns for AI model management."""

from typing import Dict, Optional
from rembg import new_session
from PyQt5.QtCore import QObject, pyqtSignal


class ModelManager(QObject):
    """
    Manages AI model sessions using Factory and Repository patterns.
    Implements Single Responsibility Principle - only responsible for model management.
    """
    
    model_loaded = pyqtSignal(str)  # Observer pattern for model loading events
    all_models_loaded = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._sessions: Dict[str, any] = {}
        self._available_models = ["isnet-general-use", "u2net", "u2netp", "silueta"]
    
    def load_all_models(self) -> bool:
        """
        Load all available models.
        Returns True if all models loaded successfully, False otherwise.
        """
        success = True
        for model_name in self._available_models:
            if not self.load_model(model_name):
                success = False
        
        if success:
            self.all_models_loaded.emit()
        
        return success
    
    def load_model(self, model_name: str) -> bool:
        """
        Factory method to create and load a model session.
        
        Args:
            model_name: Name of the model to load
            
        Returns:
            True if model loaded successfully, False otherwise
        """
        if model_name in self._sessions:
            return True  # Model already loaded
        
        try:
            session = new_session(
                model_name,
                alpha_matting=False,
                post_process_mask=False
            )
            self._sessions[model_name] = session
            self.model_loaded.emit(model_name)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Failed to load {model_name}: {str(e)}")
            return False
    
    def get_session(self, model_name: str) -> Optional[any]:
        """
        Repository method to retrieve a model session.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model session if exists, None otherwise
        """
        return self._sessions.get(model_name)
    
    def has_session(self, model_name: str) -> bool:
        """Check if a model session exists."""
        return model_name in self._sessions
    
    def get_available_models(self) -> list:
        """Get list of available model names."""
        return self._available_models.copy()
    
    def get_loaded_models(self) -> list:
        """Get list of loaded model names."""
        return list(self._sessions.keys())
