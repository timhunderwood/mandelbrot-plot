import unittest
import numpy
import time

from mandelbrotplot.mandelbrot_model import MandelbrotModel


class TestMandelbrotModel(unittest.TestCase):
    def setUp(self):
        self.sut = MandelbrotModel()
        self.sut.max_iterations = 2 ** 8  # (for reproducibility in tests)

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

    def test_large_multiprocessing_gives_same_result(self):
        self.sut.number_of_processors = 4
        test_input = self.sut.create_initial_array(-2.25, 0.75, -1.25, 1.25)
        start = time.time()
        test_output_single_process = self.sut._calculate_mandelbrot_without_multiprocessing(
            test_input
        )
        end = time.time()
        time_single_process = end - start

        start = time.time()
        test_output_multi_process = self.sut._calculate_mandelbrot_multiprocessing(
            test_input
        )
        end = time.time()
        time_multi_process = end - start

        self.assertTrue((test_output_multi_process == test_output_single_process).all())
        print(time_single_process / time_multi_process)
