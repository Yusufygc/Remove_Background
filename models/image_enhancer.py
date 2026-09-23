"""Image resizing helper used to improve segmentation accuracy on small images."""

from PIL import Image
from typing import Tuple

from utils.constants import MIN_DIMENSION_FOR_ENHANCEMENT, IMAGE_SCALE_FACTOR


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
