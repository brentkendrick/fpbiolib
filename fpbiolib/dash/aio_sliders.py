import math
import re
import uuid

import dash_bootstrap_components as dbc
import numpy as np
from dash import MATCH, Dash, Input, Output, State, callback, ctx, dcc, html
from dash.exceptions import PreventUpdate
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


# All-in-One Components should be suffixed with 'AIO'
class FloatSliderAIO(html.Div):  # html.Div will be the "parent" component
    """A set of functions that create pattern-matching callbacks of the subcomponents"""

    class ids:
        """define id functions"""

        slider = lambda aio_id: {
            "component": "FloatSliderAIO",
            "subcomponent": "slider",
            "aio_id": aio_id,
        }

        input = lambda aio_id: {
            "component": "FloatSliderAIO",
            "subcomponent": "input",
            "aio_id": aio_id,
        }

    # Make the ids class a public class
    ids = ids

    # Define the arguments of the All-in-One component
    def __init__(
        self,
        label=None,
        initial_value=None,
        slider_min=None,
        slider_max=None,
        step=None,
        marks=None,
        e_notation=None,
        cap_e=None,
        aio_id=None,
    ):
        """FloatSliderAIO is an All-in-One component that is composed
        of a parent `html.Div` with a `dcc.Store` ("`output`") that provides the
        float output ("`output`") of the slider, input `dbc.Label`
        for the FloatSlider label, `dcc.Slider` ("`slider`") and a
        `dcc.Input` ("`input`") component as children.
        The slider properties are determined by:
        - `label` - Optional label text for the slider
        - `slider_min` and `slider_max` - Range of the slider
        - `value` - initial value for the slider and input box.
        - `step`, `marks` - See https://dash.plotly.com/dash-core-components/slider for the full list.
        - `etype` - formatted as either e notation or multiplied
                    exponent notation, e.g.
                    - e notation:  3.56e+06
                    - 3.56 × 10⁺⁰⁶
        - `aio_id` - The All-in-One component ID used to generate the markdown and dropdown components's dictionary IDs.

        The All-in-One component dictionary IDs are available as
        - FloatSliderAIO.ids.slider(aio_id)
        - FloatSliderAIO.ids.input(aio_id)
        - FloatSliderAIO.ids.output(aio_id)
        """
        label = label if label else None
        initial_value = initial_value if initial_value else 0
        slider_min = slider_min if slider_min else 0
        slider_max = slider_max if slider_max else 10
        step = step if step else 0.00001
        e_notation = e_notation if e_notation else True
        cap_e = cap_e if cap_e else False

        # Allow developers to pass in their own `aio_id` if they're
        # binding their own callback to a particular component.
        if aio_id is None:
            # Otherwise use a uuid that has virtually no chance of collision.
            # Uuids are safe in dash deployments with processes
            # because this component's callbacks
            # use a stateless pattern-matching callback:
            # The actual ID does not matter as long as its unique and matches
            # the PMC `MATCH` pattern..
            aio_id = str(uuid.uuid4())

        if marks:
            marks = linear_slider_marks(
                slider_min, slider_max, e_notation=e_notation, cap_e=cap_e
            )

        initial_input_value = sci_num_format(
            float(initial_value),
            sci_sig_figs=3,
            sci_note_upper=10000,
            sci_note_lower=0.01,
        )

        # print("initial_input_value inside aio: ", initial_input_value)
        # print("initial_slider_value inside aio: ", initial_slider_value)

        # Define the component's layout
        super().__init__(
            [  # Equivalent to `html.Div([...])`
                dfc_dbc_label(label=label),
                html.Div(
                    [
                        html.Div(
                            dcc.Slider(
                                id=self.ids.slider(aio_id),
                                marks=marks,
                                value=initial_value,
                                min=slider_min,
                                max=slider_max,
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
                                "margin-left": "0px",
                            },
                        ),
                        dcc.Input(
                            id=self.ids.input(aio_id),
                            type="text",
                            debounce=True,
                            value=initial_input_value,
                            style={
                                "width": "90px",
                                "text-align": "left",
                                "font-size": "12px",
                                "height": "14px",
                                "border": "none",
                                "margin-right": "12px",
                                "margin-left": "6px",
                                "background-color": "transparent",
                            },
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
        )

    # Define this component's stateless pattern-matching callback
    # that will apply to every instance of this component.

    # Link slider and input box values, seeded with initial x-min / max values
    @callback(
        Output(ids.slider(MATCH), "value"),
        Output(
            ids.input(MATCH),
            "value",
        ),
        Input(ids.slider(MATCH), "value"),
        Input(
            ids.input(MATCH),
            "value",
        ),
        # prevent_initial_call=True,
    )
    def aio_float_slider_cb(slider_val, input_val):
        """Binds the slider and input values together"""
        trigger_id = ctx.triggered_id
        # print("trigger_id: ", trigger_id)
        # if slider_val is None:
        #     slider_val = 0
        # if input_val is None:
        #     input_val = "0"

        # Format slider values (and accompanying inputs since they are initially defined by slider values)

        if slider_val is None:
            slider_val = 0
            input_val = 0

        slider_str_value = sci_num_format(
            float(slider_val),
            sci_sig_figs=3,
            sci_note_upper=10000,
            sci_note_lower=0.001,
        )
        # Set values to those in either the input box or slider values
        input_val = (
            input_val
            if isinstance(trigger_id, list)
            and trigger_id["subcomponent"] == "input"
            else slider_str_value
        )
        # print("input_val: ", input_val)

        slider_rtn = (
            slider_val
            if isinstance(trigger_id, list)
            and trigger_id["subcomponent"] == "slider"
            else float(input_val)
        )
        # print("returning: ", float(slider_rtn), slider_rtn, input_val)
        return slider_rtn, input_val


class FloatRangeSliderAIO(html.Div):  # html.Div will be the "parent" component
    """A set of functions that create pattern-matching callbacks of the subcomponents"""

    class ids:
        """define id functions"""

        range_slider = lambda aio_id: {
            "component": "FloatRangeSliderAIO",
            "subcomponent": "range_slider",
            "aio_id": aio_id,
        }

        input_start = lambda aio_id: {
            "component": "FloatRangeSliderAIO",
            "subcomponent": "input_start",
            "aio_id": aio_id,
        }

        input_end = lambda aio_id: {
            "component": "FloatRangeSliderAIO",
            "subcomponent": "input_end",
            "aio_id": aio_id,
        }

    # Make the ids class a public class
    ids = ids

    # Define the arguments of the All-in-One component
    def __init__(
        self,
        label=None,
        min_value=None,
        max_value=None,
        slider_min=None,
        slider_max=None,
        step=None,
        marks=None,
        e_notation=None,
        cap_e=None,
        aio_id=None,
    ):
        """FloatRangeSliderAIO is an All-in-One component that is composed
        of a parent `html.Div` with a `dcc.Store` ("`output`") that provides the
        float output ("`output`") of the slider, input `dbc.Label`
        for the FloatRangeSlider label, `dcc.RangeSlider` ("`range_slider`") and a
        `dcc.Input` ("`input`") component as children.
        The slider properties are determined by:
        - `label` - Optional label text for the slider
        - `slider_min` and `slider_max` - Range of the slider
        - `value` - initial value for the slider and input box.
        - `step`, `marks` - See https://dash.plotly.com/dash-core-components/slider for the full list.
        - `etype` - formatted as either e notation or multiplied
                    exponent notation, e.g.
                    - e notation:  3.56e+06
                    - 3.56 × 10⁺⁰⁶
        - `aio_id` - The All-in-One component ID used to generate the markdown and dropdown components's dictionary IDs.

        The All-in-One component dictionary IDs are available as
        - FloatSliderAIO.ids.range_slider(aio_id)
        - FloatSliderAIO.ids.input(aio_id)
        - FloatSliderAIO.ids.output(aio_id)
        """
        min_value = min_value if min_value else 0
        max_value = max_value if max_value else 10
        slider_min = slider_min if slider_min else 0
        slider_max = slider_max if slider_max else 10
        step = step if step else 0.00001
        e_notation = e_notation if e_notation else True
        cap_e = cap_e if cap_e else False

        # Allow developers to pass in their own `aio_id` if they're
        # binding their own callback to a particular component.
        if aio_id is None:
            # Otherwise use a uuid that has virtually no chance of collision.
            # Uuids are safe in dash deployments with processes
            # because this component's callbacks
            # use a stateless pattern-matching callback:
            # The actual ID does not matter as long as its unique and matches
            # the PMC `MATCH` pattern..
            aio_id = str(uuid.uuid4())

        if marks:
            marks = linear_slider_marks(
                slider_min, slider_max, e_notation=e_notation, cap_e=cap_e
            )

        min_input = sci_num_format(
            float(min_value), e_notation=e_notation, cap_e=cap_e
        )

        max_input = sci_num_format(
            float(max_value), e_notation=e_notation, cap_e=cap_e
        )

        # Get width of dcc input based on number of characters in the input number
        input_start_width = str_px_width(min_input, font="open_sans_12pt_px")

        super().__init__(
            [  # Equivalent to `html.Div([...])`
                dfc_dbc_label(label=label),
                html.Div(
                    [
                        html.Div(
                            dcc.RangeSlider(
                                id=self.ids.range_slider(aio_id),
                                marks=marks,
                                value=[min_value, max_value],
                                min=slider_min,
                                max=slider_max,
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
                                    id=self.ids.input_start(aio_id),
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
                                html.P(
                                    "-", style={"margin": "-6px 0px 0px 0px"}
                                ),
                                dcc.Input(
                                    id=self.ids.input_end(aio_id),
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

    # Define this component's stateless pattern-matching callback
    # that will apply to every instance of this component.

    # Link slider and input box values, seeded with initial x-min / max values
    @callback(
        Output(ids.range_slider(MATCH), "value"),
        Output(
            ids.input_start(MATCH),
            "value",
        ),
        Output(
            ids.input_end(MATCH),
            "value",
        ),
        Output(
            ids.input_start(MATCH),
            "style",
        ),
        Input(ids.range_slider(MATCH), "value"),
        Input(
            ids.input_start(MATCH),
            "value",
        ),
        Input(
            ids.input_end(MATCH),
            "value",
        ),
        # prevent_initial_call=True,
    )
    def aio_float_range_slider_callback(
        slider_value, input_low_value, input_high_value
    ):
        """Binds the slider and input values together"""
        trigger_id = ctx.triggered_id
        # print("\n\ntrigger id in aio float slider: ", trigger_id)
        # print("slider_value initial aio float slider: ", slider_value)
        # print("input_low_value in aio float slider: ", input_low_value)

        # Format slider values (and accompanying inputs since they are initially defined by slider values)
        slider_low_str = sci_num_format(slider_value[0])
        slider_high_str = sci_num_format(slider_value[1])

        # Set truncation values to those in either the input box or slider values
        input_low_value = (
            input_low_value
            if isinstance(trigger_id, list)
            and trigger_id["subcomponent"] == "input_start"
            else slider_low_str
        )
        input_high_value = (
            input_high_value
            if isinstance(trigger_id, list)
            and trigger_id["subcomponent"] == "input_end"
            else slider_high_str
        )
        slider_value = (
            slider_value
            if isinstance(trigger_id, list)
            and trigger_id["subcomponent"] == "range_slider"
            else [float(input_low_value), float(input_high_value)]
        )

        # Pass width of dcc input based on number of characters in the input number
        input_start_width = str_px_width(
            input_low_value, font="open_sans_12pt_px"
        )

        input_min_style = {
            "width": input_start_width,
            "text-align": "right",
            "font-size": "12px",
            "height": "14px",
            "border": "none",
            "background-color": "transparent",
        }

        # print("slider_value: ", slider_value)
        # print("input_min_style: ", input_min_style)
        # print("input_low_value: ", input_low_value, type(input_low_value))
        # print("input_high_value: ", input_high_value, type(input_high_value))

        # print("returning output: ", output)
        # print("returning ctx.outputs: ", ctx.outputs_list)
        return (
            slider_value,
            input_low_value,
            input_high_value,
            input_min_style,
        )


class FloatLogSliderAIO(html.Div):  # html.Div will be the "parent" component
    """A set of functions that create pattern-matching callbacks of the subcomponents"""

    class ids:
        """define id functions"""

        def slider(aio_id):
            return {
                "component": "FloatLogSliderAIO",
                "subcomponent": "slider",
                "aio_id": aio_id,
            }

        def input(aio_id):
            return {
                "component": "FloatLogSliderAIO",
                "subcomponent": "input",
                "aio_id": aio_id,
            }

        def output(aio_id):
            return {
                "component": "FloatLogSliderAIO",
                "subcomponent": "output",
                "aio_id": aio_id,
            }

        def base(aio_id):
            return {
                "component": "FloatLogSliderAIO",
                "subcomponent": "base",
                "aio_id": aio_id,
            }

    # Make the ids class a public class
    ids = ids

    # Define the arguments of the All-in-One component
    def __init__(
        self,
        label=None,
        base=10,  # log base
        slider_min=-10,  # min exponent of base
        slider_max=10,
        value=None,
        step=0.00001,
        marks=None,
        e_notation=True,
        cap_e=False,
        aio_id=None,
    ):
        """FloatLogSliderAIO is an All-in-One component that is composed
        of a parent `html.Div` with a `dcc.Store` ("`output`") that provides the
        float output ("`output`") of the slider, input `dbc.Label`
        for the FloatSlider label, `dcc.Slider` ("`slider`") and a
        `dcc.Input` ("`input`") component as children.
        The slider properties are determined by:
        - `label` - Optional label text for the slider
        - `slider_min` and `slider_max` - Range of the slider
        - `value` - initial value for the slider and input box.
        - `step`, `marks` - See https://dash.plotly.com/dash-core-components/slider for the full list.
        - `etype` - formatted as either e notation or multiplied
                    exponent notation, e.g.
                    - e notation:  3.56e+06
                    - 3.56 × 10⁺⁰⁶
        - `aio_id` - The All-in-One component ID used to generate the markdown and dropdown components's dictionary IDs.

        The All-in-One component dictionary IDs are available as
        - FloatLogSliderAIO.ids.slider(aio_id)
        - FloatLogSliderAIO.ids.input(aio_id)
        - FloatLogSliderAIO.ids.output(aio_id)
        """
        # Allow developers to pass in their own `aio_id` if they're
        # binding their own callback to a particular component.
        if aio_id is None:
            # Otherwise use a uuid that has virtually no chance of collision.
            # Uuids are safe in dash deployments with processes
            # because this component's callbacks
            # use a stateless pattern-matching callback:
            # The actual ID does not matter as long as its unique and matches
            # the PMC `MATCH` pattern..
            aio_id = str(uuid.uuid4())

        if slider_min % 2 != 0:
            slider_min = math.floor(slider_min)

        if slider_max % 2 != 0:
            slider_max = math.ceil(slider_max)
        num_intervals = slider_max - slider_min
        for i in range(8, 2, -1):
            # print("i: ", i)
            # print("num_intervals: ", num_intervals)
            # print("num_intervals div i : ", num_intervals % i)
            if num_intervals % i == 0:
                log_intervals = np.linspace(slider_min, slider_max, i + 1)

                break
            else:
                log_intervals = np.linspace(slider_min, slider_max, 7)
        if marks:
            marks = log_slider_marks(
                log_intervals,
                base=base,
                round_to_ord_mag=True,
                e_notation=e_notation,
                cap_e=cap_e,
            )

        # print("log marks: ", marks)
        min_interval = log_intervals[0]
        max_interval = log_intervals[-1]
        # print("min_interval: ", min_interval)
        # print("max_interval: ", max_interval)
        # print("value: ", value)
        if value is None:
            value = sci_num_format(
                float(base**max_interval),
                sci_sig_figs=3,
                sci_note_upper=10000,
                sci_note_lower=0.01,
            )
        else:
            value = sci_num_format(
                float(base**value),
                sci_sig_figs=3,
                sci_note_upper=10000,
                sci_note_lower=0.01,
            )

        # Define the component's layout

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

        super().__init__(
            [  # Equivalent to `html.Div([...])`
                dcc.Store(id=self.ids.output(aio_id)),
                dcc.Store(id=self.ids.base(aio_id)),
                label_div,
                html.Div(
                    [
                        html.Div(
                            dcc.Slider(
                                id=self.ids.slider(aio_id),
                                marks=marks,
                                value=max_interval,
                                min=min_interval,  # exponent of base
                                max=max_interval,  # exponent of base
                                step=step,
                                dots=False,
                                vertical=False,
                                # updatemode="mouseup",
                            ),
                            style={
                                "width": "100%",
                                "margin-right": "-21px",  # override dcc.Slider padding
                                "margin-left": "0px",
                            },
                        ),
                        dcc.Input(
                            id=self.ids.input(aio_id),
                            type="text",
                            debounce=True,
                            value=value,
                            style={
                                "width": "90px",
                                "text-align": "left",
                                "font-size": "12px",
                                "height": "14px",
                                "border": "none",
                                "margin-right": "12px",
                                "margin-left": "6px",
                                "background-color": "transparent",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "justify-content": "left",
                        "width": "106%",
                        "margin-top": "2.5px",
                        "margin-bottom": "-8px",
                    },
                ),
            ],
            style={"display": "block"},
        )

    # Define this component's stateless pattern-matching callback
    # that will apply to every instance of this component.

    # Link slider and input box values, seeded with initial x-min / max values
    @callback(
        Output(ids.output(MATCH), "data"),
        Output(
            ids.input(MATCH),
            "value",
        ),
        Output(ids.slider(MATCH), "value"),
        Input(ids.slider(MATCH), "value"),
        Input(
            ids.input(MATCH),
            "value",
        ),
        Input(ids.base(MATCH), "data"),
        prevent_initial_call=True,
    )
    def float_log_slider_callback(slider_value, input_value, base):
        """Binds the slider and input values together"""
        if base is None:
            base = 10
        trigger_id = ctx.triggered_id
        if trigger_id == None:
            raise PreventUpdate

        # Format slider values (and accompanying inputs since they are initially defined by slider values)
        slider_str_value = sci_num_format(
            float(base ** (slider_value)),
            sci_sig_figs=3,
            sci_note_upper=10000,
            sci_note_lower=0.01,
        )

        # Set values to those in either the input box or slider values
        input_value = (
            input_value
            if trigger_id["subcomponent"] == "input"
            else slider_str_value
        )

        slider_value = (
            slider_value
            if trigger_id["subcomponent"] == "slider"
            else math.log(float(input_value), base)
        )

        return float(input_value), input_value, slider_value


class FloatLogRangeSliderAIO(
    html.Div
):  # html.Div will be the "parent" component
    """A set of functions that create pattern-matching callbacks of the subcomponents"""

    class ids:
        """define id functions"""

        def range_slider(aio_id):
            return {
                "component": "FloatLogRangeSliderAIO",
                "subcomponent": "range_slider",
                "aio_id": aio_id,
            }

        def input_start(aio_id):
            return {
                "component": "FloatLogRangeSliderAIO",
                "subcomponent": "input_start",
                "aio_id": aio_id,
            }

        def input_end(aio_id):
            return {
                "component": "FloatLogRangeSliderAIO",
                "subcomponent": "input_end",
                "aio_id": aio_id,
            }

        def output(aio_id):
            return {
                "component": "FloatLogRangeSliderAIO",
                "subcomponent": "output",
                "aio_id": aio_id,
            }

        def base(aio_id):
            return {
                "component": "FloatLogRangeSliderAIO",
                "subcomponent": "base",
                "aio_id": aio_id,
            }

    # Make the ids class a public class
    ids = ids

    # Define the arguments of the All-in-One component
    def __init__(
        self,
        label=None,
        base=10,
        slider_min=-10,
        slider_max=10,
        min_value=None,
        max_value=None,
        step=0.00001,
        marks=None,
        e_notation=True,
        cap_e=False,
        aio_id=None,
    ):
        """FloatLogRangeSliderAIO is an All-in-One component that is composed
        of a parent `html.Div` with a `dcc.Store` ("`output`") that provides the
        float output ("`output`") of the slider, input `dbc.Label`
        for the FloatRangeSlider label, `dcc.RangeSlider` ("`range_slider`") and a
        `dcc.Input` ("`input`") component as children.
        The slider properties are determined by:
        - `label` - Optional label text for the slider
        - `slider_min` and `slider_max` - Range of the slider
        - `value` - initial value for the slider and input box.
        - `step`, `marks` - See https://dash.plotly.com/dash-core-components/slider for the full list.
        - `etype` - formatted as either e notation or multiplied
                    exponent notation, e.g.
                    - e notation:  3.56e+06
                    - 3.56 × 10⁺⁰⁶
        - `aio_id` - The All-in-One component ID used to generate the markdown and dropdown components's dictionary IDs.

        The All-in-One component dictionary IDs are available as
        - FloatSliderAIO.ids.range_slider(aio_id)
        - FloatSliderAIO.ids.input(aio_id)
        - FloatSliderAIO.ids.output(aio_id)
        """
        # Allow developers to pass in their own `aio_id` if they're
        # binding their own callback to a particular component.
        if aio_id is None:
            # Otherwise use a uuid that has virtually no chance of collision.
            # Uuids are safe in dash deployments with processes
            # because this component's callbacks
            # use a stateless pattern-matching callback:
            # The actual ID does not matter as long as its unique and matches
            # the PMC `MATCH` pattern..
            aio_id = str(uuid.uuid4())

        if slider_min % 2 != 0:
            slider_min = math.floor(slider_min)

        if slider_max % 2 != 0:
            slider_max = math.ceil(slider_max)
        num_intervals = slider_max - slider_min
        for i in range(8, 2, -1):
            # print("i: ", i)
            # print("num_intervals: ", num_intervals)
            # print("num_intervals div i : ", num_intervals % i)
            if num_intervals % i == 0:
                log_intervals = np.linspace(slider_min, slider_max, i + 1)

                break
            else:
                log_intervals = np.linspace(slider_min, slider_max, 7)
        if marks:
            marks = log_slider_marks(
                log_intervals,
                base=base,
                round_to_ord_mag=True,
                e_notation=e_notation,
                cap_e=cap_e,
            )

        # print("log marks: ", marks)
        min_interval = log_intervals[0]
        max_interval = log_intervals[-1]
        # print("min_interval: ", min_interval)
        # print("max_interval: ", max_interval)
        # print("value: ", value)
        # print("id: ", f"{id}-slider")
        if min_value is None:
            min_value = sci_num_format(
                float(base**min_interval),
                sci_sig_figs=3,
                sci_note_upper=10000,
                sci_note_lower=0.01,
            )
        else:
            min_value = sci_num_format(
                float(base**min_value),
                sci_sig_figs=3,
                sci_note_upper=10000,
                sci_note_lower=0.01,
            )

        if max_value is None:
            max_value = sci_num_format(
                float(base**max_interval),
                sci_sig_figs=3,
                sci_note_upper=10000,
                sci_note_lower=0.01,
            )
        else:
            max_value = sci_num_format(
                float(base**max_value),
                sci_sig_figs=3,
                sci_note_upper=10000,
                sci_note_lower=0.01,
            )

        # Pass width of dcc input based on number of characters in the input number
        input_start_width = (
            f"{str(sum(c.isalnum() for c in str(min_value))*10 + 2)}px"
        )
        if input_start_width == "12px":  # need min of 23px
            input_start_width = "23px"

        input_end_width = (
            f"{str(sum(c.isalnum() for c in str(max_value))*10 + 2)}px"
        )
        if input_end_width == "12px":  # need min of 23px
            input_end_width = "23px"

        # Define the component's layout

        super().__init__(
            [  # Equivalent to `html.Div([...])`
                dcc.Store(id=self.ids.output(aio_id)),
                dcc.Store(id=self.ids.base(aio_id)),
                dfc_dbc_label(label=label),
                html.Div(
                    [
                        html.Div(
                            dcc.RangeSlider(
                                id=self.ids.range_slider(aio_id),
                                marks=marks,
                                value=[min_interval, max_interval],
                                min=min_interval,  # exponent of base
                                max=max_interval,  # exponent of base
                                step=step,
                                dots=False,
                                vertical=False,
                                updatemode="mouseup",
                            ),
                            style={
                                "width": "100%",
                                "margin-right": "-21px",  # override dcc.Slider padding
                                "margin-left": "0px",
                            },
                        ),
                        dcc.Input(
                            id=self.ids.input_start(aio_id),
                            type="text",
                            debounce=True,
                            value=min_value,
                            style={
                                "width": input_start_width,
                                "text-align": "right",
                                "font-size": "12px",
                                "height": "14px",
                                "border": "none",
                                "background-color": "transparent",
                            },
                        ),
                        html.P("–", style={"margin": "-6px 0px 0px 0px"}),
                        dcc.Input(
                            id=self.ids.input_end(aio_id),
                            type="text",
                            debounce=True,
                            value=max_value,
                            style={
                                "width": input_end_width,
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
                        "justify-content": "left",
                        "width": "103%",
                        "margin-top": "2.5px",
                        "margin-bottom": "-8px",
                    },
                ),
            ],
            style={"display": "block"},
        )

    # Define this component's stateless pattern-matching callback
    # that will apply to every instance of this component.

    # Link slider and input box values, seeded with initial x-min / max values
    @callback(
        Output(ids.output(MATCH), "data"),
        Output(ids.range_slider(MATCH), "value"),
        Output(
            ids.input_start(MATCH),
            "value",
        ),
        Output(
            ids.input_end(MATCH),
            "value",
        ),
        Output(
            ids.input_start(MATCH),
            "style",
        ),
        Output(
            ids.input_end(MATCH),
            "style",
        ),
        Input(ids.range_slider(MATCH), "value"),
        Input(
            ids.input_start(MATCH),
            "value",
        ),
        Input(
            ids.input_end(MATCH),
            "value",
        ),
        Input(ids.base(MATCH), "data"),
        prevent_initial_call=True,
    )
    def float_log_range_slider_callback(slider, start, end, base):
        """Binds the slider and input values together"""
        trigger_id = ctx.triggered_id
        if base is None:
            base = 10
        # Format slider values (and accompanying inputs since they are initially defined by slider values)
        slider_0_str = sci_num_format(
            float(base ** (slider[0])),
            sci_sig_figs=3,
            sci_note_upper=10000,
            sci_note_lower=0.01,
        )
        slider_1_str = sci_num_format(
            (base ** (slider[1])),
            sci_sig_figs=3,
            sci_note_upper=10000,
            sci_note_lower=0.01,
        )

        # Set truncation values to those in either the input box or slider values
        slider_start = (
            start
            if trigger_id["subcomponent"] == "input_start"
            else slider_0_str
        )
        slider_end = (
            end if trigger_id["subcomponent"] == "input_end" else slider_1_str
        )

        slider_value = (
            slider
            if trigger_id["subcomponent"] == "range_slider"
            else [
                math.log(float(slider_start), base),
                math.log(float(slider_end), base),
            ]
        )

        # Pass width of dcc input based on number of characters in the input number
        input_start_width = (
            f"{str(sum(c.isalnum() for c in str(slider_start))*10 + 2)}px"
        )
        if input_start_width == "12px":  # need min of 23px
            input_start_width = "23px"

        input_end_width = (
            f"{str(sum(c.isalnum() for c in str(slider_end))*10 + 2)}px"
        )
        if input_end_width == "12px":  # need min of 23px
            input_end_width = "23px"

        style_start = {
            "width": input_start_width,
            "text-align": "right",
            "font-size": "12px",
            "height": "14px",
            "border": "none",
            "background-color": "transparent",
        }

        style_end = {
            "width": input_end_width,
            "text-align": "left",
            "font-size": "12px",
            "height": "14px",
            "border": "none",
            "margin-right": "12px",
            "background-color": "transparent",
        }

        converted_output = [
            float(base ** (slider_value[0])),
            float(base ** (slider_value[1])),
        ]

        return (
            converted_output,
            slider_value,
            slider_start,
            slider_end,
            style_start,
            style_end,
        )
