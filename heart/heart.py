from bisect import bisect

import svgwrite
from svgwrite.animate import Animate, AnimateTransform

from .config import (
    BASE_HEART_COLOR,
    BASE_HEART_TEXT_COLOR,
    BASE_PATH_TRANSLATE,
    BASE_TEXT_STYLE,
    BASE_TRANSLATE,
    PATH_D,
    THREE_LETTERS_TEXT_TRANSLATE,
    TWO_LETTERS_TEXT_TRANSLATE,
)
from .utils import intersperse, make_key_times, make_key_values


class Heart:
    def __init__(self, file_path, base_height=150, base_width=150):
        self.file_path = file_path
        self.base_height = base_height
        self.base_width = base_width
        self.values = None
        self.dur = None
        self.letters_trans_dict = {
            2: TWO_LETTERS_TEXT_TRANSLATE,
            3: THREE_LETTERS_TEXT_TRANSLATE,
        }
        self._make_drawer()

    def _make_drawer(self):
        self.drawer = svgwrite.Drawing(
            self.file_path, (str(self.base_height), str(self.base_width))
        )
        self.drawer.viewbox(0, 0, 200, 200)

    def set_values(self, values):
        self.values = values
        # from start -> end (heart rate timeline)
        self.values.reverse()

    def _make_g(self):
        return self.drawer.g(transform=BASE_TRANSLATE)

    def _make_path(self):
        return self.drawer.path(
            fill=BASE_HEART_COLOR,
            transform=BASE_PATH_TRANSLATE,
            d=PATH_D,
            stroke="#B6BBC1",
            stroke_width=2,
        )

    def _make_base_animate_transform(self):
        values = self._make_heart_scale_values()
        values_str = ";".join(values) + ";"
        return AnimateTransform(
            type="scale",
            dur=self.dur,
            values=values_str,
            repeatCount="indefinite",
            additive="sum",
            transform="scale",
        )

    def _make_animate(self, index):
        num_count = len(self.values)
        a = Animate(
            "opacity",
            dur=self.dur,
            values=make_key_values(num_count, index),
            keyTimes=make_key_times(num_count),
            repeatCount="indefinite",
        )
        return a

    def _make_text(self, value, index):
        transform = self.letters_trans_dict.get(len(value))
        t = self.drawer.text(
            str(value),
            transform=transform,
            fill=BASE_HEART_TEXT_COLOR,
            style=BASE_TEXT_STYLE,
        )
        text_anmiate = self._make_animate(index)
        t.add(text_anmiate)
        return t

    def __compute_statistics(self):
        if not self.values:
            raise Exception("No heart rate values set")
        dur_break_points = (5, 10, 15, 20)
        i = bisect(dur_break_points, len(self.values))
        self.dur = str(12 * i) + "s"

    def _make_heart_scale_values(self):
        """
        break_points -> scale number
        """
        break_points = ("0.625", "0.75", "0.875", "1.125", "1.25", "1.375", "1.5")
        min_value, max_value = min(self.values), max(self.values)
        interval = (max_value - min_value) / 5
        heart_rate_points = [min_value + interval * i for i in range(5)]
        heart_rate_points.append(max_value)
        heart_scale_list = [
            break_points[bisect(heart_rate_points, i)] for i in self.values
        ]
        # Make the effect of a beating heart
        heart_scale_list = intersperse(heart_scale_list, "1")
        return heart_scale_list

    def make_heart_svg(self):
        self.__compute_statistics()
        g = self._make_g()
        path = self._make_path()
        path_animate = self._make_base_animate_transform()
        g.add(path)
        g.add(path_animate)
        for index, v in enumerate(self.values):
            g.add(self._make_text(str(v), index))
        self.drawer.add(g)
        self.drawer.save()
