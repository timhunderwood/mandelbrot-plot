import unittest
import numpy

from mandelbrotplot.mandelbrot_model import MandelbrotModel


class TestMandelbrotModel(unittest.TestCase):
    def setUp(self):
        self.sut = MandelbrotModel()

    def tearDown(self):
        self.sut = None

    def test_calculate_mandelbrot(self):
        test_input = numpy.linspace(-1, 1, 11)
        test_output = self.sut._calculate_mandelbrot_without_multiprocessing(test_input)
        expected_output = numpy.array([256, 256, 256, 256, 256, 256, 256, 6, 3, 2, 1])
        self.assertTrue((test_output == expected_output).all())

    def test_calculate_mandelbrot_multiprocessing(self):
        test_input = numpy.linspace(-1, 1, 11)
        test_output = self.sut._calculate_mandelbrot_multiprocessing(test_input)
        expected_output = numpy.array([256, 256, 256, 256, 256, 256, 256, 6, 3, 2, 1])
        self.assertTrue((test_output == expected_output).all())

    def test_create_initial_array(self):
        output_array = self.sut.create_initial_array(-1, 1, -1, 1)
        self.assertEqual(output_array.shape, (self.sut.x_steps, self.sut.y_steps))
