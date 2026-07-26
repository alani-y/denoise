"""Dark frame subtraction: removes fixed-pattern sensor noise before denoising."""

from pathlib import Path

import cv2
import numpy as np


class DarkFrameSubtractor:
    def __init__(self, dark_frame_path: str):
        path = Path(dark_frame_path)
        if not path.exists():
            raise FileNotFoundError(f"Dark frame not found: '{dark_frame_path}'")

        self.dark_frame = cv2.imread(str(path))
        if self.dark_frame is None:
            raise ValueError(f"Could not read dark frame (corrupt/unsupported file): '{dark_frame_path}'")

    def subtract(self, image: np.ndarray) -> np.ndarray:
        dark = self._match_dark_frame(image)
        # cv2.subtract clips to 0 instead of wrapping around like raw
        # numpy subtraction would on uint8 (e.g. 5 - 10 -> 251, not 0).
        return cv2.subtract(image, dark)

    def _match_dark_frame(self, image: np.ndarray) -> np.ndarray:
        dark = self.dark_frame

        # Resize dark frame if it doesn't match the input image's dimensions.
        if dark.shape[:2] != image.shape[:2]:
            dark = cv2.resize(dark, (image.shape[1], image.shape[0]))

        # Match channel count: convert dark frame to grayscale if the
        # input image is grayscale, or vice versa.
        image_is_color = image.ndim == 3
        dark_is_color = dark.ndim == 3
        if image_is_color and not dark_is_color:
            dark = cv2.cvtColor(dark, cv2.COLOR_GRAY2BGR)
        elif not image_is_color and dark_is_color:
            dark = cv2.cvtColor(dark, cv2.COLOR_BGR2GRAY)

        return dark