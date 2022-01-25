# from app import app
import dash_bootstrap_components as dbc

import pandas as pd

from ..file_parsing import parse_uploaded_traces, parse_data
from ..redis_storage import read_numeric, write_dataframe, write_numeric

from dash import no_update, dcc, html, callback_context

from dash.dependencies import Input, Output, State

# Modal for selecting import type
datatype_import_selector_modal = dbc.Modal(
    [
        dbc.ModalHeader("Click Button Corresponding to Appropriate Data Format"),
        dbc.ModalBody(
            [
                dcc.Loading(id="data_loading"),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Single X, One or More Y"),
                                dbc.CardImg(
                                    src="assets/x_many_y_values.jpg",
                                    title="X with Many Y Values",
                                    class_name="data_modal",
                                ),
                                dbc.Button(
                                    "One X Many Y",
                                    color="primary",
                                    id="x_many_y_button",
                                ),
                            ],
                            width=6,
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Multiple X, Y Pairs"),
                                dbc.CardImg(
                                    src="assets/many_x_y.jpg",
                                    title="Many X,Y pairs",
                                    class_name="data_modal",
                                ),
                                dbc.Button(
                                    "Many X, Y Pairs",
                                    color="primary",
                                    id="many_x_y_button",
                                ),
                            ],
                            width=6,
                        ),
                    ]
                ),
            ]
        ),
    ],
    id="main_graph_data_import_modal",  size='l', class_name='xxl_modal', centered=False, fade=True,
)


# *** Uploader layout ***


def uploader_layout(id):
    return html.Div(
        [
            # Instatiate importer modal
            datatype_import_selector_modal,
            # Uploader
            dcc.Upload(
                [
                    html.P(className="upload-icon fas fa-cloud-download-alt"),
                    html.Div(
                        [
                            "Drag and Drop or ",
                            html.A("Select Files"),
                            html.P(
                                "(.csv or single-sheet .xlsx)", className="upload_note"
                            ),
                        ]
                    ),
                ],
                className="uploader",
                multiple=True,
                id=id,
            ),
            # Alert
            html.Div(id="import-status"),
            html.P(id="uploaded_trace_filenames"),
            html.Hr(className="hr"),
        ]
    )


# Uploader Callbacks
def uploader_callbacks(app, id):
    # Open / close modal to display data import options
    @app.callback(
        Output("main_graph_data_import_modal", "is_open"),
        Input(id, "contents"),
        Input("x_many_y_button", "n_clicks"),
        Input("many_x_y_button", "n_clicks"),
        State("main_graph_data_import_modal", "is_open"),
    )
    def show_modal(filename, n_x_many_y, n_x_y, is_open):
        """Show modal for adding a label."""
        # Open the modal when file is uploaded
        if filename is not None:
            return not is_open
        # Close the modal when the datatype is selected
        elif n_x_many_y or n_x_y:
            return is_open

    # Create initial trace dataframe from imported data type
    @app.callback(
        Output("data_loading", "children"),
        Output("uploaded_trace_filenames", "children"),
        Output("initial_x_min", "children"),
        Output("initial_x_max", "children"),
        Output("import-status", "children"),
        Input("x_many_y_button", "n_clicks"),
        Input("many_x_y_button", "n_clicks"),
        Input('session-id', 'data'),
        State(id, "contents"),
        State(id, "filename"),
    )
    def parse_trace_df(n1, n2, session_id, contents, filenames):

        print("INSIDE UPLOADER.PY: ")
        # clear out last saved df and x_min, x_max values
        df = pd.DataFrame()

        write_dataframe(df, f"trace_df_{session_id}")  # Used in main app w/Redis
        
        # When user clicks the x_many_y_button or another of the file type buttons, grab the id
        changed_id = [p["prop_id"] for p in callback_context.triggered][0]

        if contents is None:
            # clear out stored data
            return (
                None,
                html.Div("No file", style={"color": "red"}),
                no_update,
                no_update,
                "",
            )

        (
            uploaded_trace_filenames,
            df,
            import_status,
            x_min,
            x_max,
        ) = parse_uploaded_traces(contents, filenames, changed_id)

        # Write raw data dataframe to redis
        write_dataframe(df, f"trace_df_{session_id}")

        write_numeric(8, f"temp_lam_{session_id}")
        write_numeric(x_min, f"temp_asym_x_{session_id}")

        write_numeric(360.0, f"ref_lambda_{session_id}")

        # Write the initial peak alignment variable values to redis so initial callback has some values
        write_numeric(x_min, f"temp_ctr_pk_range_low_{session_id}")
        write_numeric(x_max, f"temp_ctr_pk_range_high_{session_id}")
        write_numeric(80, f"ctr_pk_min_dist_{session_id}")
        write_numeric(-0.097, f"pk_det_threshold_{session_id}")

        if "error" in import_status:
            import_status = dbc.Alert(
                [
                    html.H4("Uh oh!", className="alert-heading m-0"),
                    html.P(
                        "Your file doesn't appear to have the correct format, please ensure it is a single sheet xlsx or csv file and refer to the format examples provided in the popup window after you've uploaded your file"
                    ),
                ],
                color="danger",
                duration=4000,
                className="alert-import",
            )
        else:
            import_status = ""
            # import_status = dbc.Alert(
            #     [
            #             html.P("Import successful!", className="alert-heading m-0"),

            #     ],
            #     color="success",
            #     duration=1500,
            #     className='alert-import'
            #     )
        # returning None for the data loading spinner, uploaded filename(s),
        return "data loaded", uploaded_trace_filenames, x_min, x_max, import_status


""" BELOW NOT USED """
# Simple Uploader Callbacks
def simple_uploader_callbacks(app):
    @app.callback(
        Output("output-data-upload", "children"),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
    )
    def update_output(list_of_contents, list_of_names):
        if list_of_contents is not None:
            df = parse_data(list_of_contents, list_of_names)

            df.to_csv(
                "exports/simple_dash_upload_df.csv"
            )  # Uncomment to write csv to local storage

            return html.Div()


# Simple uploader layout
simple_uploader_layout = html.Div(
    [
        dcc.Upload(
            id="upload-data",
            children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
            # Don't Allow multiple files to be uploaded
            multiple=False,
        ),
        html.Div(id="output-data-upload"),
    ]
)
