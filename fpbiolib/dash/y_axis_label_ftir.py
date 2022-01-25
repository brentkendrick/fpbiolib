import dash
import dash_bootstrap_components as dbc
from dash import Input, Output


def input_group_y(id):
    dropdown_menu_items = [
        dbc.DropdownMenuItem("Abs", id=f"{id}-dropdown-menu-item-1"),
        dbc.DropdownMenuItem("2nd Der", id=f"{id}-dropdown-menu-item-2"),
        dbc.DropdownMenuItem("2nd Der w/units", id=f"{id}-dropdown-menu-item-3"),
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


def ftir_y_axis_dropdown_input_ctl(app, id):
    @app.callback(
        Output(id, "value"),
        [
            Input(f"{id}-dropdown-menu-item-1", "n_clicks"),
            Input(f"{id}-dropdown-menu-item-2", "n_clicks"),
            Input(f"{id}-dropdown-menu-item-3", "n_clicks"),
            Input(f"{id}-dropdown-menu-item-clear", "n_clicks"),
        ],
    )
    def on_button_click(n1, n2, n3, n_clear):
        ctx = dash.callback_context

        if not ctx.triggered:
            return ""
        else:
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == f"{id}-dropdown-menu-item-clear":
            return ""
        elif button_id == f"{id}-dropdown-menu-item-1":
            return "Absorbance"
        elif button_id == f"{id}-dropdown-menu-item-2":
            return "d²A/d²ν"
        else:
            return "d²A/d²ν (cm⁻¹)⁻²"
