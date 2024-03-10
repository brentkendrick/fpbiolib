import math
import re
import uuid

import dash_bootstrap_components as dbc
import numpy as np
from dash import (
    MATCH,
    Dash,
    Input,
    Output,
    State,
    callback,
    clientside_callback,
    ctx,
    dcc,
    html,
)
from dash.exceptions import PreventUpdate

clientside_callback

# from dash_fpbio_components.ids import ids

from fpbiolib import (
    dec_notation,
    interval_range,
    process_str_list,
    sci_notation,
    str_px_width,
)


def dfc_dbc_label(label: str):
    """Takes in an optional label string and
    formats it for the custom dfc components
    """
    label_div = None
    if label:
        label_div = dbc.Label(
            label,
            style={
                "font-size": "14px",
                "margin-bottom": "-5px",
                "margin-left": "7px",
                "color": " rgb(17, 80, 143)",
            },
        )
    return label_div


def sci_num_format(
    num: float,
    sci_sig_figs: int = 3,
    sci_note_upper: float = 10000,
    sci_note_lower: float = 0.01,
    e_notation: bool = True,
    cap_e: bool = False,
) -> str:
    """Formats numbers above and below a specified
    limit to a string in scientific or decimal notation.
    """
    if num == 0:
        return "0"
    elif abs(num) >= sci_note_upper or abs(num) < sci_note_lower:
        return sci_notation(
            num, sci_sig_figs, e_notation=e_notation, cap_e=cap_e
        )
    else:
        return dec_notation(num, sci_note_upper).rstrip("0").rstrip(".")


def linear_slider_marks(x_min, x_max, e_notation=True, cap_e=False) -> dict:
    """Generate linearly spaced slider value
    dictionary for generating slider marks.
    """
    intervals = interval_range(x_min, x_max)
    marks = {
        i: sci_num_format(
            i, sci_note_lower=0.001, e_notation=e_notation, cap_e=cap_e
        )
        for i in intervals
    }
    return {int(k) if k.is_integer() else k: v for k, v in marks.items()}


def log_slider_marks(
    log_intervals, base=10, round_to_ord_mag=True, e_notation=True, cap_e=False
) -> dict:
    """Generate log spaced slider value
    dictionary for generating slider marks.
    """
    if round_to_ord_mag:
        # Convert the intervals to sorted, unique list of integers
        log_intervals = np.unique(np.rint(log_intervals))
        # for some reason, mark values that are -2, -1, 1, 2, etc must be explicitely converted to integers to display in the slider
        marks = {
            int(
                k
            ): f"{sci_num_format(base**k, sci_sig_figs=0, sci_note_upper=10000, sci_note_lower=0.001, e_notation=e_notation, cap_e=cap_e)}"
            for k in log_intervals
        }

    else:
        marks = {(i): f"{base**i:#.3g}" for i in log_intervals[1:]}
        marks = {int(k) if k.is_integer() else k: v for k, v in marks.items()}
    return marks


# FLOAT_SLIDER FUNCTIONS
def float_slider_layout(
    id="f-s",
    label=None,
    value=0,
    slider_min=0,
    slider_max=10,
    step=0.00001,
    marks=None,
    e_notation=True,
    cap_e=False,
):
    """One of two interacting functions, both necessary for the
    slider to function properly.  This fxn provides the layout div
    and component ids for the slider/input combo.  The other function,
    float_slider_callbacks provides the interactivity between the
    slider and the input components.

    The slider properties are determined by:
    - `label` - Optional label text for the slider
    - `slider_min` and `slider_max` - Range of the slider
    - `step`, `marks` - See https://dash.plotly.com/dash-core-components/slider for the full list.
    - `e_notation and cap_e` - formatted as either e notation or multiplied
                exponent notation, e.g.
                - e notation:  3.56e+06
                - cap_e: 3.56E+06
                - scientific notation: 3.56 × 10⁺⁰⁶
    - `comp_id` - The All-in-One component ID used to generate the markdown and dropdown
    """

    if marks:
        marks = linear_slider_marks(
            slider_min, slider_max, e_notation=e_notation, cap_e=cap_e
        )

    input_value = sci_num_format(
        float(value),
        sci_sig_figs=3,
        sci_note_upper=10000,
        sci_note_lower=0.01,
    )

    label_div = None
    if label:
        label_div = dbc.Label(
            label,
            style={
                "font-size": "14px",
                "margin-bottom": "-5px",
                # "margin-top": "12px",
                "margin-left": "7px",
                "color": " rgb(17, 80, 143)",
            },
        )

    # Define the component's layout
    return html.Div(
        [
            dcc.Store(id=id),  # This will contain the primary value output
            label_div,
            html.Div(
                [
                    html.Div(
                        dcc.Slider(
                            id=f"{id}-slider",
                            marks=marks,
                            value=value,  # float
                            min=slider_min,  # float
                            max=slider_max,  # float
                            step=step,
                            dots=False,
                            vertical=False,
                            tooltip={
                                "always_visible": False,
                                "placement": "bottom",
                            },
                            # updatemode="mouseup",
                        ),
                        style={
                            "width": "100%",
                            "margin-right": "-21px",  # override dcc.Slider padding
                            "margin-left": "-0px",
                        },
                    ),
                    dcc.Input(
                        id=f"{id}-input",
                        type="text",
                        debounce=True,
                        value=input_value,  # str
                        style={
                            "width": "70px",
                            "text-align": "left",
                            "font-size": "12px",
                            "height": "14px",
                            "border": "none",
                            "margin-right": "12px",
                            "margin-left": "6px",
                            "background-color": "transparent",
                        },
                        # className="slider_input",
                    ),
                ],
                style={
                    "display": "flex",
                    "justify-content": "left",
                    "width": "106%",
                    "margin-top": "2.5px",
                    "margin-bottom": "-3px",
                },
            ),
        ],
        style={"display": "block"},
        # style={"width": "100%", "margin-bottom": "-8px"},
    )


def float_slider_callbacks(app, id):
    @app.callback(
        Output(id, "data"),
        Output(f"{id}-slider", "value"),
        Output(f"{id}-input", "value"),
        Input(f"{id}-slider", "value"),
        Input(f"{id}-input", "value"),
        # prevent_initial_call=True,
    )
    def float_slider_callback(slider_value, input_value):
        """Binds the slider and input_field values together"""
        trigger_id = ctx.triggered_id
        # print("\nTriggered ID: ", trigger_id)

        # Format slider values (and accompanying inputs since they are initially defined by slider values)
        slider_str_value = sci_num_format(
            float(slider_value),
            sci_sig_figs=3,
            sci_note_upper=10000,
            sci_note_lower=0.001,
        )

        # Set values to those in either the input_field box or slider values
        input_value = (
            input_value if trigger_id == f"{id}-input" else slider_str_value
        )

        slider_value = (
            slider_value
            if trigger_id == f"{id}-slider"
            else float(input_value)
        )

        return float(input_value), slider_value, input_value


# MERGE ATTEMPT


def float_slider_component(
    # app: Dash,
    id="f-s",
    label=None,
    value=0,
    slider_min=0,
    slider_max=10,
    step=0.00001,
    marks=None,
    e_notation=True,
    cap_e=False,
):
    """One of two interacting functions, both necessary for the
    slider to function properly.  This fxn provides the layout div
    and component ids for the slider/input combo.  The other function,
    float_slider_callbacks provides the interactivity between the
    slider and the input components.

    The slider properties are determined by:
    - `label` - Optional label text for the slider
    - `slider_min` and `slider_max` - Range of the slider
    - `step`, `marks` - See https://dash.plotly.com/dash-core-components/slider for the full list.
    - `e_notation and cap_e` - formatted as either e notation or multiplied
                exponent notation, e.g.
                - e notation:  3.56e+06
                - cap_e: 3.56E+06
                - scientific notation: 3.56 × 10⁺⁰⁶
    - `comp_id` - The All-in-One component ID used to generate the markdown and dropdown
    """

    if marks:
        marks = linear_slider_marks(
            slider_min, slider_max, e_notation=e_notation, cap_e=cap_e
        )

    input_value = sci_num_format(
        float(value),
        sci_sig_figs=3,
        sci_note_upper=10000,
        sci_note_lower=0.01,
    )

    label_div = None
    if label:
        label_div = dbc.Label(
            label,
            style={
                "font-size": "14px",
                "margin-bottom": "-5px",
                # "margin-top": "12px",
                "margin-left": "7px",
                "color": " rgb(17, 80, 143)",
            },
        )

    # Define the component's layout
    layout = html.Div(
        [
            dcc.Store(id=id),  # This will contain the primary value output
            label_div,
            html.Div(
                [
                    html.Div(
                        dcc.Slider(
                            id=f"{id}-slider",
                            marks=marks,
                            value=value,  # float
                            min=slider_min,  # float
                            max=slider_max,  # float
                            step=step,
                            dots=False,
                            vertical=False,
                            tooltip={
                                "always_visible": False,
                                "placement": "bottom",
                            },
                            # updatemode="mouseup",
                        ),
                        style={
                            "width": "100%",
                            "margin-right": "-21px",  # override dcc.Slider padding
                            "margin-left": "-8px",
                        },
                    ),
                    dcc.Input(
                        id=f"{id}-input",
                        type="text",
                        debounce=True,
                        value=input_value,  # str
                        style={
                            "width": "70px",
                            "text-align": "left",
                            "font-size": "12px",
                            "height": "14px",
                            "border": "none",
                            "margin-right": "12px",
                            "margin-left": "6px",
                            "background-color": "transparent",
                        },
                        # className="slider_input",
                    ),
                ],
                style={
                    "display": "flex",
                    "justify-content": "left",
                    "width": "103%",
                    "margin-top": "2.5px",
                    "margin-bottom": "-12px",
                },
            ),
        ],
        # style={"display": "block"},
        style={"width": "100%", "margin-bottom": "-8px"},
    )

    @callback(
        Output(id, "data"),
        Output(f"{id}-slider", "value"),
        Output(f"{id}-input", "value"),
        Input(f"{id}-slider", "value"),
        Input(f"{id}-input", "value"),
        prevent_initial_call=True,
    )
    def float_slider_callback(slider_value, input_value):
        """Binds the slider and input_field values together"""
        trigger_id = ctx.triggered_id
        print("\nTriggered ID: ", trigger_id)
        print("slider_value: ", slider_value)
        print("input_value: ", input_value)
        if input_value is None:
            input_value = 0

        # Format slider values (and accompanying inputs since they are initially defined by slider values)
        slider_str_value = sci_num_format(
            float(slider_value),
            sci_sig_figs=3,
            sci_note_upper=10000,
            sci_note_lower=0.001,
        )

        # Set values to those in either the input_field box or slider values
        input_value = (
            input_value if trigger_id == f"{id}-input" else slider_str_value
        )

        slider_value = (
            slider_value
            if trigger_id == f"{id}-slider"
            else float(input_value)
        )
        print("slider_value: ", slider_value)
        print("input_value: ", input_value)

        return float(input_value), slider_value, input_value

    return layout


# FLOAT_RANGE_SLIDER FUNCTIONS
def float_range_slider_layout(
    id="f-r-s",
    label=None,
    min_value=0,
    max_value=10,
    slider_min=0,
    slider_max=10,
    step=0.00001,
    marks=None,
    e_notation=True,
    cap_e=False,
):
    """One of two interacting functions, both necessary for the
    slider to function properly.  This fxn provides the layout div
    and component ids for the slider/input combo.  The other function,
    float_slider_callbacks provides the interactivity between the
    slider and the input components.

    The slider properties are determined by:
    - `label` - Optional label text for the slider
    - `slider_min` and `slider_max` - Range of the slider
    - `step`, `marks` - See https://dash.plotly.com/dash-core-components/slider for the full list.
    - `e_notation and cap_e` - formatted as either e notation or multiplied
                exponent notation, e.g.
                - e notation:  3.56e+06
                - cap_e: 3.56E+06
                - scientific notation: 3.56 × 10⁺⁰⁶
    - `comp_id` - The All-in-One component ID used to generate the markdown and dropdown
    """

    if marks:
        marks = linear_slider_marks(
            slider_min, slider_max, e_notation=e_notation, cap_e=cap_e
        )

    min_input = sci_num_format(
        float(min_value),
        sci_sig_figs=3,
        sci_note_upper=10000,
        sci_note_lower=0.01,
    )

    max_input = sci_num_format(
        float(max_value),
        sci_sig_figs=3,
        sci_note_upper=10000,
        sci_note_lower=0.01,
    )

    # Get width of dcc input based on number of characters in the input number
    input_start_width = str_px_width(min_input, font="open_sans_12pt_px")

    label_div = None
    if label:
        label_div = dbc.Label(
            label,
            style={
                "font-size": "14px",
                "margin-bottom": "-5px",
                # "margin-top": "12px",
                "margin-left": "7px",
                "color": " rgb(17, 80, 143)",
            },
        )

    # Define the component's layout
    return html.Div(
        [
            dcc.Store(id=id),  # This will contain the primary value output
            label_div,
            html.Div(
                [
                    html.Div(
                        dcc.RangeSlider(
                            id=f"{id}-slider",
                            # marks=marks,
                            # value=[min_value, max_value],
                            # min=slider_min,
                            # max=slider_max,
                            step=step,
                            dots=False,
                            vertical=False,
                            tooltip={
                                "always_visible": False,
                                "placement": "bottom",
                            },
                            updatemode="mouseup",
                        ),
                        style={
                            "width": "75%",
                            "margin-right": "-22px",  # override dcc.Slider padding
                            "margin-left": "-8px",
                        },
                    ),
                    html.Div(
                        [
                            dcc.Input(
                                id=f"{id}-input-min",
                                type="text",
                                debounce=True,
                                value=min_input,
                                style={
                                    "width": input_start_width,
                                    "text-align": "right",
                                    "margin-left": "4px",
                                    "font-size": "12px",
                                    "height": "14px",
                                    "border": "none",
                                    "background-color": "transparent",
                                },
                            ),
                            html.P("–", style={"margin": "-6px 0px 0px 0px"}),
                            dcc.Input(
                                id=f"{id}-input-max",
                                type="text",
                                debounce=True,
                                value=max_input,
                                style={
                                    "width": "70px",
                                    "text-align": "left",
                                    "font-size": "12px",
                                    "height": "14px",
                                    "border": "none",
                                    "margin-right": "12px",
                                    "background-color": "transparent",
                                },
                            ),
                        ],
                        style={
                            "display": "flex",
                            # "width": "50%",
                            # "margin-right": "-26px",  # override dcc.Slider padding
                            "margin-left": "4px",
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "justify-content": "left",
                    "width": "100%",
                    "margin-top": "2.5px",
                    "margin-bottom": "-12px",
                },
            ),
        ],
        style={"width": "100%", "margin-bottom": "-8px"},
    )


def float_range_slider_callbacks(app, id):
    @app.callback(
        Output(f"{id}-slider", "min"),
        Output(f"{id}-slider", "max"),
        Output(f"{id}-slider", "marks"),
        Input("truncate-upload-params", "data"),
        Input(ids.initial_x_min_id.id(), "data"),
        State(ids.initial_x_max_id.id(), "data"),
        prevent_initial_call=True,
    )
    def init_slider_vals(uploaded_values, x_min, x_max):
        min_value = x_min
        max_value = x_max
        marks = True
        if x_min is None:
            marks = None
            min_value = 0
            max_value = 10
            x_min = 0
            x_max = 10

        if ctx.triggered_id == "truncate-upload-params" and uploaded_values:
            min_value = x_min
            max_value = x_max

            uploaded_values = process_str_list(uploaded_values)

            if x_max > min(uploaded_values) > x_min:
                min_value = min(uploaded_values)
            if x_min < max(uploaded_values) < x_max:
                max_value = max(uploaded_values)
        print("min_value: ", min_value)
        print("max_value: ", max_value)
        print("marks: ", marks)
        return min_value, max_value, marks

    @app.callback(
        Output(id, "data"),
        Output(f"{id}-slider", "value"),
        Output(f"{id}-input-min", "value"),
        Output(f"{id}-input-max", "value"),
        Output(f"{id}-input-min", "style"),
        Input(f"{id}-slider", "value"),
        Input(f"{id}-input-min", "value"),
        Input(f"{id}-input-max", "value"),
        prevent_initial_call=True,
    )
    def float_range_slider_callback(slider, input_min_value, input_max_value):
        """Binds the slider and input values together"""
        trigger_id = ctx.triggered_id

        # Format slider values (and accompanying inputs since they are initially defined by slider values)
        slider_min_str = sci_num_format(
            float(slider[0]),
            sci_sig_figs=3,
            sci_note_upper=10000,
            sci_note_lower=0.01,
        )
        slider_max_str = sci_num_format(
            float(slider[1]),
            sci_sig_figs=3,
            sci_note_upper=10000,
            sci_note_lower=0.01,
        )

        # Set truncation values to those in either the input box or slider values
        slider_min = (
            input_min_value
            if trigger_id == f"{id}-input-min"
            else slider_min_str
        )
        slider_max = (
            input_max_value
            if trigger_id == f"{id}-input-max"
            else slider_max_str
        )
        slider_value = (
            slider
            if trigger_id == f"{id}-slider"
            else [float(slider_min), float(slider_max)]
        )

        # Pass width of dcc input based on number of characters in the input number
        input_min_width = str_px_width(slider_min, font="open_sans_12pt_px")

        input_min_style = {
            "width": input_min_width,
            "text-align": "right",
            "font-size": "12px",
            "height": "14px",
            "border": "none",
            "background-color": "transparent",
        }

        output = [
            float(slider_value[0]),
            float(slider_value[1]),
        ]

        return (
            output,
            slider_value,
            slider_min,
            slider_max,
            input_min_style,
        )


# Example range slider with label and fixed width
#     truncation_slider_input_layout = html.Div(
#     [
#         # dfc_dbc_label(label="Truncate traces"),
#         html.Div(
#             [
#                 html.Div(
#                     dcc.RangeSlider(
#                         id=ids.truncate_slider.id(),
#                         marks=None,
#                         value=[1, 10],
#                         min=1,
#                         max=10,
#                         step=0.00001,
#                         dots=False,
#                         vertical=False,
#                         tooltip={
#                             "always_visible": False,
#                             "placement": "bottom",
#                         },
#                         updatemode="mouseup",
#                     ),
#                     className="slider-slider_input_sync",
#                     style={"flex": "0 0 280px"},  # fixes flex width
#                 ),
#                 html.Div(
#                     [
#                         dcc.Input(
#                             id=ids.truncate_input1.id(),
#                             type="text",
#                             debounce=True,
#                             value="1",
#                             className="input1-slider_input_sync",
#                         ),
#                         html.P("-", style={"margin": "-6px 0px 0px 0px"}),
#                         dcc.Input(
#                             id=ids.truncate_input2.id(),
#                             type="text",
#                             debounce=True,
#                             value="10",
#                             className="input2-slider_input_sync",
#                         ),
#                     ],
#                     className="range-slider-input1-input2-div",
#                 ),
#             ],
#             className="slider_input_sync",
#         ),
#     ],
# )


# def render():
#     """Truncation slider and input component
#     layout and related callbacks. Relies on
#     other callback inputs, including:
#      - xmin and xmax from the initial dataframe
#     containing all x, y data (which is created
#     when the user uploads a file into the app.)
#      - trace truncation values uploaded from a
#     parameters .csv file.
#      - truncation activation switch
#      - truncation collapse modal
#     """

#     """When truncate button is pressed, collapse opens"""

#     @callback(
#         Output(ids.truncate_collapse.id(), "is_open"),
#         Input(ids.truncate_button.id(), "n_clicks"),
#         State(ids.truncate_collapse.id(), "is_open"),
#     )
#     def truncate_collapse_modal_ctl(n, is_open):
#         if n:
#             return not is_open
#         return is_open

#     @callback(
#         Output(ids.truncate_slider_output.id(), "data"),
#         Output(ids.truncate_input1.id(), "value"),
#         Output(ids.truncate_input1.id(), "style"),
#         Output(ids.truncate_input2.id(), "value"),
#         Output(ids.truncate_slider.id(), "value"),
#         Output(ids.truncate_slider.id(), "marks"),
#         Output(ids.truncate_slider.id(), "min"),
#         Output(ids.truncate_slider.id(), "max"),
#         Input(ids.truncate_input1.id(), "value"),
#         Input(ids.truncate_input2.id(), "value"),
#         Input(ids.truncate_slider.id(), "value"),
#         Input(ids.truncate_upload_id.id(), "data"),
#         Input(ids.initial_x_min_id.id(), "data"),
#         State(ids.initial_x_max_id.id(), "data"),
#         State(ids.truncate_slider_output.id(), "data"),
#         prevent_initial_call=True,
#     )
#     def truncate_slider_ctl(
#         input1, input2, slider, upload_params, x_min, x_max, output_store
#     ):
#         trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]  # returns string

#         # Slider min and max range based on initial df x-range
#         if "initial_x_min" in trigger_id:
#             input1 = str(x_min)
#             input2 = str(x_max)
#             slider_min = float(x_min)
#             slider_max = float(x_max)
#             slider = [slider_min, slider_max]
#             marks = linear_slider_marks(
#                 slider_min, slider_max, e_notation=None, cap_e=None
#             )

#         # No need to update slider min / max after set by initial load
#         else:
#             slider_min = no_update
#             slider_max = no_update
#             marks = no_update

#         # Handle uploaded parameter truncation range if it exists
#         if (
#             trigger_id is not None
#             and "truncate_upload" in trigger_id
#             and upload_params is not None
#         ):
#             upload_params = process_str_list(upload_params)

#             if x_max > min(upload_params) > x_min:
#                 slider[0] = min(upload_params)
#             if x_min < max(upload_params) < x_max:
#                 slider[1] = max(upload_params)

#             input1 = str(slider[0])
#             input2 = str(slider[1])

#         # Format input strings with desired sci notation
#         slider_low_str = sci_num_format(float(slider[0]), e_notation=None, cap_e=None)
#         slider_high_str = sci_num_format(float(slider[1]), e_notation=None, cap_e=None)

#         # Set truncation values to those in either the input box or slider values
#         input1 = input1 if "truncate_input1" in trigger_id else slider_low_str
#         input2 = input2 if "truncate_input2" in trigger_id else slider_high_str

#         slider = (
#             slider
#             if "truncate_slider" in trigger_id
#             else [float(input1), float(input2)]
#         )

#         # Get style width of dcc input based on number of characters in the input number
#         input1_width = str_px_width(input1, font="open_sans_12pt_px")

#         input1_style = {"width": input1_width}

#         output = [
#             float(slider[0]),
#             float(slider[1]),
#         ]

#         return (
#             output,
#             input1,
#             input1_style,
#             input2,
#             slider,
#             marks,
#             slider_min,
#             slider_max,
#         )

#     return html.Div(
#         [
#             main_switch.render(),
#             dcc.Store(id=ids.truncate_slider_output.id()),
#             dbc.Collapse(
#                 [
#                     dbc.Tooltip(
#                         "x-value limits (drag slider ends or enter left/right limits in input fields)",
#                         target=ids.truncate_button.id(),
#                     ),
#                     truncation_slider_input_layout,
#                 ],
#                 id=ids.truncate_collapse.id(),
#                 is_open=False,
#             ),
#         ]
#     )


# Example working clientside callback for float_range_slider
# to set input width style
# clientside_callback(
#     """
#     function getTextWidth(text) {
#         // uses a cached canvas if available
#         var canvas = getTextWidth.canvas || (getTextWidth.canvas = document.createElement("canvas"));
#         var context = canvas.getContext("2d");
#         // get the full font style property
#         // set the font attr for the canvas text
#         context.font = "12pt Open Sans";
#         var textMeasurement = context.measureText(text);
#         var width = textMeasurement.width + 0;
#         return {
#                         "width": width,
#                         "text-align": "left",
#                         "font-size": "12px",
#                         "height": "14px",
#                         "border": "none",
#                         "background-color": "transparent",
#                     }
#         }
#     """,
#     Output(f"{id}-input-min", "style"),
#     Input(f"{id}-input-min", "value"),
# )
