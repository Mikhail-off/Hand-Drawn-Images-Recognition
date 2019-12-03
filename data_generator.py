# -*- coding: utf-8 -*-

import argparse
import os

argparser = argparse.ArgumentParser()
argparser.add_argument("--dst_dataset", "-dst", type=str,
                       help="Путь до результирующей папки")
argparser.add_argument("--object_count", "-n", type=int, default=100,
                       help="Кол-во генерируемых объектов")
argparser.add_argument("--rewrite", action='store_true', default=False,
                       help="Перезаписать dst папку")

args = argparser.parse_args()


def main():
    print('Data generation started')

if __name__ == '__main__':
    main()