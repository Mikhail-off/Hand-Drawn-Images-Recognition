import os
from PIL import Image
import shutil

IMAGE_SIZE = 256


class ImageRender:
    def __init__(self, temp_dir):
        os.makedirs(temp_dir, exist_ok=True)
        self.temp_dir = temp_dir

    def render(self, figures, grid_size, noisy=False):
        canvas = "\draw[fill = white, white] (0,0) rectangle (%d,%d);" % grid_size

        preamble = "\\begin{tikzpicture}"
        preamble += "[pencildraw/.style={black,decorate,decoration={random steps,segment length=4pt,amplitude=1pt}}]"
        preamble += "\n"
        sources = [preamble + canvas + "\n" + figure.to_command(noisy) + "\n\\end{tikzpicture}" for figure in figures]
        source = "\n\n\n".join(sources)
        source = "\\documentclass[convert={density=300,size=%dx%d,outext=.png},tikz]{standalone}"\
                 "\\usetikzlibrary{decorations.pathmorphing}"\
                 "\\usetikzlibrary{arrows.meta}"\
                 "\\begin{document}"\
                 "%s"\
                 "\\end{document}" % (IMAGE_SIZE, IMAGE_SIZE, source)

        with open(os.path.join(self.temp_dir, 'temp.tex'), 'w') as f:
            f.write(source)

        os.system('cd temp/ && pdflatex -shell-escape temp.tex > log.txt && rm log.txt')
        images = []
        for i in range(len(figures)):
            if len(figures) != 1:
                format_str = 'temp-%%0%dd.png' % len(str(len(figures) - 1))
                image_path = os.path.join(self.temp_dir, format_str % i)
            else:
                image_path = os.path.join(self.temp_dir, 'temp.png')

            image = Image.open(image_path).convert("L")
            (width, height) = image.size
            # плохая картинка
            if width != IMAGE_SIZE or height != IMAGE_SIZE:
                continue
            images.append(image)
        return images

    def close(self):
        shutil.rmtree(self.temp_dir)
