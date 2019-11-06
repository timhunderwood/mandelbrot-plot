import numpy
import multiprocessing
from traits.api import HasTraits, Int, Bool

numpy.seterr(over="ignore", invalid="ignore")


class MandelbrotModel(HasTraits):
    """Model of the Mandelbrot set calculator.

    Using the Traits package, so MandelbrotModel inherits from HasTraits
    and defines class level attributes that may be edited or updated by a
    user interface.
    """

    max_iterations = Int(2 ** 7)
    number_of_processors = Int(4)
    x_steps = Int(2 ** 10)
    y_steps = Int(2 ** 10)
    use_multiprocessing = Bool(True)
    _latest_xs = None
    _latest_ys = None

    def calculate_mandelbrot(self, z: numpy.ndarray) -> numpy.ndarray:
        """Calculates the mandelbrot set for a given input array of complex values.

        Determines whether multiprocessing should be used based on use_multiprocessing attribute.
        :param z:
        :return:
        """
        if self.use_multiprocessing:
            return self._calculate_mandelbrot_multiprocessing(z)
        else:
            return self._calculate_mandelbrot_without_multiprocessing(z)

    def create_initial_array(
        self, min_x: float, max_x: float, min_y: float, max_y: float
    ) -> numpy.ndarray:
        """Create a meshgrid of complex numbers on the complex plane."""
        x, y = self._create_mesh_grid(min_x, max_x, min_y, max_y)
        return x + 1j * y

    def _calculate_mandelbrot_without_multiprocessing(self, z):
        """Algorithm to get the mandelbrot set efficiently using numpy.

        Adapted from: http://code.seas.harvard.edu/almondpy/almondpy/blobs/master/mandelbrot-multiprocessing.py
        """
        z = z.copy()
        original_z = z.copy()
        mandelbrot = numpy.full(z.shape, 0)

        for _ in range(self.max_iterations):
            mandelbrot += numpy.abs(z) < 2
            z *= z
            z += original_z
        return mandelbrot

    def _create_pool(self, number_of_processors: int) -> multiprocessing.Pool:
        """Returns a multiprocessing pool for the requested number of processors."""
        return multiprocessing.Pool(processes=number_of_processors)

    def _create_mesh_grid(
        self, min_x: float, max_x: float, min_y: float, max_y: float
    ) -> numpy.ndarray:
        """Create a 2d meshgrid array for the relevant part of the mandelbrot set specified by min max x,y arguments."""
        self._latest_xs = numpy.linspace(min_x, max_x, self.x_steps)
        self._latest_ys = numpy.linspace(min_y, max_y, self.y_steps)
        return numpy.meshgrid(self.latest_xs, self.latest_ys)

    @property
    def latest_xs(self):
        """Tracks the x (real) region/bounds calculated."""
        return self._latest_xs

    @property
    def latest_ys(self):
        """Tracks the y (imaginary) region/bounds calculated."""
        return self._latest_ys

    def _calculate_mandelbrot_multiprocessing(self, z: numpy.ndarray) -> numpy.ndarray:
        """Calculate the mandelbrot set using multiprocessing.

        Input z is a 2d meshgrid array. A pool is created with the desired
        number of processors. The calculate without multiprocessing method is then applied to the
        2d grid, which effectively calculates the values for horizontal lines (1d arrays) in the
        2d grid separately.

        The individual lines are then combined back into a 2d-array and returned.
        """
        pool = self._create_pool(self.number_of_processors)
        return numpy.array(
            pool.map(self._calculate_mandelbrot_without_multiprocessing, z)
        )
