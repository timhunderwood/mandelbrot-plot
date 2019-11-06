from chaco.tools.api import ZoomTool
import numpy


class RecalculatingZoomTool(ZoomTool):
    """Extends the standard Chaco zoom tool.

     Calls a method to update underlying plot data after every zoom event.
     """

    def __init__(self, recalculation_method, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recalculation_method = recalculation_method

    def _end_select(self, event):
        """ Ends selection of the zoom region, adds the new zoom range to
        the zoom stack, and does the zoom.

        Overidden for Recalculating ZoomTool to also call the recalculation method.
        Currently does not work with the saved zoom state (using zoom history will not call the
        recalculation method).
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

        self._end_selecting(event)
        event.handled = True
        return
