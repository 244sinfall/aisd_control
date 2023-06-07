"""
    This module contains QuadtreePart class
"""
from PIL import Image
import numpy as np
from histogram import Histogram


class QuadtreePart():
    """
        This class encapsulate inner quadtree part logic
    """

    def __init__(self, image, bbox, depth):
        self.bbox = bbox
        self.depth = depth
        self.children = None
        self.leaf = False
        # Задаем площадь QuadtreePart как отдельное изображение
        image = image.crop(bbox)
        # Гистограмма и детализация
        histogram = Histogram(image.histogram())
        self.detail = histogram.get_histogram_detail()

        self.color = self.get_average_image_color(image)

    def get_average_image_color(self, image: Image):
        """
        Return average rgb value for image
        """
        image_as_array = np.asarray(image)
        row_average = np.average(image_as_array, axis=0)
        average = np.average(row_average, axis=0)
        for idx, color in enumerate(average):
            average[idx] = 255 if np.isnan(color) else color
        return (int(average[0]), int(average[1]), int(average[2]))

    def split_quadrant(self, image):
        """
        Splits current bbox to 4 new Quadtree Parts
        """
        left, top, width, height = self.bbox

        middle_x = left + (width - left) / 2
        middle_y = top + (height - top) / 2

        upper_left = QuadtreePart(
            image, (left, top, middle_x, middle_y), self.depth+1)
        upper_right = QuadtreePart(
            image, (middle_x, top, width, middle_y), self.depth+1)
        bottom_left = QuadtreePart(
            image, (left, middle_y, middle_x, height), self.depth+1)
        bottom_right = QuadtreePart(
            image, (middle_x, middle_y, width, height), self.depth+1)

        self.children = [upper_left, upper_right, bottom_left, bottom_right]
