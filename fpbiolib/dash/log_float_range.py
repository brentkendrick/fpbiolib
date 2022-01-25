import math
from .slider_formatting import (
    slider_num_formatter,
    slider_log_intervals,
    ten_to_the_x,
    slider_marks,
)

from dash import dcc, html, callback_context
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate


def log_float_range_slider_layout_callbacks(
    app,
    slider_id="default",
    layout_id="default_layout",
    min=1,
    max=100,
    step=1,
    marks_option=None,
):
    @app.callback(
        Output(layout_id, "children"), Input("data_loading", "children"),
    )
    def slider(data_loading):
        if data_loading == None:
            raise PreventUpdate

        if marks_option:
            marks = slider_marks(min, max, 10)
        else:
            marks = {}

        log_intervals = slider_log_intervals(max)
        layout = html.Div(
            [
                dcc.RangeSlider(
                    id=slider_id,
                    marks={(i): "{}".format(10 ** i) for i in log_intervals[1:]},
                    value=[min, max],
                    min=min,
                    max=max,
                    step=10 ** min,
                    dots=False,
                    vertical=False,
                    # marks = slider_marks(min, max, 20),
                    updatemode="mouseup",
                    tooltip={"always_visible": False, "placement": "bottom"},
                    className="float_slider",
                ),
                dcc.Input(
                    id=f"{slider_id}-low-input",
                    type="text",
                    debounce=True,
                    value=str(min),
                    className="slider_input",
                ),
                html.P("–", id=f"{slider_id}slider_en_space", className="en_space"),
                dcc.Input(
                    id=f"{slider_id}-high-input",
                    type="text",
                    debounce=True,
                    value=str(max),
                    className="slider_input",
                ),
            ],
            id=f"{slider_id}_div",
            className="slider_div",
        )

        return layout

    # Link slider and input box values, seeded with initial x-min / max values
    @app.callback(
        Output(f"{slider_id}-low-input", "value"),
        Output(f"{slider_id}-high-input", "value"),
        Output(f"{slider_id}", "value"),  # primary output of slider values
        Output(f"{slider_id}-low-input", "style"),
        Output(f"{slider_id}-high-input", "style"),
        Input(f"{slider_id}", "value"),
        Input(f"{slider_id}-low-input", "value"),
        Input(f"{slider_id}-high-input", "value"),
    )
    def callback(slider, low_input_value, high_input_value):

        ctx = callback_context
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # Format slider values (and accompanying inputs since they are initially defined by slider values)
        slider_0_str = slider_num_formatter(
            float(ten_to_the_x(slider[0])),
            sci_sig_figs=3,
            sci_note_upper=10000,
            sci_note_lower=0.01,
        )
        slider_1_str = slider_num_formatter(
            float(ten_to_the_x(slider[1])),
            sci_sig_figs=3,
            sci_note_upper=10000,
            sci_note_lower=0.01,
        )

        # Set truncation values to those in either the input box or slider values
        low_input_value = (
            low_input_value if trigger_id == f"{slider_id}-low-input" else slider_0_str
        )
        high_input_value = (
            high_input_value
            if trigger_id == f"{slider_id}-high-input"
            else slider_1_str
        )
        slider_value = (
            slider
            if trigger_id == f"{slider_id}"
            else [
                math.log10(float(low_input_value)),
                math.log10(float(high_input_value)),
            ]
        )

        # Pass width of dcc input based on number of characters in the input number
        low_input_style = {
            "width": f"{str(sum(c.isalnum() for c in str(low_input_value))*10 + 2)}px",
            "textAlign": "right",
        }
        high_input_style = {
            "width": f"{str(sum(c.isalnum() for c in str(high_input_value))*10 + 2)}px"
        }
        return (
            low_input_value,
            high_input_value,
            slider_value,
            low_input_style,
            high_input_style,
        )
