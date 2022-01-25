from dash.dependencies import Input, Output, State

from dash import html, no_update
import dash_bootstrap_components as dbc


# Layouts
def chklist_switch_layout(id, label, switch=True):
    if switch == True:
        class_name = "switch_ctl"
    else:
        class_name = "chklist_ctl"
    return dbc.Checklist(
        id=f"{id}",
        options=[{"label": label, "value": "selected"},],
        value=[],
        switch=switch,
        class_name=class_name,
    )


def control_chkbox_btn_layout(id):

    return html.Div(
        [
            html.Div(
                [chklist_switch_layout(id=f"{id}-chkbox", label="", switch=True),],
                className="control-chklist-btn",
            ),
            dbc.Label(f"{id}", class_name="control-label"),
            dbc.Button(id=f"{id}_button", class_name="open_close_button",),
        ],
        className="control-chklist-btn-container",
    )


def control_chkbox_btn_layout_padding_top(id):

    return html.Div(
        [
            html.Div(
                [chklist_switch_layout(id=f"{id}-chkbox", label="", switch=True),],
                className="control-chklist-btn",
            ),
            dbc.Label(f"{id}", class_name="control-label"),
            dbc.Button(id=f"{id}_button", class_name="open_close_button",),
        ],
        className="control-chklist-btn-container-padding-top",
    )


def control_chkbox_layout(id):

    return html.Div(
        [
            html.Div(
                [chklist_switch_layout(id=f"{id}-chkbox", label="", switch=True),],
                className="control-chklist-btn",
            ),
            dbc.Label(f"{id}", class_name="control-label"),
        ],
        className="control-chklist-btn-container",
    )


def control_btn_layout(id):

    return html.Div(
        [
            html.Div(
                [
                    dbc.Label(f"{id}", class_name="control-label"),
                    dbc.Button(id=f"{id}_button", class_name="open_close_button",),
                ],
                className="control-chklist-btn",
            ),
        ],
        className="control-chklist-btn-container",
    )


def control_btn_no_label_layout(id):

    return html.Div(
        [dbc.Button(id=f"{id}_button", class_name="open_close_button",),],
        className="control-dropdown-btn",
    )


# Callbacks
# The control to open and collapse is generic
def control_chkbox_btn_callbacks(app, id):
    # Collapse controller
    @app.callback(
        Output(f"{id}_collapse", "is_open"),
        Input(f"{id}_button", "n_clicks"),
        State(f"{id}_collapse", "is_open"),
    )
    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open

    # Activate switch first time collapse is opened
    @app.callback(
        Output(f"{id}-chkbox", "value"),
        Input(f"{id}_button", "n_clicks"),
        Input(f"{id}_collapse", "is_open"),
        State(f"{id}-chkbox", "value"),
    )
    def toggle_collapse(n, is_open, chkbox):
        if n == 1:
            return ["selected"]

            # if is_open:
            #     return ['selected']
            # return []
        else:
            return chkbox

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


def main_window_column_widths_callbacks(app, id1, id2):
    # Change the window widths when large controllers are opened
    @app.callback(
        Output("controls-outputs-downloads-row", "width"),
        Output("graph-row", "width"),
        Input(f"{id1}_collapse", "is_open"),
        Input(f"{id2}_collapse", "is_open"),
    )
    def format_width(pk_label_is_open, truncate_is_open):
        if pk_label_is_open:
            return 5, 7
        elif truncate_is_open:
            return 4, 8
        else:
            return 3, 9


""" BELOW ITEMS DROPPED FROM DEV / """

# This kinda works...goal was to have checkbox auto select when pressing on button
# but it will unselect when toggling the button again, which isn't desired.
# @app.callback(
#     Output(f'{id}-chkbox', 'value'),
#     Input(f'{id}_button', "n_clicks"),
#     State(f'{id}-chkbox', 'value'),
# )
# def toggle_chkbox(n, chk):
#     print('CHECKBOX IN collapse: ', chk)
#     if n==1:
#         return ['selected']
#     else:
#         return []

truncation_toast = dbc.Toast(
    [
        html.H6(
            "x-value limits (drag slider ends or enter left/right limits in input boxes to truncate x-data)",
            id="trace_cut_slider_h6",
        ),
        html.Div(id="cut_trace", className="slider_div"),
    ],
    id="truncation_toast",
    header="Trace Truncation Controller",
    is_open=False,
    class_name="graph_controller_toasts",
    dismissable=False,
)
# Peak alignment control layout served in the modal,
# and dcc id values used in the main trace processing callback

# Peak alignment toast controller
def trace_truncation_toast_control(app):
    @app.callback(
        Output("truncation_toast", "is_open"),
        Input("truncation_button", "n_clicks"),
        Input("truncation_chkbox", "value"),
    )
    def toggle_collapse(n1, truncation):
        if "checked" in truncation:
            if n1 == 0:
                return no_update
            return True
        return False


# Optional Modal
truncation_modal = dbc.Modal(
    [
        dbc.ModalHeader("Trace Truncation Controller"),
        dbc.ModalBody(
            [dbc.Row([dbc.Col(html.Div(id="cut_trace"), width=11),],),],
            id="trace_truncation_container",
        ),
        dbc.ModalFooter(
            dbc.Button(
                "Close",
                id="close_trace_truncation_modal",
                class_name="mr-1",
                color="primary",
                size="sm",
                n_clicks=0,
            )
        ),
    ],
    id="trace_truncation_modal",
    size="xl",
    is_open=False,
    class_name="xxl_modal",
    centered=True,
    fade=True,
)
# Peak alignment modal controller
def trace_truncation_modal_control(app):
    @app.callback(
        Output("trace_truncation_modal", "is_open"),
        Input("truncation_button", "n_clicks"),
        Input("close_trace_truncation_modal", "n_clicks"),
        State("trace_truncation_modal", "is_open"),
        State("truncation_chkbox", "value"),
    )
    def toggle_collapse(n1, n2, is_open, truncation):
        if "align" in truncation:
            if n1 or n2:
                return not is_open
            return is_open
        return False
