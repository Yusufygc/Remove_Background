"""Image processing service: upscale -> rembg remove (with alpha matting) -> downscale."""

from PIL import Image
from rembg import remove
from typing import Any

from models.image_enhancer import ImageResizer


class ImageProcessor:
    """
    Service class for processing images to remove backgrounds.
    Implements Single Responsibility Principle - only handles image processing.
    """

    def process(
        self,
        input_image: Image.Image,
        model_session: Any,
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

        # Remove background. Alpha matting refines the edge alpha channel
        # (soft transitions for hair/fur) instead of a hard 0/255 cutout;
        # post_process_mask cleans small noise islands in the mask.
        if progress_callback:
            progress_callback("Arka plan siliniyor...")
        output_image = remove(
            processed_image,
            session=model_session,
            alpha_matting=True,
            post_process_mask=True,
        )

        # Downscale if was upscaled
        if ImageResizer.should_upscale(input_image.size):
            if progress_callback:
                progress_callback("Son işlemler...")
            output_image = ImageResizer.downscale(output_image, original_size)

        return output_image
