"""Non-local means denoiser."""

import cv2
import numpy as np

from base import Denoiser


class NonLocalMeansDenoiser(Denoiser):
    def __init__(self, h: float, template_window_size: int, search_window_size: int):
        self.h = h
        self.template_window_size = template_window_size
        self.search_window_size = search_window_size

    def denoise(self, image: np.ndarray) -> np.ndarray:
        if image.ndim == 3:
            return cv2.fastNlMeansDenoisingColored(
                image,
                None,
                self.h,
                self.h,
                self.template_window_size,
                self.search_window_size,
            )
        return cv2.fastNlMeansDenoising(
            image,
            None,
            self.h,
            self.template_window_size,
            self.search_window_size,
        )