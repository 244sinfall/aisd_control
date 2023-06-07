import numpy as np 
import cv2
from PIL import Image, ImageDraw
from argparse import ArgumentParser, ArgumentError
from os import getcwd, path

DETAIL_TRESHOLD = 3
RED_WEIGHT_MULTIPLIER = 0.2989
GREEN_WEIGHT_MULTIPLIER = 0.587
BLUE_WEIGHT_MULTIPLIER = 0.114

# Получает средний rgb изображения
def get_average_image_color(image):
    image_as_array = np.asarray(image)
    row_average = np.average(image_as_array, axis=0)
    average = np.average(row_average, axis=0) 
    for idx, color in enumerate(average):
        average[idx] = 255 if np.isnan(color) else color
    return (int(average[0]), int(average[1]), int(average[2]))

# Получаем детализацию цвета по отрезку гистограммы
def histogram_weight_average(histogram):
    total = sum(histogram)
    error = value = 0
    if total > 0:
        value = sum(i * x for i, x in enumerate(histogram)) / total
        error = sum(x * (value - i) ** 2 for i, x in enumerate(histogram)) / total
        error = error ** 0.5
    return error

# Детализация всей гистограммы
def get_histogram_detail(histogram):
    red_detail = histogram_weight_average(histogram[:256])
    green_detail = histogram_weight_average(histogram[256:512])
    blue_detail = histogram_weight_average(histogram[512:768])

    detail_intensity = red_detail * RED_WEIGHT_MULTIPLIER + green_detail * GREEN_WEIGHT_MULTIPLIER + blue_detail * BLUE_WEIGHT_MULTIPLIER

    return detail_intensity

class QuadtreePart():
    def __init__(self, image, bbox, depth):
        self.bbox = bbox
        self.depth = depth
        self.children = None
        self.leaf = False
        # Задаем площадь QuadtreePart как отдельное изображение
        image = image.crop(bbox)
        #Гистограмма и детализация
        histogram = image.histogram()
        self.detail = get_histogram_detail(histogram)

        self.color = get_average_image_color(image)

    # Разделяет площадь квадранта на 4 части
    def split_quadrant(self, image):
        left, top, width, height = self.bbox

        middle_x = left + (width - left) / 2
        middle_y = top + (height - top) / 2

        upper_left = QuadtreePart(image, (left, top, middle_x, middle_y), self.depth+1)
        upper_right = QuadtreePart(image, (middle_x, top, width, middle_y), self.depth+1)
        bottom_left = QuadtreePart(image, (left, middle_y, middle_x, height), self.depth+1)
        bottom_right = QuadtreePart(image, (middle_x, middle_y, width, height), self.depth+1)

        self.children = [upper_left, upper_right, bottom_left, bottom_right]

class Quadtree():
    def __init__(self, image, rate):
        self.width, self.height = image.size 
        self.rate = rate
        self.current_depth = 0 # Отслеживание глубины рекурсии
        self.init(image)
    
    def init(self, image):

        self.root = QuadtreePart(image, image.getbbox(), 0)
        self.build(self.root, image)

    def build(self, root, image):
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
        image = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, self.width, self.height), (0, 0, 0))

        leaf_quadrants = self.get_leafs(recursion_depth)

        # Рисуем каждый квадрант в пустом изображении
        for quadrant in leaf_quadrants:
            if cells:
                draw.rectangle(quadrant.bbox, quadrant.color, outline=(0, 0, 0))
            else:
                draw.rectangle(quadrant.bbox, quadrant.color)

        return image

    def get_leafs(self, depth):
        quandrants = []
        self.recursive_search(self, self.root, depth, quandrants.append)
        return quandrants

    def recursive_search(self, tree, quadrant, max_depth, append_func):
        # Базовый случай. Прошли через ограничения или глубина достигла максимальной
        if quadrant.leaf == True or quadrant.depth == max_depth:
            append_func(quadrant)

        # Рекурсивный случай
        elif quadrant.children != None:
            for child in quadrant.children:
                self.recursive_search(tree, child, max_depth, append_func)

    def create_gif(self, file_name, duration=1000, loop=0, cells=False, reverse=False):
        gif = []
        result = self.create_image(self.current_depth, cells=cells)

        for i in range(self.current_depth):
            image = self.create_image(i, cells=cells)
            gif.append(image)
        gif.append(result)
        if reverse:
            gif.reverse()
        gif[0].save(file_name,save_all=True,append_images=gif[1:], duration=duration, loop=loop)
        

if __name__ == '__main__':
    # Работа с аргументами
    parser = ArgumentParser(prog='Quadtree Image Compressor',
                            description='This software compress the input image using quadtrees',
                            epilog='Made by Dmitry Filin for educational purposes')
    parser.add_argument('-o', '--output', dest='output',
                        help='Output dir', default=getcwd())
    parser.add_argument('-g', '--gif', dest='gif',
                        help='Add this argument to produce gif as well',
                        action='store_true')
    parser.add_argument('--gif-reverse', dest='gif_reverse',
                        help='Make gif from original to compressed (reversed of false)', action='store_true')
    parser.add_argument('-c', '--cells', dest='cells',
                        help='Add this argument to retain cells on output image',
                        action='store_true')
    parser.add_argument('-r', '--rate', dest='rate', default=10,
                        help='Details treshold (integer, defaults to 10), lower value is lower quality -> lower time complexity', type=int)
    
    parser.add_argument('source_file')

    args = parser.parse_args()
    # Ошибки ввода
    if not path.isdir(args.output):
       raise ArgumentError('Output arg should contain path only/dir doesnt exist.')
    # Открытие изображения
    source_image = Image.open(args.source_file)
    # Создание дерева
    quadtree = Quadtree(source_image, args.rate)
    # Создание картинки / гифки
    result = quadtree.create_image(args.rate + 8, args.cells)
    result.save(f"{args.output}/output.jpg")
    if args.gif:
        quadtree.create_gif(f"{args.output}/output.gif", cells=args.cells, reverse=args.gif_reverse)
    