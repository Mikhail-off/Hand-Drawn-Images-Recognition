# -*- coding: utf-8 -*-

import argparse
import os
from backend.objects import Point, Line, Figure, MAX_COORDINATE
from backend.image_render import ImageRender

argparser = argparse.ArgumentParser()
argparser.add_argument("--dst_dataset", "-dst", type=str,
                       help="Путь до результирующей папки")
argparser.add_argument("--figures_count", "-n", type=int, default=100,
                       help="Кол-во генерируемых фигур")
argparser.add_argument("--rewrite", action='store_true', default=False,
                       help="Перезаписать dst папку")

args = argparser.parse_args()


ONE_FIGURE_MAX_OBJ = 12


def main():
    os.makedirs(args.dst_dataset, exist_ok=args.rewrite)
    figures = [Figure.sample(ONE_FIGURE_MAX_OBJ) for _ in range(args.figures_count)]

    render = ImageRender('temp/')
    images = []
    for fig in figures:
        images.append(render.render(fig.to_command(), (MAX_COORDINATE, MAX_COORDINATE)))

    for i, img in enumerate(images):
        img.save(os.path.join(args.dst_dataset, '%06d.png' % i))
    render.close()


if __name__ == '__main__':
    main()
