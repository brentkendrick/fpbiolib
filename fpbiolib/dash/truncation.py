import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash import dcc, html, callback_context
from dash.exceptions import PreventUpdate

from .slider_formatting import slider_num_formatter, slider_marks


def truncate_collapse_layout(id):

    return dbc.Collapse(
        [
            html.H6(
                "x-value limits (drag slider ends or enter left/right limits in input fields)",
                id="trace_cut_slider_h6",
            ),
            html.Div(
                id=f"{id}_slider_div",  # Same id as called in truncation_float_range_slider_callback function
                className="truncate_slider_div",
            ),
        ],
        id=f"{id}_collapse",  # Controlled by 'control_chkbox_btn_callbacks'
        is_open=False,
    )


def truncation_float_range_slider_layout_callbacks(
    app, slider_id, layout_id, marks_option
):
    # Trace truncation controller / div
    @app.callback(
        Output(layout_id, "children"),
        # Output('truncation_slider', 'value'),
        Input("data_loading", "children"),
        State("initial_x_min", "children"),
        State("initial_x_max", "children"),
        # prevent_initial_call=True
    )
    def slider(data_loading, initial_x_min, initial_x_max):

        if data_loading == None:
            raise PreventUpdate

        # print('Data loading inside truncation float slider: ', data_loading)
        if marks_option:
            marks = slider_marks(initial_x_min, initial_x_max, 10)
        else:
            marks = {}

        layout = html.Div(
            [
                dcc.RangeSlider(
                    id=slider_id,
                    value=[initial_x_min, initial_x_max],
                    min=initial_x_min,
                    max=initial_x_max,
                    step=0.0001,
                    marks=marks,
                    updatemode="mouseup",
                    tooltip={"always_visible": False, "placement": "bottom"},
                    className="float_slider",
                ),
                dcc.Input(
                    id=f"{slider_id}_start",
                    type="text",
                    debounce=True,
                    value=str(initial_x_min),
                    className="slider_input",
                ),
                html.P("–", id=f"{slider_id}slider_en_space", className="en_space"),
                dcc.Input(
                    id=f"{slider_id}_end",
                    type="text",
                    debounce=True,
                    value=str(initial_x_max),
                    className="slider_input",
                ),
            ],
            id=f"{slider_id}_div",
            className="slider_div",
        )

        return layout

    # app.layout = layout
    # Link trace trucation slider and input box values, seeded with initial x-min / max values
    @app.callback(
        Output(f"{slider_id}_start", "value"),
        Output(f"{slider_id}_end", "value"),
        Output(f"{slider_id}", "value"),  # primary output of slider values
        Output(f"{slider_id}_start", "style"),
        Output(f"{slider_id}_end", "style"),
        Input(f"{slider_id}", "value"),
        Input(f"{slider_id}_start", "value"),
        Input(f"{slider_id}_end", "value"),
        # prevent_initial_call=True
    )
    def callback(slider, start, end):

        ctx = callback_context
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # Format slider values (and accompanying inputs since they are initially defined by slider values)
        slider_0_str = slider_num_formatter(
            float(slider[0]), sci_sig_figs=3, sci_note_upper=10000, sci_note_lower=0.01
        )
        slider_1_str = slider_num_formatter(
            float(slider[1]), sci_sig_figs=3, sci_note_upper=10000, sci_note_lower=0.01
        )

        # Set truncation values to those in either the input box or slider values
        slider_start = start if trigger_id == f"{slider_id}_start" else slider_0_str
        slider_end = end if trigger_id == f"{slider_id}_end" else slider_1_str
        slider_value = (
            slider
            if trigger_id == f"{slider_id}"
            else [float(slider_start), float(slider_end)]
        )

        # Pass width of dcc input based on number of characters in the input number
        style_start = {
            "width": f"{str(sum(c.isalnum() for c in str(slider_start))*10 + 2)}px",
            "textAlign": "right",
        }
        style_end = {
            "width": f"{str(sum(c.isalnum() for c in str(slider_end))*10 + 2)}px"
        }
        return slider_start, slider_end, slider_value, style_start, style_end
