from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from ..file_parsing import parse_data
from ..df_cleanup import cleanup_df_import
from .chkbox_btn import control_chkbox_btn_callbacks

import pandas as pd


def peak_labeling_toast_layout(id):
    return dbc.Toast(
        [
            html.H6(
                "Upload a csv file with pre-defined peak labels and retention times, or manually enter in table below",
                className="section_headings",
            ),
            dcc.Upload(
                [
                    "Drag and Drop or ",
                    html.A("Select Files"),
                    html.P("(.csv or single-sheet .xlsx)", className="upload_note"),
                ],
                className="uploader",
                multiple=False,
                id="upload_pk_labels",  # Used in callback function below
            ),
            html.Div(
                id="output_pk_label_div"
            ),  # layout depends on callbacks in peak_labeling_callbacks function below
        ],
        id=f"{id}_collapse",
        class_name="toast_container",
        header="Peak Labeling Control Window",
        icon="primary",
        dismissable=False,
    )


def peak_labeling_callbacks(app, id):
    # Call the control checkbox and button function
    control_chkbox_btn_callbacks(app, id=id)  # Same id as in Controls container layout

    # Enable peak labeling layout and functions
    @app.callback(
        Output("output_pk_label_div", "children"),
        Input("sel-traces", "children"),
        Input("upload_pk_labels", "contents"),
        State("upload_pk_labels", "filename"),
        # prevent_initial_call=True
    )
    def parse_pk_labels_df(sel_trace, content, filename):
        # print("SEL_TRACE IN peak_labeling.py: ", sel_trace)
        if sel_trace == [] or sel_trace == None:
            raise PreventUpdate

        if content is not None:

            label_df = parse_data(content, filename)
            label_df = cleanup_df_import(label_df)
            label_list = label_df.columns.to_list()

        else:
            # clear out last dataframe and create template
            lst = [[3.2, "pre-peak"], [4.0, "main-peak"], [4.4, "post-peak"]]
            label_df = pd.DataFrame(lst, columns=["RT (min)", "Peak Name"])
            filename = "None"

        label_list = label_df.columns.to_list()

        layout = html.Div(
            [
                html.H6("Uploaded filename: " + filename),
                html.P(
                    "The labeling algorithm takes an xls or csv file with, minimally, a column containing the x-axis postion of a peak label, and a column containing the corresponding peak label at each position.  You can select the x-axis position to also be the peak label.  The selected trace from the dropdown below will be used as the basis for placement of label (i.e. the label arrow will point to the y-axis position of the trace at the corresponding x-axis position"
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dcc.Dropdown(
                                    id="dropdown_pk_label_trace",
                                    options=[
                                        {"label": i, "value": i} for i in sel_trace
                                    ],
                                    value=sel_trace[0],
                                    searchable=False,
                                    clearable=False,
                                    placeholder="Select trace for label basis",
                                    className="sm_dropdown",
                                ),
                                dbc.Tooltip(
                                    "Select the trace to use as a basis for placement of peak label arrow. Defaults to first selected trace",
                                    target="dropdown_pk_label_trace",
                                ),
                            ]
                        ),
                        dbc.Col(
                            [
                                dcc.Dropdown(
                                    id="dropdown_pk_label_x_val",
                                    options=[
                                        {"label": i, "value": i} for i in label_list
                                    ],
                                    value="",
                                    searchable=False,
                                    clearable=False,
                                    placeholder="Select x values column",
                                    className="sm_dropdown",
                                ),
                                dbc.Tooltip(
                                    "Select the column heading that contains the x-axis values of the labels (e.g. retention time, wavelength, etc.)",
                                    target="dropdown_pk_label_x_val",
                                ),
                            ]
                        ),
                        dbc.Col(
                            [
                                dcc.Dropdown(
                                    id="dropdown_pk_label",
                                    options=[
                                        {"label": i, "value": i} for i in label_list
                                    ],
                                    value="",
                                    searchable=False,
                                    clearable=False,
                                    placeholder="Select labels column",
                                    className="sm_dropdown",
                                ),
                                dbc.Tooltip(
                                    "Select the column heading that contains the desired labels",
                                    target="dropdown_pk_label",
                                ),
                            ]
                        ),
                    ]
                ),
                html.Div(
                    [
                        dash_table.DataTable(
                            id="label_table",
                            # export_format='xlsx',
                            columns=[{"name": i, "id": i} for i in label_df.columns],
                            page_size=10,
                            data=label_df.to_dict(
                                "records"
                            ),  # the contents of the table
                            editable=True,
                            fixed_rows={"headers": True, "data": 0},
                            style_header={
                                "backgroundColor": "white",
                                "fontWeight": "bold",
                                "whiteSpace": "normal",
                                "height": "auto",
                                "border-bottom": "1px solid black",
                            },
                            style_cell={  # ensure adequate header width when text is shorter than cell's text
                                "width": "80px",  #'minWidth': '50px',# 'maxWidth': 95,
                                "whiteSpace": "normal",
                                "height": "auto",
                                "textAlign": "center",
                                "overflow": "hidden",
                                "textOverflow": "ellipsis",
                                "fontSize": 12,
                                "font-family": "Arial",
                                "color": "black",
                            },
                            style_as_list_view=True,
                            css=[
                                {
                                    "selector": ".dash-table-tooltip",
                                    "rule": "background-color: LightBlue; font-family: Arial; opacity: 1.0",
                                },
                                {"selector": ".show-hide", "rule": "display: none"},
                            ],
                        ),
                        dbc.Button(
                            "Add Row",
                            id="add-pk-label-row-button",
                            n_clicks=0,
                            size="sm",
                            color="primary",
                        ),
                    ]
                ),
            ]
        )
        # print("RETURNING PEAK_LABLE LAYOUT")
        return layout

    # Add rows to peak labeling table
    @app.callback(
        Output("label_table", "data"),
        Input("add-pk-label-row-button", "n_clicks"),
        State("label_table", "data"),
        State("label_table", "columns"),
    )
    def add_row(n_clicks, rows, columns):
        if n_clicks > 0:
            rows.append({c["id"]: "" for c in columns})
        return rows


def peak_labeling_graph_config(df, label_table_data, pk_label_x_val_sel, pk_label_sel):

    # Stick selected x_value and labels in the peak labels table into a dataframe
    labels_df = pd.DataFrame(label_table_data)

    # labels_df.to_csv('labels_df.csv')

    # This fixes an issue with the default label table having strings
    if "RT (min)" in labels_df.columns:
        labels_df["RT (min)"] = pd.to_numeric(labels_df["RT (min)"], errors="coerce")

    # Sort and clean up dataframe
    if pk_label_x_val_sel != pk_label_sel:
        labels_df = (
            labels_df[[pk_label_x_val_sel, pk_label_sel]]
            .sort_values(by=[pk_label_x_val_sel])
            .reset_index(drop=True)
        )
        labels_df.dropna(how="any", inplace=True)

    else:
        pk_label_df = labels_df[[pk_label_sel]].copy()
        pk_label_df.columns = ["pk_labels"]
        labels_df = pd.concat([labels_df[pk_label_x_val_sel], pk_label_df], axis=1)
        labels_df = labels_df.sort_values(by=[pk_label_x_val_sel]).reset_index(
            drop=True
        )
        labels_df.dropna(how="any", inplace=True)

    # x_values and labels need same number of rows
    mindex = labels_df.apply(pd.Series.last_valid_index).min()
    labels_df = labels_df.truncate(after=mindex)

    # Fix any label tables that might have usable data but also x_values outside the range of the trace x_range
    max_x_val_filter = labels_df[pk_label_x_val_sel] <= float(df.iloc[:, 0].max())
    min_x_val_filter = labels_df[pk_label_x_val_sel] >= float(df.iloc[:, 0].min())
    filtered_df = labels_df[min_x_val_filter & max_x_val_filter]

    indexes = []
    if len(filtered_df) == 0:
        """
        In case user tries to select a label x-value that doesn't correspond to trace x-values 
        """
        pk_labels = []

    else:

        def find_index(value):
            exactmatch = df[df.iloc[:, 0] == value]
            if not exactmatch.empty:
                return (exactmatch.index - 1)[
                    0
                ]  # index starts at 1 rather than zero in this case
            else:
                upperneighbour_ind = df[df.iloc[:, 0] > value].iloc[:, 0].idxmin() - 1
                return upperneighbour_ind

        if isinstance(filtered_df.iloc[0, 0], float):
            for value in filtered_df.iloc[:, 0]:
                indexes.append(find_index(float(value)))

        pk_labels = filtered_df.iloc[:, 1].to_list()
        # print('PEAK LABELS', pk_labels)

    return pk_labels, indexes
