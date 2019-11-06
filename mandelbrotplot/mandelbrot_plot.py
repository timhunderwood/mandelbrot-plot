from typing import Tuple

import numpy

from chaco import default_colormaps
from chaco.api import Plot, ArrayPlotData, HPlotContainer
from traits.api import HasTraits, Int, Instance, Enum, Button
from traitsui.api import View, VGroup, HGroup, Item, OKCancelButtons
from enable.api import ComponentEditor

from mandelbrotplot.mandelbrot_model import MandelbrotModel
from mandelbrotplot.recalculating_zoom_tool import RecalculatingZoomTool

colormaps = list(default_colormaps.color_map_name_dict.keys())


class MandelbrotPlot(HasTraits):
    """View and Controller for the Mandelbrot Plot interface."""

    mandelbrot_model_view = View(
        VGroup(
            HGroup(
                Item("use_multiprocessing", label="multiprocessing?"),
                Item("number_of_processors", label="processors"),
                label="multiprocessing",
                show_border=True,
            ),
            VGroup(
                Item("max_iterations"),
                Item("x_steps"),
                Item("y_steps"),
                label="calculation",
                show_border=True,
            ),
        ),
        buttons=OKCancelButtons,
        kind="modal",
        resizable=True,
        title="Mandelbrot calculation settings",
        icon=None,
    )
    traits_view = View(
        VGroup(
            HGroup(
                Item("mandelbrot_model", show_label=False),
                Item("colormap"),
                Item("reset_button", show_label=False),
            ),
            Item("container", editor=ComponentEditor(), show_label=False),
            orientation="vertical",
        ),
        resizable=True,
        title="mandelbrot",
    )

    mandelbrot_model = Instance(MandelbrotModel, view=mandelbrot_model_view)
    container = Instance(HPlotContainer)
    colormap = Enum(colormaps)
    reset_button = Button(label="reset")

    _initial_region = (-2.25, 0.75, -1.25, 1.25)
    _plot_data = ArrayPlotData()
    _plot_object = Plot(_plot_data)

    def __init__(self, *args, **kwargs):
        """Instantiates the mandelbrot model and necessary objects for the view/controller."""
        super().__init__(*args, **kwargs)
        self.mandelbrot_model = MandelbrotModel()
        self._update_with_initial_plot_data()

        self.image_plot = self._create_image_plot()
        self.container = HPlotContainer(
            padding=10, fill_padding=True, bgcolor="white", use_backbuffer=True
        )
        self.container.add(self._plot_object)
        self._fix_aspect_ratio()
        self._colormap_changed()
        self._append_tools()

    def _create_image_plot(self):
        """Return a Chaco image plot from the plot object referencing the ArrayPlotData fields."""
        return self._plot_object.img_plot(
            "mandelbrot", xbounds="x_bounds", ybounds="y_bounds"
        )[0]

    def _fix_aspect_ratio(self):
        """Fix the aspect ratio of the container."""
        x_width = (
            self.mandelbrot_model.latest_xs[-1] - self.mandelbrot_model.latest_xs[0]
        )
        y_width = (
            self.mandelbrot_model.latest_ys[-1] - self.mandelbrot_model.latest_ys[0]
        )
        self.container.aspect_ratio = x_width / y_width

    def _update_plot_data(self, mandelbrot_C: numpy.ndarray) -> None:
        """Update the plot_data attribute with passed values.

        Updates the main 2d-array data with mandelbrot_C values
        Updates the x bounds and y bounds of the image with the latest values
         stored on the mandelbrot model.

        :param mandelbrot_C:
        """
        self._plot_data.set_data("mandelbrot", mandelbrot_C)
        self._plot_data.set_data("x_bounds", self.mandelbrot_model.latest_xs)
        self._plot_data.set_data("y_bounds", self.mandelbrot_model.latest_ys)
        if hasattr(self, "image_plot"):
            self.image_plot.index.set_data(
                xdata=self.mandelbrot_model.latest_xs,
                ydata=self.mandelbrot_model.latest_ys,
            )

    def _append_tools(self):
        """Add tools to the necessary components."""
        zoom = RecalculatingZoomTool(
            self._zoom_recalculation_method,
            component=self.image_plot,
            tool_mode="box",
            always_on=True,
        )
        self.image_plot.overlays.append(zoom)

    def _zoom_recalculation_method(
        self, mins: Tuple[float, float], maxs: Tuple[float, float]
    ):
        """Callable for the RecalculatingZoomTool to recalculate/display the mandelbrot set on zoom events.

        :param mins: min positions in selected zoom range
        :param maxs: max positions in selected zoom range
        :return:
        """
        min_x, max_x = mins[0], maxs[0]
        min_y, max_y = mins[1], maxs[1]

        mandelbrot_C = self._recalculate_mandelbrot(min_x, max_x, min_y, max_y)
        self._update_plot_data(mandelbrot_C)
        self.container.invalidate_draw()
        self.container.request_redraw()
        self._fix_aspect_ratio()

    def _recalculate_mandelbrot(
        self, min_x: float, max_x: float, min_y: float, max_y: float
    ) -> numpy.ndarray:
        """Recalculate the mandelbrot set for a given region.

        :param min_x:
        :param max_x:
        :param min_y:
        :param max_y:
        :return:
        """
        z = self.mandelbrot_model.create_initial_array(min_x, max_x, min_y, max_y)
        return self.mandelbrot_model.calculate_mandelbrot(z[:-1, :-1])

    def _mandelbrot_model_changed(self):
        """Method automatically called by Traits when mandelbrot_model attribute changes.

        Recalculates the mandelbrot set for the current range.
        """
        if self.mandelbrot_model.latest_xs is None:
            return
        min_x, max_x = (
            self.mandelbrot_model.latest_xs[-1],
            self.mandelbrot_model.latest_xs[0],
        )
        min_y, max_y = (
            self.mandelbrot_model.latest_ys[-1],
            self.mandelbrot_model.latest_ys[0],
        )
        mandelbrot_C = self._recalculate_mandelbrot(min_x, max_x, min_y, max_y)
        self._update_plot_data(mandelbrot_C)
        self.container.invalidate_draw()
        self.container.request_redraw()
        self._fix_aspect_ratio()

    def _colormap_changed(self):
        """Method automatically called by Traits when colormap attribute changes.

        Updates the color map for the image plot with the selected colormap.
        """
        self._cmap = default_colormaps.color_map_name_dict[self.colormap]
        if self.image_plot is not None:
            value_range = self.image_plot.color_mapper.range
            self.image_plot.color_mapper = self._cmap(value_range)
            self.container.request_redraw()

    def _reset_button_fired(self):
        """Method automatically called by Traits when reset_button fired.

        Resets to the initial range and recalculates the plot.
        """
        self._update_with_initial_plot_data()
        self._fix_aspect_ratio()

    def _update_with_initial_plot_data(self):
        """Creates the initial mesh-grid and mandelbrot values on the grid."""
        self._initial_z_array = self.mandelbrot_model.create_initial_array(
            *self._initial_region
        )
        mandelbrot_C = self.mandelbrot_model.calculate_mandelbrot(
            self._initial_z_array[:-1, :-1]
        )
        self._update_plot_data(mandelbrot_C)


if __name__ == "__main__":
    mandelbrot_plot = MandelbrotPlot()
    mandelbrot_plot.configure_traits()
