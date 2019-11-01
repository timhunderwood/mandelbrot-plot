# mandelbrot-plot
Interactive plotting of the Mandelbrot set with zoom functionality, using Python with the Chaco plotting library.

##Installation
Relies on chaco library for plotting which is easiest to install using conda. Once conda is installed in a Python 3.7
setup, follow the below steps to install.

On any OS (windows / MAC / Linux):
* `conda create --name mandelbrot-plot python=3.7`
* `conda activate mandelbrot-plot`
* `conda install swig`
* `pip install numpy`
* `pip install -r requirements.txt`

Alternatively (for windows only):
* `conda create -f environment.yml`