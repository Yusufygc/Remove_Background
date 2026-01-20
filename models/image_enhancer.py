"""Image enhancement strategies using Strategy pattern."""

from abc import ABC, abstractmethod
from PIL import Image
import numpy as np
from typing import Tuple

from utils.constants import (
    MIN_DIMENSION_FOR_ENHANCEMENT,
    IMAGE_SCALE_FACTOR,
    ALPHA_THRESHOLD_MIN,
    ALPHA_THRESHOLD_MAX,
    ALPHA_MULTIPLIER,
    DEFAULT_ALPHA_THRESHOLD
)


class ImageEnhancementStrategy(ABC):
    """Abstract base class for image enhancement strategies."""
    
    @abstractmethod
    def enhance(self, image: Image.Image) -> Image.Image:
        """Enhance the image."""
        pass


class EdgeSharpeningStrategy(ImageEnhancementStrategy):
    """Strategy for sharpening edges in RGBA images."""
    
    def enhance(self, image: Image.Image) -> Image.Image:
        """
        Sharpen edges by adjusting alpha channel threshold.
        
        Args:
            image: PIL Image to enhance
            
        Returns:
            Enhanced PIL Image
        """
        if image.mode != 'RGBA':
            return image
        
        img_array = np.array(image)
        alpha = img_array[:, :, 3]
        
        # Calculate dynamic threshold based on average alpha
        non_zero_alpha = alpha[alpha > 0]
        if len(non_zero_alpha) > 0:
            avg_alpha = np.mean(non_zero_alpha)
            threshold = int(max(
                ALPHA_THRESHOLD_MIN,
                min(ALPHA_THRESHOLD_MAX, avg_alpha * ALPHA_MULTIPLIER)
            ))
        else:
            threshold = DEFAULT_ALPHA_THRESHOLD
        
        # Apply threshold to alpha channel
        alpha = np.where(alpha > threshold, 255, 0).astype(np.uint8)
        img_array[:, :, 3] = alpha
        
        return Image.fromarray(img_array)


class ImageEnhancer:
    """
    Context class for image enhancement strategies.
    Uses Strategy pattern to allow different enhancement algorithms.
    """
    
    def __init__(self, strategy: ImageEnhancementStrategy = None):
        """
        Initialize with an enhancement strategy.
        
        Args:
            strategy: Enhancement strategy to use (default: EdgeSharpeningStrategy)
        """
        self._strategy = strategy or EdgeSharpeningStrategy()
    
    def set_strategy(self, strategy: ImageEnhancementStrategy):
        """Set a new enhancement strategy."""
        self._strategy = strategy
    
    def enhance(self, image: Image.Image) -> Image.Image:
        """Enhance image using the current strategy."""
        return self._strategy.enhance(image)


class ImageResizer:
    """Handles image resizing operations."""
    
    @staticmethod
    def should_upscale(size: Tuple[int, int]) -> bool:
        """Check if image should be upscaled for processing."""
        max_dimension = max(size)
        return max_dimension < MIN_DIMENSION_FOR_ENHANCEMENT
    
    @staticmethod
    def calculate_upscale_size(original_size: Tuple[int, int]) -> Tuple[int, int]:
        """Calculate upscaled size maintaining aspect ratio."""
        max_dimension = max(original_size)
        scale_factor = IMAGE_SCALE_FACTOR / max_dimension
        return (
            int(original_size[0] * scale_factor),
            int(original_size[1] * scale_factor)
        )
    
    @staticmethod
    def upscale(image: Image.Image) -> Tuple[Image.Image, Tuple[int, int]]:
        """
        Upscale image if needed.
        
        Returns:
            Tuple of (upscaled_image, original_size)
        """
        original_size = image.size
        if ImageResizer.should_upscale(original_size):
            new_size = ImageResizer.calculate_upscale_size(original_size)
            upscaled = image.resize(new_size, Image.Resampling.LANCZOS)
            return upscaled, original_size
        return image, original_size
    
    @staticmethod
    def downscale(image: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
        """Downscale image to target size."""
        return image.resize(target_size, Image.Resampling.LANCZOS)
