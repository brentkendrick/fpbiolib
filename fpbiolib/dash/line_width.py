import dash_bootstrap_components as dbc
from dash import dcc, html


def linewidth_layout(id):

    return html.Div(
        [
            dbc.Label(f"{id}", class_name="control-label"),
            dcc.Input(
                id=id,
                type="number",
                value=1.2,
                min=0.1,
                max=5.0,
                step=0.1,
                className="input_box",
            ),
        ],
        className="control-chklist-btn-container",
    )
