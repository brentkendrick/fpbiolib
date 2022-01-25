import numpy as np
from .slider_formatting import (
    slider_num_formatter,
    round_up_nearest_order_mag,
    slider_marks,
)
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc


def single_float_slider_layout(
    label="default", slider_id="default", min=0, max=100, step=1, marks_option=None
):
    # Trace truncation controller / div

    max_round = round_up_nearest_order_mag(max)
    if marks_option:
        marks = slider_marks(min, max_round, 6)
    else:
        marks = {}
    layout = html.Div(
        [
            dbc.Label(label, class_name="slider-control-label"),
            html.Div(
                [
                    dcc.Slider(
                        id=slider_id,
                        value=min,
                        min=min,
                        max=max_round,
                        marks=marks,
                        step=step,
                        updatemode="mouseup",
                        # tooltip={'always_visible':False, 'placement':'bottom'},
                        className="float_slider2",
                        vertical=False,
                    ),
                    dcc.Input(
                        id=f"{slider_id}-input",
                        type="text",
                        debounce=True,
                        value=str(min),
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


def single_float_slider_callbacks(app, slider_id="default"):
    # Link trace trucation slider and input box values, seeded with initial x-min / max values
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
            float(slider_value),
            sci_sig_figs=3,
            sci_note_upper=10000,
            sci_note_lower=0.01,
        )

        # Set truncation values to those in either the input box or slider values
        input_value = (
            input_value if trigger_id == f"{slider_id}-input" else slider_str_value
        )
        slider_value = (
            slider_value if trigger_id == f"{slider_id}" else float(input_value)
        )

        # Pass width of dcc input based on number of characters in the input number
        input_style = {
            "width": f"{str(sum(c.isalnum() for c in str(input_value))*10 + 2)}px"
        }
        return input_value, slider_value, input_style


"""BELOW NOT CURRENTLY USED"""


def single_float_slider_layout_callbacks(
    app, slider_id="default", layout_id="default_layout", min=0, max=100, step=1
):
    @app.callback(
        Output(layout_id, "children"), Input("data_loading", "children"),
    )
    def slider(data_loading):
        # print("DATA LOADING IN SINGLE FLOAT SLIDER: ", data_loading)
        if data_loading == None:
            raise PreventUpdate

        max_round = round_up_nearest_order_mag(max)
        # marks = np.linspace(min, max_round, 6)
        marks = slider_marks(min, max_round, 6)
        layout = html.Div(
            [
                dcc.Slider(
                    id=slider_id,
                    value=min,
                    min=min,
                    max=max_round,
                    marks=marks,
                    step=step,
                    updatemode="mouseup",
                    # tooltip={'always_visible':False, 'placement':'bottom'},
                    className="float_slider",
                    vertical=False,
                ),
                dcc.Input(
                    id=f"{slider_id}-input",
                    type="text",
                    # debounce=True,
                    value=str(min),
                    className="slider_input",
                ),
            ],
            id=f"{slider_id}_div",
            className="slider_div",
        )

        return layout

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
            float(slider_value),
            sci_sig_figs=3,
            sci_note_upper=10000,
            sci_note_lower=0.01,
        )

        # Set truncation values to those in either the input box or slider values
        input_value = (
            input_value if trigger_id == f"{slider_id}-input" else slider_str_value
        )
        slider_value = (
            slider_value if trigger_id == f"{slider_id}" else float(input_value)
        )

        # Pass width of dcc input based on number of characters in the input number
        input_style = {
            "width": f"{str(sum(c.isalnum() for c in str(input_value))*10 + 2)}px"
        }
        return input_value, slider_value, input_style
