from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from lib.dashapps.upload import parse_data

import pandas as pd


def parse_pk_label_div(sel_trace, content, filename):

    if content is not None:

        label_df = parse_data(content, filename)
        label_list = label_df.columns.to_list()

    else:
        # clear out last dataframe and create template
        lst = [[3.2, "pre-peak"], [4.0, "main-peak"], [4.4, "post-peak"]]
        label_df = pd.DataFrame(lst, columns=["RT (min)", "Peak Name"])
        filename = "None"

    label_list = label_df.columns.to_list()

    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Checklist(
                            id="x_labels",
                            options=[
                                {
                                    "label": " Label peaks with x-value",
                                    "value": True,
                                },
                            ],
                            value=False,
                            switch=False,
                            className="pk_labels_chkbox",
                        ),
                        width=3,
                    ),
                    dbc.Col(
                        dbc.Checklist(
                            id="user_choice_labels",
                            options=[
                                {
                                    "label": " Label peaks from selected heading",
                                    "value": True,
                                },
                            ],
                            value=False,
                            switch=False,
                            className="pk_labels_chkbox",
                        ),
                        width=4,
                    ),
                ]
            ),
            html.Hr(className="hr"),
            html.H6("Uploaded filename: " + filename),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(
                            id="dropdown_pk_label_trace",
                            options=[
                                {"label": i, "value": i} for i in sel_trace
                            ],
                            # value=sel_trace[0],
                            searchable=False,
                            clearable=False,
                            placeholder="Select trace for label basis",
                            className="sm_dropdown",
                        )
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="dropdown_pk_label_x_val",
                            options=[
                                {"label": i, "value": i} for i in label_list
                            ],
                            value="",
                            searchable=False,
                            clearable=False,
                            placeholder="Select x_value heading",
                            className="sm_dropdown",
                        )
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="dropdown_pk_label",
                            options=[
                                {"label": i, "value": i} for i in label_list
                            ],
                            value="",
                            searchable=False,
                            clearable=False,
                            placeholder="Select label heading",
                            className="sm_dropdown",
                        )
                    ),
                ]
            ),
            html.Div(
                [
                    dash_table.DataTable(
                        id="label_table",
                        # export_format='xlsx',
                        columns=[
                            {"name": i, "id": i} for i in label_df.columns
                        ],
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
                                "white-space": "pre-wrap",
                            },
                            {
                                "selector": ".show-hide",
                                "rule": "display: none",
                            },
                        ],
                    ),
                    dbc.Button(
                        "Add Row",
                        id="editing-rows-button",
                        n_clicks=0,
                        size="sm",
                        color="primary",
                    ),
                ]
            ),
        ]
    )
