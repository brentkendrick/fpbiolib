import numpy as np
from dash import html
import math


def slider_marks(x_min, x_max, num_points):
    abs_delta = abs(x_max - x_min)
    if abs_delta >= 1.0:
        marks = {i: "{:.0f}".format(i) for i in np.linspace(x_min, x_max, num_points)}
    elif abs_delta >= 0.10:
        marks = {i: "{:.1f}".format(i) for i in np.linspace(x_min, x_max, num_points)}
    elif abs_delta >= 0.010:
        marks = {i: "{:.2f}".format(i) for i in np.linspace(x_min, x_max, num_points)}
    else:
        marks = {i: "{:.3f}".format(i) for i in np.linspace(x_min, x_max, num_points)}
    return {int(k) if k.is_integer() else k: v for k, v in marks.items()}


def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])]
        +
        # Body
        [
            html.Tr([html.Td(dataframe.iloc[i][col]) for col in dataframe.columns])
            for i in range(min(len(dataframe), max_rows))
        ]
    )


def dec_notation(num, sci_note_upper):
    num_order_power = math.floor(math.log10(num))
    num_order = 10 ** num_order_power
    dec = str(int(math.log10(sci_note_upper) - math.log10(num_order)))
    return f"{{:.{dec}f}}".format(num)


def sci_notation(num, sig_figs):
    return f"{{:.{sig_figs}e}}".format(num)


def slider_num_formatter(
    num, sci_sig_figs=3, sci_note_upper=10000, sci_note_lower=0.01
):
    if num == 0:
        return "0"
    elif num >= sci_note_upper or num < sci_note_lower:
        return sci_notation(num, sci_sig_figs)
    else:
        return dec_notation(num, sci_note_upper).rstrip("0").rstrip(".")


def round_up_nearest_order_mag(x):
    return 10 ** (math.ceil(math.log10(abs(x))))


def slider_log_intervals(max_x):
    upper_interval = round_up_nearest_order_mag(max_x)
    log_intervals = []
    for i in range(7):
        log_intervals.append(int(math.log10(upper_interval) + i - 6))
    return log_intervals


def ten_to_the_x(value):
    if type(value) == list:
        valueList = []
        for i in value:
            valueList.append(10 ** i)
        return valueList
    else:
        return 10 ** value


def slider_log_intervals_float(max_x):
    upper_interval = round_up_nearest_order_mag(max_x)
    log_intervals = []
    for i in range(7):
        log_intervals.append(int(math.log10(upper_interval) + i - 6))
    return log_intervals


def slider_log_mark_format(log_intervals, integer_only=True):
    marks = {(i): "{:#.3g}".format(10 ** i) for i in log_intervals[1:]}
    # for some reason, marks that are 1.0, 10.0, etc must be converted to integers to display in the slider
    if integer_only:
        marks = {
            int(k): "{:.0f}".format(float(v))
            for k, v in marks.items()
            if k.is_integer()
        }
    else:
        marks = {int(k) if k.is_integer() else k: v for k, v in marks.items()}
    return marks
