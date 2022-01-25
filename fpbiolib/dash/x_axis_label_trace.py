import dash
import dash_bootstrap_components as dbc
from dash import Input, Output


def input_group_x(id):
    dropdown_menu_items = [
        dbc.DropdownMenuItem("Retention Time", id=f"{id}-dropdown-menu-item-1"),
        dbc.DropdownMenuItem("Retention Time w/units", id=f"{id}-dropdown-menu-item-2"),
        dbc.DropdownMenuItem("Mass", id=f"{id}-dropdown-menu-item-3"),
        dbc.DropdownMenuItem("Mass w/units", id=f"{id}-dropdown-menu-item-4"),
        dbc.DropdownMenuItem("Wavelength", id=f"{id}-dropdown-menu-item-5"),
        dbc.DropdownMenuItem("Wavelength w/units", id=f"{id}-dropdown-menu-item-6"),
        dbc.DropdownMenuItem("Wavenumber", id=f"{id}-dropdown-menu-item-7"),
        dbc.DropdownMenuItem("Wavenumber w/units", id=f"{id}-dropdown-menu-item-8"),
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


def x_axis_dropdown_input_ctl(app, id):
    @app.callback(
        Output(id, "value"),
        [
            Input(f"{id}-dropdown-menu-item-1", "n_clicks"),
            Input(f"{id}-dropdown-menu-item-2", "n_clicks"),
            Input(f"{id}-dropdown-menu-item-3", "n_clicks"),
            Input(f"{id}-dropdown-menu-item-4", "n_clicks"),
            Input(f"{id}-dropdown-menu-item-5", "n_clicks"),
            Input(f"{id}-dropdown-menu-item-6", "n_clicks"),
            Input(f"{id}-dropdown-menu-item-7", "n_clicks"),
            Input(f"{id}-dropdown-menu-item-8", "n_clicks"),
            Input(f"{id}-dropdown-menu-item-clear", "n_clicks"),
        ],
    )
    def on_button_click(n1, n2, n3, n4, n5, n6, n7, n8, n_clear):
        ctx = dash.callback_context

        if not ctx.triggered:
            return ""
        else:
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == f"{id}-dropdown-menu-item-clear":
            return ""
        elif button_id == f"{id}-dropdown-menu-item-1":
            return "Retention Time"
        elif button_id == f"{id}-dropdown-menu-item-2":
            return "Retention Time (min)"
        elif button_id == f"{id}-dropdown-menu-item-3":
            return "Mass"
        elif button_id == f"{id}-dropdown-menu-item-4":
            return "Mass (Da.)"
        elif button_id == f"{id}-dropdown-menu-item-5":
            return "Wavelength"
        elif button_id == f"{id}-dropdown-menu-item-6":
            return "Wavelength (nm)"
        elif button_id == f"{id}-dropdown-menu-item-7":
            return "Wavenumber"
        else:
            return "Wavenumber (cm⁻¹)"
