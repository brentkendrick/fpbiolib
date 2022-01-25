import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from ..redis_storage import read_numeric

from ..plotly_config import config
from .slider_formatting import slider_marks
from .chkbox_btn import control_btn_no_label_layout, control_chkbox_btn_callbacks


def peak_alignment_modal_layout(id):
    return dbc.Modal(
        [
            dbc.ModalHeader("Peak Alignment Controller"),
            dbc.ModalBody(
                [
                    dbc.Row([dbc.Col(html.Div(id=f"{id}_sel_trace"), width=3),],),
                    dbc.Row(
                        [
                            dbc.Col(html.Div(id=f"{id}_min_dist")),
                            dbc.Col(html.Div(id=f"{id}_det_thresh")),
                        ],
                    ),
                    dbc.Row([dbc.Col(html.Div(id=f"{id}_range"), width=11),],),
                    dcc.Graph(id="align_graph", config=config),
                ],
            ),
        ],
        id=f"{id}_collapse",
        size="xl",
        className="xxl_modal",
    )


### Peak alignment ###
# Peak alignment modal controller
def peak_alignment_callbacks(app, id, truncate):

    # Call the control checkbox and button function
    control_chkbox_btn_callbacks(app, id=id)  # Same id as in Controls container layout

    @app.callback(
        Output(f"{id}_sel_trace", "children"),
        Output(f"{id}_range", "children"),
        Output(f"{id}_min_dist", "children"),
        Output(f"{id}_det_thresh", "children"),
        Input(f"{truncate}_slider", "value"),
        Input("sel-traces", "children"),
        Input('session-id', 'data'),
        # prevent_initial_call=True
    )
    def pk_align_trace(truncation_values, sel_trace, session_id):
        if sel_trace == [] or sel_trace == None:
            raise PreventUpdate

            # TODO can this entire callback be only fired when alignment is needed?  Right now, the dcc id
            #      values are utilized in the main trace processing callback

        try:

            x_min = float(truncation_values[0])
            x_max = float(truncation_values[1])

            # Read the peak alignment variable values from redis so it persists even after callback inputs to the peak alignment callbacks
            ctr_pk_range = [0.0, 1.0]  # temporary placeholder values
            ctr_pk_range[0] = read_numeric(f"temp_ctr_pk_range_low_{session_id}")
            ctr_pk_range[1] = read_numeric(f"temp_ctr_pk_range_high_{session_id}")
            min_dist = read_numeric(f"ctr_pk_min_dist_{session_id}")
            pk_det_threshold = read_numeric(f"pk_det_threshold_{session_id}")

            pk_align_select = html.Div(
                [
                    html.H6("Select trace for peak detection"),
                    dcc.Dropdown(
                        id="dropdown_align_trace",
                        options=[{"label": i, "value": i} for i in sel_trace],
                        value=sel_trace[0],
                        searchable=False,
                        clearable=False,
                        placeholder="Select trace for alignment basis",
                        className="sm_dropdown",
                    ),
                ]
            )

            pk_align_range = html.Div(
                [
                    html.H6("Select peak center reference range:"),
                    dcc.RangeSlider(
                        id="ctr_pk_slider",
                        value=ctr_pk_range,
                        min=x_min,
                        max=x_max,
                        step=0.1,
                        marks=slider_marks(x_min, x_max, 20),
                        updatemode="mouseup",
                        className="slider",
                        tooltip={"always_visible": False, "placement": "bottom"},
                    ),
                ]
            )

            pk_align_min_dist = html.Div(
                [
                    html.H6("Peak minimum distance parameter:"),
                    dcc.Slider(
                        id="min_dist_slider",
                        value=min_dist,
                        min=0,
                        max=100,
                        step=0.1,
                        marks=slider_marks(0, 100, 10),
                        updatemode="mouseup",
                        className="slider",
                        tooltip={"always_visible": False, "placement": "bottom"},
                    ),
                ]
            )

            pk_align_det_thresh = html.Div(
                [
                    html.H6("Peak detection threshold:"),
                    dcc.Slider(
                        id="threshold_slider",
                        value=pk_det_threshold,
                        min=-2,
                        max=0,
                        step=0.01,
                        marks=slider_marks(-2, 0, 10),
                        updatemode="mouseup",
                        className="slider",
                        # handleLabel = {"showCurrentValue": True}
                        tooltip={"always_visible": False, "placement": "bottom"},
                    ),
                ]
            )
            return (
                pk_align_select,
                pk_align_range,
                pk_align_min_dist,
                pk_align_det_thresh,
            )
        except:
            raise PreventUpdate
