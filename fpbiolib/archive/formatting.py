import numpy as np
from dash import html
import math


def slider_marks(x_min, x_max, num_points):
    abs_delta = abs(x_max - x_min)
    if abs_delta >= 1.0:
        marks = {
            i: "{:.0f}".format(i)
            for i in np.linspace(x_min, x_max, num_points)
        }
    elif abs_delta >= 0.10:
        marks = {
            i: "{:.1f}".format(i)
            for i in np.linspace(x_min, x_max, num_points)
        }
    elif abs_delta >= 0.010:
        marks = {
            i: "{:.2f}".format(i)
            for i in np.linspace(x_min, x_max, num_points)
        }
    else:
        marks = {
            i: "{:.3f}".format(i)
            for i in np.linspace(x_min, x_max, num_points)
        }
    return marks


def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])]
        +
        # Body
        [
            html.Tr(
                [html.Td(dataframe.iloc[i][col]) for col in dataframe.columns]
            )
            for i in range(min(len(dataframe), max_rows))
        ]
    )


def dec_notation(num, sci_note_upper):
    num_order_power = math.floor(math.log10(num))
    num_order = 10**num_order_power
    dec = str(int(math.log10(sci_note_upper) - math.log10(num_order)))
    return f"{{:.{dec}f}}".format(num)


def sci_notation(num, sig_figs):
    return f"{{:.{sig_figs}e}}".format(num)


def slider_num_formatter(
    num, sci_sig_figs=3, sci_note_upper=10000, sci_note_lower=0.01
):
    if num >= sci_note_upper or num < sci_note_lower:
        return sci_notation(num, sci_sig_figs)
    else:
        return dec_notation(num, sci_note_upper).rstrip("0").rstrip(".")


def process_str_list(range_limits: str):
    """Some range limits are stored as a formatted string
    for user readability in the csv file.  Process it
    to create a normal python list with floats.
    """
    if not range_limits:
        return None

    bad_chars = "]['"
    for c in bad_chars:
        range_limits = range_limits.replace(c, "")
    range_limits = range_limits.split(",")
    return [float(x) for x in range_limits]
