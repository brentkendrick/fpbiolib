import dash_bootstrap_components as dbc
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from ..redis_storage import read_numeric

from ..plotly_config import config
from .slider_formatting import slider_marks
from .chkbox_btn import control_btn_no_label_layout


def light_scattering_uvvis_control_layout(id):
    return html.Div(
        [
            dbc.Label(f"{id}", class_name="dropdown-control-label"),
            html.Div(
                [
                    dcc.Dropdown(
                        id="baseline_dropdown",
                        options=[
                            {"label": "None", "value": "none"},
                            {"label": "minimum", "value": "min"},
                            {"label": "Linear", "value": "straight"},
                            {"label": "Rubber Band", "value": "rubberband"},
                            {"label": "Light Scattering", "value": "LS"},
                        ],
                        value="none",
                        clearable=False,
                        searchable=False,
                    ),
                    control_btn_no_label_layout(id=id),
                    dbc.Tooltip(
                        "Only for Light Scattering baseline option",
                        target=f"{id}_button",
                    ),
                ],
                className="row_container_no_wrap",
            ),
        ],
        className="control-dropdown-btn-container",
    )


def light_scattering_uvvis_modal_layout(id):
    return dbc.Modal(
        [
            dbc.ModalHeader("Light Scattering Baseline Correction Controller"),
            dbc.ModalBody(
                [
                    html.Div(id=f"{id}_sel_trace"),
                    html.Div(id=f"{id}_ref_lambda"),
                    dcc.Graph(id="baseline_fit_graph", config=config),
                ],
            ),
        ],
        id=f"{id}_collapse",
        size="xl",
        is_open=False,
        className="xxl_modal",
    )


### Light Scattering baseline ###
# LS baseline modal controller
def light_scattering_baseline_callbacks(app, id, truncate):

    # Asymmetric baseline control layout served in the modal,
    # and dcc id values used in the main trace processing callback
    @app.callback(
        Output(f"{id}_sel_trace", "children"),
        Output(f"{id}_ref_lambda", "children"),
        Input("data_loading", "children"),
        Input(f"{truncate}_slider", "value"),
        Input("sel-traces", "children"),
        Input('session-id', 'data'),
        # prevent_initial_call=True
    )
    def ls_baseline_trace(data_loading, truncation_values, sel_traces, session_id):
        # This throws an error in the console.log since the dropdown_baseline_sel_traces is non-existent until
        # print("SEL_TRACEs IN peak_labeling.py: ", sel_traces)

        # this reloads every time a new trace is selcted, and all values get reset.  Try read/write to redis?
        if data_loading == None:
            raise PreventUpdate
        try:

            x_min = float(truncation_values[0])
            x_max = float(truncation_values[1])

            lam_value = read_numeric(f"temp_lam_{session_id}")

            ref_lambda = read_numeric(f"ref_lambda_{session_id}")

            dropdown_baseline_obj = html.Div(
                [
                    html.H6("Select trace to correct", className="slider__text"),
                    dcc.Dropdown(
                        id="dropdown_baseline_sel_trace",
                        options=[{"label": i, "value": i} for i in sel_traces],
                        value=sel_traces[0],
                        searchable=False,
                        clearable=False,
                        placeholder="Select trace for baseline",
                        className="sm_dropdown",
                    ),
                ]
            )

            ref_lambda_obj = html.Div(
                [
                    html.H6(
                        "Select wavelength free of chromophore signal:",
                        className="slider__text",
                    ),
                    dcc.Slider(
                        id="ref_lambda_slider",
                        value=ref_lambda,
                        min=x_min,
                        max=x_max,
                        step=0.1,
                        marks=slider_marks(x_min, x_max, 10),
                        updatemode="mouseup",
                        className="slider",
                        # handleLabel = {"showCurrentValue": True}
                        tooltip={"always_visible": False, "placement": "bottom"},
                    ),
                    dcc.Input(id="ref_lambda_slider_value", type="number", step=0.1),
                ],
                className="light_scattering_modal_div",
            )

            return dropdown_baseline_obj, ref_lambda_obj
        except:
            raise PreventUpdate

    # Slider and Input
    @app.callback(
        Output("ref_lambda_slider_value", "value"),
        Output("ref_lambda_slider", "value"),
        Input("ref_lambda_slider", "value"),
        Input("ref_lambda_slider_value", "value"),
    )
    def callback(slider_value, input_value):
        ctx = callback_context
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # Format slider values (and accompanying inputs since they are initially defined by slider values)
        # slider_str_value = slider_num_formatter(float(slider_value), sci_sig_figs=3, sci_note_upper=10000, sci_note_lower=0.01)

        input_value = (
            input_value if trigger_id == "ref_lambda_slider_value" else slider_value
        )
        slider_value = (
            slider_value if trigger_id == "ref_lambda_slider" else input_value
        )

        return float(input_value), float(slider_value)

    # Collapse controller
    @app.callback(
        Output(f"{id}_collapse", "is_open"),
        Input(f"{id}_button", "n_clicks"),
        Input("baseline_dropdown", "value"),
        State(f"{id}_collapse", "is_open"),
    )
    def toggle_collapse(n, baseline_type, is_open):
        if baseline_type == "LS":
            if n:
                return not is_open
            return not is_open
        return is_open

    # Change the button to indicate when function is activated
    @app.callback(
        Output(f"{id}_button", "children"),
        Output(f"{id}_button", "color"),
        Input(f"{id}_collapse", "is_open"),
    )
    def format_collapse_button(is_open):
        if is_open:
            return html.I(className="fas fa-chevron-down"), "success"
        else:
            return html.I(" ", className="fas fa-chevron-right"), "secondary"
