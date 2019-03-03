from chaco import default_colormaps
from chaco.api import Plot, ArrayPlotData, HPlotContainer
from traits.api import HasTraits, Int, Instance, Button, Enum
from traitsui.api import View, VGroup, HGroup, Item, InstanceEditor
from enable.api import ComponentEditor

from mandelbrotplot.mandelbrot_model import MandelbrotModel
from mandelbrotplot.recalculating_zoom_tool import RecalculatingZoomTool

colormaps = list(default_colormaps.color_map_name_dict.keys())


class MandelbrotPlot(HasTraits):
    mandelbrot_model = Instance(MandelbrotModel)
    plot_data = ArrayPlotData()
    plot_object = Plot(plot_data)
    container = Instance(HPlotContainer)
    fix_aspect_ratio_button = Button()
    mandelbrot = "mandelbrot"
    min_x = Int(-2.25)
    max_x = Int(0.75)
    min_y = Int(-1.25)
    max_y = Int(1.25)
    colormap = Enum(colormaps)

    traits_view = View(
        VGroup(
            HGroup(
                Item("mandelbrot_model", editor=InstanceEditor(), show_label=False),
                Item("fix_aspect_ratio_button", show_label=False),
                Item("colormap"),
            ),
            Item("container", editor=ComponentEditor(), show_label=False),
            orientation="vertical",
        ),
        resizable=True,
        title=mandelbrot,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mandelbrot_model = MandelbrotModel()
        self._initial_z_array = self.mandelbrot_model.create_initial_array(
            -2.25, 0.75, -1.25, 1.25
        )

        mandelbrot_C = self.mandelbrot_model.calculate_mandelbrot(
            self._initial_z_array[:-1, :-1]
        )
        self.update_plot_data(mandelbrot_C)

        self.image_plot = self.create_image_plot()
        self.container = HPlotContainer(
            padding=10, fill_padding=True, bgcolor="white", use_backbuffer=True
        )
        self.container.add(self.plot_object)
        self.fix_aspect_ratio()
        self._append_tools()

    def create_image_plot(self):
        return self.plot_object.img_plot(
            self.mandelbrot, xbounds="x_bounds", ybounds="y_bounds"
        )[0]

    def fix_aspect_ratio(self):
        x_width = (
            self.mandelbrot_model.latest_xs[-1] - self.mandelbrot_model.latest_xs[0]
        )
        y_width = (
            self.mandelbrot_model.latest_ys[-1] - self.mandelbrot_model.latest_ys[0]
        )
        self.container.aspect_ratio = x_width / y_width

    def _fix_aspect_ratio_button_fired(self):
        print("click")
        self.fix_aspect_ratio()

    def update_plot_data(self, mandelbrot_C):
        """

        :return:
        """
        self.plot_data.set_data(self.mandelbrot, mandelbrot_C)
        self.plot_data.set_data("x_bounds", self.mandelbrot_model.latest_xs)
        self.plot_data.set_data("y_bounds", self.mandelbrot_model.latest_ys)
        if hasattr(self, "image_plot"):
            self.image_plot.index.set_data(
                xdata=self.mandelbrot_model.latest_xs,
                ydata=self.mandelbrot_model.latest_ys,
            )

    def _append_tools(self):
        zoom = RecalculatingZoomTool(
            self._zoom_recalculation_method,
            component=self.image_plot,
            tool_mode="box",
            always_on=True,
        )
        self.image_plot.overlays.append(zoom)

    def _zoom_recalculation_method(self, mins, maxs):
        min_x, max_x = mins[0], maxs[0]
        min_y, max_y = mins[1], maxs[1]

        mandelbrot_C = self._recalculate_mandelbrot(min_x, max_x, min_y, max_y)
        self.update_plot_data(mandelbrot_C)
        self.container.invalidate_draw()
        self.container.request_redraw()
        self.fix_aspect_ratio()

    def _recalculate_mandelbrot(self, min_x, max_x, min_y, max_y):
        z = self.mandelbrot_model.create_initial_array(min_x, max_x, min_y, max_y)
        return self.mandelbrot_model.calculate_mandelbrot(z[:-1, :-1])

    def _mandelbrot_model_changed(self):
        print("recalculating mandelbrot")
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
        self.update_plot_data(mandelbrot_C)
        self.container.invalidate_draw()
        self.container.request_redraw()
        self.fix_aspect_ratio()

    def _colormap_changed(self):
        self._cmap = default_colormaps.color_map_name_dict[self.colormap]
        if self.image_plot is not None:
            value_range = self.image_plot.color_mapper.range
            self.image_plot.color_mapper = self._cmap(value_range)
            self.container.request_redraw()


if __name__ == "__main__":
    mandelbrot_plot = MandelbrotPlot()
    mandelbrot_plot.configure_traits()
