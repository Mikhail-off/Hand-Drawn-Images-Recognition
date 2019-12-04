import os
import glob
from PIL import Image
import shutil

class ImageRender:
    def __init__(self, temp_dir):
        os.makedirs(temp_dir, exist_ok=True)
        self.temp_dir = temp_dir

    def render(self, tikz_command, grid_size):
        canvas = "\draw[fill = white, white] (0,0) rectangle (%d,%d);" % grid_size

        preamble = "\\begin{tikzpicture}"
        preamble += "[pencildraw/.style={black,decorate,decoration={random steps,segment length=4pt,amplitude=1pt}}]"
        preamble += "\n"
        source = preamble + canvas + "\n" + tikz_command + "\n\\end{tikzpicture}"
        source = '''
\\documentclass[convert={density=300,size=%dx%d,outext=.png},tikz]{standalone}
\\usetikzlibrary{decorations.pathmorphing}
\\usetikzlibrary{arrows.meta}
\\begin{document}
%s
\\end{document}
''' % (256, 256, source)

        with open(os.path.join(self.temp_dir, 'temp.tex'), 'w') as f:
            f.write(source)

        os.system('cd temp/ && pdflatex -shell-escape temp.tex > log.txt && rm log.txt')

        image_path = os.path.join(self.temp_dir, 'temp.png')
        image = Image.open(image_path).convert("L")
        return image

    def close(self):
        shutil.rmtree(self.temp_dir)
