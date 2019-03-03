from chaco.tools.api import ZoomTool
import numpy


class RecalculatingZoomTool(ZoomTool):
    def __init__(self, recalculation_method, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recalculation_method = recalculation_method

    def _end_select(self, event):
        """ Ends selection of the zoom region, adds the new zoom range to
                the zoom stack, and does the zoom.
                """
        self._screen_end = (event.x, event.y)

        start = numpy.array(self._screen_start)
        end = numpy.array(self._screen_end)

        if sum(abs(end - start)) < self.minimum_screen_delta:
            self._end_selecting(event)
            event.handled = True
            return

        low, high = self._map_coordinate_box(self._screen_start, self._screen_end)

        self.recalculation_method(low, high)

        x_range = self._get_x_mapper().range
        y_range = self._get_y_mapper().range

        prev = (x_range.low, x_range.high, y_range.low, y_range.high)

        if self.tool_mode == "range":
            axis = self._determine_axis()
            if axis == 1:
                # vertical
                next = (x_range.low, x_range.high, low[1], high[1])
            else:
                # horizontal
                next = (low[0], high[0], y_range.low, y_range.high)

        else:
            next = (low[0], high[0], low[1], high[1])

        # self._update_bounds(next)
        #
        # # zoom_state = SelectedZoomState(prev, next)
        # # zoom_state.apply(self)
        # # self._append_state(zoom_state)
        #
        # self._end_selecting(event)
        # event.handled = True
        # return

        self._end_selecting(event)
        event.handled = True
        return

    def _update_bounds(self, next_bounds):
        x_mapper = self._get_x_mapper()
        y_mapper = self._get_y_mapper()

        x_mapper.range.set_bounds(low=next_bounds[0], high=next_bounds[1])
        y_mapper.range.set_bounds(low=next_bounds[2], high=next_bounds[3])
