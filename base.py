"""Common interface for denoisers."""

from abc import ABC, abstractmethod
import numpy as np


class Denoiser(ABC):
    @abstractmethod
    def denoise(self, image: np.ndarray) -> np.ndarray:
        """Take a BGR or grayscale image array and return the denoised version."""
        raise NotImplementedError