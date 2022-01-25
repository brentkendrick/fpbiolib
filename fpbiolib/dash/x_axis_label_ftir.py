import dash
import dash_bootstrap_components as dbc
from dash import Input, Output


def input_group_x(id):
    dropdown_menu_items = [
        dbc.DropdownMenuItem("Wavenumber", id=f"{id}-dropdown-menu-item-1"),
        dbc.DropdownMenuItem("Wavenumber w/units", id=f"{id}-dropdown-menu-item-2"),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem("Clear", id=f"{id}-dropdown-menu-item-clear"),
    ]
    return dbc.InputGroup(
        [
            dbc.DropdownMenu(dropdown_menu_items, label=f"{id}-label"),
            dbc.Input(id=id, placeholder="type or select from dropdown"),
        ],
        class_name="primary_button",
    )


def ftir_x_axis_dropdown_input_ctl(app, id):
    @app.callback(
        Output(id, "value"),
        [
            Input(f"{id}-dropdown-menu-item-1", "n_clicks"),
            Input(f"{id}-dropdown-menu-item-2", "n_clicks"),
            Input(f"{id}-dropdown-menu-item-clear", "n_clicks"),
        ],
    )
    def on_button_click(n1, n2, n_clear):
        ctx = dash.callback_context

        if not ctx.triggered:
            return ""
        else:
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == f"{id}-dropdown-menu-item-clear":
            return ""
        elif button_id == f"{id}-dropdown-menu-item-1":
            return "Wavenumber"
        else:
            return "Wavenumber (cm⁻¹)"
