"""Image processing service using Strategy pattern."""

from PIL import Image
from rembg import remove
from typing import Tuple

from models.image_enhancer import ImageEnhancer, ImageResizer


class ImageProcessor:
    """
    Service class for processing images to remove backgrounds.
    Implements Single Responsibility Principle - only handles image processing.
    """
    
    def __init__(self, enhancer: ImageEnhancer = None):
        """
        Initialize image processor.
        
        Args:
            enhancer: Image enhancer instance (default: creates new one)
        """
        self._enhancer = enhancer or ImageEnhancer()
    
    def process(
        self,
        input_image: Image.Image,
        model_session: any,
        progress_callback=None
    ) -> Image.Image:
        """
        Process image to remove background.
        
        Args:
            input_image: PIL Image to process
            model_session: rembg model session
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Processed PIL Image with transparent background
        """
        if progress_callback:
            progress_callback("Görüntü yükleniyor...")
        
        # Upscale if needed
        processed_image, original_size = ImageResizer.upscale(input_image)
        
        if ImageResizer.should_upscale(input_image.size):
            if progress_callback:
                progress_callback("Görüntü optimize ediliyor...")
        
        # Remove background
        if progress_callback:
            progress_callback("Arka plan siliniyor...")
        output_image = remove(processed_image, session=model_session)
        
        # Downscale if was upscaled
        if ImageResizer.should_upscale(input_image.size):
            if progress_callback:
                progress_callback("Son işlemler...")
            output_image = ImageResizer.downscale(output_image, original_size)
        
        # Enhance edges
        if progress_callback:
            progress_callback("Keskinleştiriliyor...")
        output_image = self._enhancer.enhance(output_image)
        
        return output_image
