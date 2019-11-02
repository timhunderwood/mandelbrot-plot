import numpy
import multiprocessing
from traits.api import HasTraits, Int, Bool

numpy.seterr(over="ignore", invalid="ignore")


class MandelbrotModel(HasTraits):
    max_iterations = Int(2 ** 7)
    number_of_processors = Int(4)
    x_steps = Int(2 ** 10)
    y_steps = Int(2 ** 10)
    use_multiprocessing = Bool(True)
    _latest_xs = None
    _latest_ys = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _calculate_mandelbrot_without_multiprocessing(self, z):
        """Algorithm to get the mandelbrot set efficiently using numpy.

        Adapted from: http://code.seas.harvard.edu/almondpy/almondpy/blobs/master/mandelbrot-multiprocessing.py
        """

        mandelbrot = numpy.full(z.shape, 0)
        original_z = z.copy()

        for _ in range(self.max_iterations):
            mandelbrot += numpy.abs(z) < 2
            z *= z
            z += original_z
        return mandelbrot

    def create_pool(self, number_of_processors):
        return multiprocessing.Pool(processes=number_of_processors)

    def create_mesh_grid(self, min_x, max_x, min_y, max_y):
        self._latest_xs = numpy.linspace(min_x, max_x, self.x_steps)
        self._latest_ys = numpy.linspace(min_y, max_y, self.y_steps)
        return numpy.meshgrid(self.latest_xs, self.latest_ys)

    @property
    def latest_xs(self):
        return self._latest_xs

    @property
    def latest_ys(self):
        return self._latest_ys

    def create_initial_array(self, min_x, max_x, min_y, max_y):
        x, y = self.create_mesh_grid(min_x, max_x, min_y, max_y)
        return x + 1j * y

    def _calculate_mandelbrot_multiprocessing(self, z):
        pool = self.create_pool(self.number_of_processors)
        return numpy.array(
            pool.map(self._calculate_mandelbrot_without_multiprocessing, z)
        )

    def calculate_mandelbrot(self, z):
        if self.use_multiprocessing:
            return self._calculate_mandelbrot_multiprocessing(z)
        else:
            return self._calculate_mandelbrot_without_multiprocessing(z)
