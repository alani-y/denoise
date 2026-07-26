"""Bilateral filter denoiser."""

import cv2
import numpy as np

from base import Denoiser


class BilateralDenoiser(Denoiser):
    def __init__(self, diameter: int, sigma_color: float, sigma_space: float):
        self.diameter = diameter
        self.sigma_color = sigma_color
        self.sigma_space = sigma_space

    def denoise(self, image: np.ndarray) -> np.ndarray:
        return cv2.bilateralFilter(image, self.diameter, self.sigma_color, self.sigma_space)