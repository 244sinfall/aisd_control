"""This module contains main tree entity"""
from PIL import Image, ImageDraw
from constants import DETAIL_TRESHOLD
from tree_part import QuadtreePart


class Quadtree():
    """
        This is main entity of the program which contains either recursive and quadtree parts management logic
    """

    def __init__(self, image, rate):
        self.width, self.height = image.size
        self.rate = rate
        self.current_depth = 0  # Отслеживание глубины рекурсии
        self.init(image)

    def init(self, image):
        """Launches recursion"""
        self.root = QuadtreePart(image, image.getbbox(), 0)
        self.build(self.root, image)

    def build(self, root, image):
        """Builds quadtree structure, splitting roots to parts"""
        if root.depth >= self.rate or root.detail <= DETAIL_TRESHOLD:
            if root.depth > self.current_depth:
                self.current_depth = root.depth
            # Базовый случай
            root.leaf = True
            return

        # Рекурсиный случай
        root.split_quadrant(image)

        for children in root.children:
            self.build(children, image)

    def create_image(self, recursion_depth, cells=False):
        """Returns PIL image"""
        image = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, self.width, self.height), (0, 0, 0))

        leaf_quadrants = self.get_leafs(recursion_depth)

        # Рисуем каждый квадрант в пустом изображении
        for quadrant in leaf_quadrants:
            if cells:
                draw.rectangle(quadrant.bbox, quadrant.color,
                               outline=(0, 0, 0))
            else:
                draw.rectangle(quadrant.bbox, quadrant.color)

        return image

    def get_leafs(self, depth):
        """Returns all quandrants by explicit depth"""
        quandrants = []
        self.recursive_search(self, self.root, depth, quandrants.append)
        return quandrants

    def recursive_search(self, tree, quadrant, max_depth, append_func):
        """Recursive quandrant gather function. Give append func of used to store list"""
        # Базовый случай. Прошли через ограничения или глубина достигла максимальной
        if quadrant.leaf or quadrant.depth == max_depth:
            append_func(quadrant)

        # Рекурсивный случай
        elif quadrant.children is not None:
            for child in quadrant.children:
                self.recursive_search(tree, child, max_depth, append_func)

    def create_gif(self, file_name, duration=1000, loop=0, cells=False, reverse=False):
        """Creates image stage by stage and making array of it. Returns gif of this array"""
        gif = []
        result = self.create_image(self.current_depth, cells=cells)

        for i in range(self.current_depth):
            image = self.create_image(i, cells=cells)
            gif.append(image)
        gif.append(result)
        if reverse:
            gif.reverse()
        gif[0].save(file_name, save_all=True, append_images=gif[1:],
                    duration=duration, loop=loop)
