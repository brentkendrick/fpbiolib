import dash_bootstrap_components as dbc
from dash import dcc, html
from .chkbox_btn import chklist_switch_layout


def second_derivative_layout(id):

    return html.Div(
        [
            html.Div(
                [chklist_switch_layout(id=f"{id}-chkbox", label="", switch=True),],
                className="control-chklist-btn",
            ),
            dbc.Label(f"{id}", class_name="control-label"),
            # html.P('Window', className='control-label-margin-left'),
            dcc.Input(
                id="window",
                type="number",
                value=19,
                min=3,
                max=99,
                step=2,
                className="input_box",
            ),
            dbc.Tooltip("Enter window length for second derivative", target="window"),
        ],
        className="control-chklist-input-container",
    )
