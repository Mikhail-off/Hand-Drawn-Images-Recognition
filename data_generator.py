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
argparser.add_argument("--batch_size", "-bs", type=int, default=50,
                       help="Размер батча")
argparser.add_argument("--rewrite", action='store_true', default=False,
                       help="Перезаписать dst папку")
argparser.add_argument("--noisy", action='store_true', default=False,
                       help="Добавить шум")

args = argparser.parse_args()

ONE_FIGURE_MAX_OBJ = 8


def main():
    os.makedirs(args.dst_dataset, exist_ok=args.rewrite)

    render = ImageRender('temp/')
    i = 0
    while i < args.figures_count:
        start = i
        end = min(args.figures_count, i + args.batch_size)
        cur_batch_size = end - start
        figures = [Figure.sample(ONE_FIGURE_MAX_OBJ) for _ in range(cur_batch_size)]
        images = render.render(figures, (MAX_COORDINATE, MAX_COORDINATE), args.noisy)

        for batch_i, img in enumerate(images):
            img.save(os.path.join(args.dst_dataset, '%06d.png' % (i + batch_i)))

        i += len(images)

    render.close()


if __name__ == '__main__':
    main()
