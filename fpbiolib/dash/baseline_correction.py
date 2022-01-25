import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from ..redis_storage import read_numeric

from ..plotly_config import config
from .slider_formatting import slider_marks
from .chkbox_btn import control_btn_no_label_layout


def baseline_correction_control_layout(id):
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
                            {"label": "Asymmetric", "value": "complex"},
                        ],
                        value="none",
                        clearable=False,
                        searchable=False,
                    ),
                    control_btn_no_label_layout(id=id),
                    dbc.Tooltip(
                        "Only for Asymmetric baseline option", target=f"{id}_button"
                    ),
                ],
                className="row_container_no_wrap",
            ),
        ],
        className="control-dropdown-btn-container",
    )


def asym_baseline_modal_layout(id):
    return dbc.Modal(
        [
            dbc.ModalHeader("Asymmetric Baseline Correction Controller"),
            dbc.ModalBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(html.Div(id=f"{id}_sel_trace"), width=3),
                            dbc.Col(html.Div(id=f"{id}_left_cut"), width=5),
                            dbc.Col(html.Div(id=f"{id}_lam"), width=4),
                        ]
                    ),
                    dcc.Graph(id="baseline_fit_graph", config=config),
                ],
            ),
        ],
        id=f"{id}_collapse",
        size="xl",
        is_open=False,
        className="xxl_modal",
    )


### Asymmetric baseline ###
# Asymmetric baseline modal controller
def asym_baseline_callbacks(app, id, truncate):

    # Asymmetric baseline control layout served in the modal,
    # and dcc id values used in the main trace processing callback
    @app.callback(
        Output(f"{id}_sel_trace", "children"),
        Output(f"{id}_left_cut", "children"),
        Output(f"{id}_lam", "children"),
        Input("data_loading", "children"),
        Input(f"{truncate}_slider", "value"),
        Input("sel-traces", "children"),
        Input('session-id', 'data'),
        # prevent_initial_call=True
    )
    def complex_baseline_trace(data_loading, truncation_values, sel_trace, session_id):
        # This throws an error in the console.log since the dropdown_baseline_sel_trace is non-existent until
        # print("SEL_TRACE IN peak_labeling.py: ", sel_trace)

        # this reloads every time a new trace is selcted, and all values get reset.  Try read/write to redis?
        if data_loading == None:
            raise PreventUpdate
        try:

            x_min = float(truncation_values[0])
            x_max = float(truncation_values[1])

            lam_value = read_numeric(f"temp_lam_{session_id}")
            left_baseline_x = read_numeric(f"temp_asym_x_{session_id}")

            dropdown_baseline_obj = html.Div(
                [
                    html.H6("Select trace to correct", className="slider__text"),
                    dcc.Dropdown(
                        id="dropdown_baseline_sel_trace",
                        options=[{"label": i, "value": i} for i in sel_trace],
                        value=sel_trace[0],
                        searchable=False,
                        clearable=False,
                        placeholder="Select trace for baseline",
                        className="sm_dropdown",
                    ),
                ]
            )

            left_baseline_obj = html.Div(
                [
                    html.H6(
                        "Select left x-axis baseline position:",
                        className="slider__text",
                    ),
                    dcc.Slider(
                        id="left_baseline_slider",
                        value=left_baseline_x,
                        min=x_min,
                        max=x_max,
                        step=0.1,
                        marks=slider_marks(x_min, x_max, 10),
                        updatemode="mouseup",
                        className="slider",
                        # handleLabel = {"showCurrentValue": True}
                        tooltip={"always_visible": False, "placement": "bottom"},
                    ),
                ]
            )
            lam_obj = html.Div(
                [
                    html.H6("Select Lam value:", className="slider__text"),
                    dcc.Slider(
                        id="lam_slider",
                        value=lam_value,
                        min=3,
                        max=10,
                        step=0.001,
                        marks=slider_marks(3, 10, 10),
                        updatemode="mouseup",
                        className="slider",
                        # handleLabel = {"showCurrentValue": True}
                        tooltip={"always_visible": False, "placement": "bottom"},
                    ),
                ]
            )
            return dropdown_baseline_obj, left_baseline_obj, lam_obj
        except:
            raise PreventUpdate

    # Collapse controller
    @app.callback(
        Output(f"{id}_collapse", "is_open"),
        Input(f"{id}_button", "n_clicks"),
        Input("baseline_dropdown", "value"),
        State(f"{id}_collapse", "is_open"),
    )
    def toggle_collapse(n, baseline_type, is_open):
        if baseline_type == "complex":
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
