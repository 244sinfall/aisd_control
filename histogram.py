"""
This module contains Histogram class
"""
from constants import RED_WEIGHT_MULTIPLIER, GREEN_WEIGHT_MULTIPLIER, BLUE_WEIGHT_MULTIPLIER

class Histogram:
    """
        Histogram class encapsulates logic of getting detail and weight of histogram
    """
    def __init__(self, histogram_array: list[int]) -> None:
        self.hist = histogram_array

    def average_weight(self, start_index: int, end_index: int) -> float:
        """Returns average detail weight of histogram's part"""
        needed_slice = self.hist[start_index:end_index]
        total = sum(needed_slice)
        error = value = 0
        if total > 0:
            value = sum(i * x for i, x in enumerate(needed_slice)) / total
            error = sum(x * (value - i) ** 2 for i, x in enumerate(needed_slice)) / total
            error = error ** 0.5
        return error

    def get_histogram_detail(self) -> float:
        """Return overall histogram detail instensity"""
        red_detail = self.average_weight(0, 256)
        green_detail = self.average_weight(256, 512)
        blue_detail = self.average_weight(512, 768)

        detail_intensity = red_detail * RED_WEIGHT_MULTIPLIER + green_detail * GREEN_WEIGHT_MULTIPLIER + blue_detail * BLUE_WEIGHT_MULTIPLIER

        return detail_intensity
