import dash_bootstrap_components as dbc
from dash import ctx, dcc, html, no_update, Dash


# Generic checkbox button component


def switch_label_controller(
    id="f-s",
    label=None,
):
    return html.Div(
        [
            dbc.Switch(
                id=id,
                value=False,
                style={"font-size": "16px", "margin-right": "-5px"},
            ),
            dbc.Label(
                label, style={"font-size": "14px", "margin": "1px 3px 0 0px"}
            ),
        ],
        style={
            "display": "flex",
            "margin": "5px",
            "padding": "4px",
            "padding-top": "0px",
            "padding-bottom": "0px",
            "color": "rgb(17,80,143)",
        },
    )
