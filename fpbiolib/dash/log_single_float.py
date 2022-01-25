import math
import numpy as np
from .slider_formatting import (
    slider_num_formatter,
    slider_log_mark_format,
    ten_to_the_x,
    round_up_nearest_order_mag,
)

from dash import dcc, html, callback_context
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc


def log_single_float_slider_layout(
    label="default", slider_id="default", min=1, max=100, step=0.01, marks_option=None
):

    max_round = round_up_nearest_order_mag(max)
    log_intervals = np.round(np.linspace(math.log10(min), math.log10(max_round), 7), 2)
    if marks_option:
        marks = slider_log_mark_format(log_intervals, integer_only=True)
    else:
        marks = {}
    min_interval = log_intervals[0]
    max_interval = log_intervals[-1]

    layout = html.Div(
        [
            dbc.Label(label, class_name="slider-control-label"),
            html.Div(
                [
                    dcc.Slider(
                        id=slider_id,
                        marks=marks,
                        value=min_interval,
                        min=min_interval,
                        max=max_interval,
                        step=step,
                        dots=False,
                        vertical=False,
                        updatemode="mouseup",
                        # tooltip={'always_visible':True, 'placement':'bottom'},
                        className="float_slider2",
                    ),
                    dcc.Input(
                        id=f"{slider_id}-input",
                        type="text",
                        debounce=True,
                        value=str(min_interval),
                        className="slider_input2",
                    ),
                ],
                id=f"{slider_id}_div",
                className="slider_div",
            ),
        ],
        className="slider_container",
    )

    return layout


def log_single_float_slider_callbacks(app, slider_id="default"):
    # Link slider and input box values, seeded with initial x-min / max values
    @app.callback(
        Output(f"{slider_id}-input", "value"),
        Output(f"{slider_id}", "value"),  # primary output of slider values
        Output(f"{slider_id}-input", "style"),
        Input(f"{slider_id}", "value"),
        Input(f"{slider_id}-input", "value"),
    )
    def callback(slider_value, input_value):

        ctx = callback_context
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # Format slider values (and accompanying inputs since they are initially defined by slider values)
        slider_str_value = slider_num_formatter(
            float(ten_to_the_x(slider_value)),
            sci_sig_figs=3,
            sci_note_upper=10000,
            sci_note_lower=0.01,
        )

        # Set truncation values to those in either the input box or slider values
        input_value = (
            input_value if trigger_id == f"{slider_id}-input" else slider_str_value
        )

        slider_value = (
            slider_value
            if trigger_id == f"{slider_id}"
            else math.log10(float(input_value))
        )

        # Pass width of dcc input based on number of characters in the input number
        input_style = {
            "width": f"{str(sum(c.isalnum() for c in str(input_value))*10 + 2)}px",
            "textAlign": "right",
        }

        return input_value, slider_value, input_style


def log_single_float_slider_layout_callbacks(
    app, slider_id="default", layout_id="default_layout", min=1, max=100, step=0.01
):
    @app.callback(
        Output(layout_id, "children"), Input("data_loading", "children"),
    )
    def slider(data_loading):
        if data_loading == None:
            raise PreventUpdate
        # print('Data loading inside log single float slider: ', data_loading)

        max_round = round_up_nearest_order_mag(max)
        log_intervals = np.round(
            np.linspace(math.log10(min), math.log10(max_round), 7), 2
        )
        marks = slider_log_mark_format(log_intervals, integer_only=True)
        min_interval = log_intervals[0]
        max_interval = log_intervals[-1]
        layout = html.Div(
            [
                dcc.Slider(
                    id=slider_id,
                    marks=marks,
                    value=min_interval,
                    min=min_interval,
                    max=max_interval,
                    step=step,
                    dots=False,
                    vertical=False,
                    updatemode="mouseup",
                    # tooltip={'always_visible':True, 'placement':'bottom'},
                    className="float_slider",
                ),
                dcc.Input(
                    id=f"{slider_id}-input",
                    type="text",
                    # debounce=True,
                    value=str(min_interval),
                    className="slider_input",
                ),
            ],
            id=f"{slider_id}_div",
            className="slider_div",
        )

        return layout
