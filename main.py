"""Program start point"""
from argparse import ArgumentParser, ArgumentError
from os import getcwd, path
from PIL import Image
from tree import Quadtree


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
                        help='Make gif from original to compressed (reversed of false)',
                        action='store_true')
    parser.add_argument('-c', '--cells', dest='cells',
                        help='Add this argument to retain cells on output image',
                        action='store_true')
    parser.add_argument('-r', '--rate', dest='rate', default=10,
                        help='Details treshold (integer, defaults to 10),' +
                        ' lower value is lower quality -> lower time complexity', type=int)

    parser.add_argument('source_file')

    args = parser.parse_args()
    # Ошибки ввода
    if not path.isdir(args.output):
        raise ArgumentError(
            None, 'Output arg should contain path only/dir doesnt exist.')
    # Открытие изображения
    source_image = Image.open(args.source_file)
    # Создание дерева
    quadtree = Quadtree(source_image, args.rate)
    # Создание картинки / гифки
    result = quadtree.create_image(args.rate + 8, args.cells)
    result.save(f"{args.output}/output.jpg")
    if args.gif:
        quadtree.create_gif(f"{args.output}/output.gif",
                            cells=args.cells, reverse=args.gif_reverse)
