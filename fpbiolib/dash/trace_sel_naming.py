import dash_bootstrap_components as dbc

from itertools import compress

from ..redis_storage import read_dataframe, write_dataframe
from ..lists import make_list_vals_unique

from dash import dcc, html, callback_context

from dash.dependencies import Input, Output, State, ALL

from dash.exceptions import PreventUpdate


def select_rename_traces_layout_callbacks(app, layout_id):

    # Overall layout callback instantiated on data_loading
    @app.callback(
        Output(f"{layout_id}-div", "children"),
        Input("data_loading", "children"),
        Input('session-id', 'data'),
        State(f"{layout_id}-div", "children"),
    )
    def rename(data_loading, session_id, children):
        if data_loading == None:
            raise PreventUpdate

        df = read_dataframe(f"trace_df_{session_id}")

        # Loop through df.columns and create corresponding selection chkboxes and editable column name input fields
        layout = dbc.Collapse([
            html.Div(
                [
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(
                                dbc.Checkbox(
                                    value=False,
                                    id={"type": "trace-select-chkbox", "index": i},
                                )
                            ),
                            dbc.Input(
                                value=i,
                                id={"type": "rename-trace-input", "index": i},
                                debounce=True,
                            ),
                        ]
                    )
                    for i in df.columns[1:]
                ],
            ),
        ],
            id=f"{layout_id}_collapse",
            is_open=True,
                className="trace_naming_div",
        )
        return layout

    @app.callback(
        Output("sel-traces", "children"),
        Input({"type": "rename-trace-input", "index": ALL}, "value"),
        Input({"type": "trace-select-chkbox", "index": ALL}, "value"),
        Input('session-id', 'data'),
        State("sel-traces", "children"),
    )
    def trace_select_and_naming(inputs, chkbox_bool_list, session_id, selected_traces):
        if inputs == []:
            raise PreventUpdate
        if True not in chkbox_bool_list:
            return []

        # create a temporary list to hold list with new input values
        temp_list = [value for value in inputs]

        # create a new column name list, ensuring it has unique values (can't have duplicate column headings)
        name_list = make_list_vals_unique(temp_list)

        # Only write an updated dataframe if renaming a trace
        ctx = callback_context
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if "rename-trace" in trigger_id:
            print("Renaming the trace, writing new dataframe")
            # pull in the dataframe so we can rename the columns
            df = read_dataframe(f"trace_df_{session_id}")

            # Grab the x-axis column since it won't be changing, then extend it with the new names
            new_df_columns = [df.columns[0]]
            new_df_columns.extend(name_list)

            # Rename the dataframe columns and write the df to redis
            df.columns = new_df_columns
            write_dataframe(df, f"trace_df_{session_id}")

        # First intance of selected_traces will be 'None'
        if selected_traces == None:
            selected_traces = []

        selected_traces_temp = list(compress(name_list, chkbox_bool_list))

        if len(selected_traces_temp) > len(selected_traces):
            # Find the newly selected trace in the set of selected traces
            selected_traces_difference = list(
                set(selected_traces_temp).difference(selected_traces)
            )
            # Extend the list of selected traces with the newly selected trace
            selected_traces.extend(selected_traces_difference)
        elif len(selected_traces_temp) < len(selected_traces):
            # Find the newly removed trace in the set of selected traces and remove it
            selected_traces_difference = list(
                set(selected_traces).difference(selected_traces_temp)
            )
            selected_traces.remove(selected_traces_difference[0])
        else:
            # find the value that was input (e.g. modified) in the temporary list
            selected_traces_tmp_difference = min(
                set(selected_traces_temp).difference(selected_traces)
            )
            # find the corresponding value that needs to be replaced in the selected_traces list
            selected_traces_difference = min(
                set(selected_traces).difference(selected_traces_temp)
            )
            # rebuild the selected traces list with the modified input value
            selected_traces = [
                selected_traces_tmp_difference if selected_traces_difference == i else i
                for i in selected_traces
            ]

        return selected_traces


    @app.callback(
        Output("reference_trace_div", "children"),
        Input("sel-traces", "children"),
    )
    def reference_trace_selection(selected_traces):
        if selected_traces == []:
            raise PreventUpdate
        else:
            layout = html.Div(
                    [
                        dbc.Label("Reference Trace", class_name="dropdown-control-label"),
                        html.Div(
                            [
                                dcc.Dropdown(
                                    id="reference_trace_dropdown",
                                    options=[
                                        {"label": trace_name, "value": trace_name}
                                        for trace_name in selected_traces
                                    ],
                                    value=selected_traces[0],
                                    clearable=False,
                                    searchable=False,
                                ),
                            ],
                            className="row_container_no_wrap",
                        ),
                    ],
                    id="reference-trace-selector-container",
                )
            return layout