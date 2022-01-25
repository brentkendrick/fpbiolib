import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table, callback_context
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from ..redis_storage import read_dataframe

from ..plotly_config import config
from .slider_formatting import slider_marks, slider_num_formatter
from .generate_html_table import generate_table

from ..ftir_band_assignments import (
    yang_h20_2015,
    yang_h20_2015_w_side_chains,
    secondary_structure,
)
from ..gaussian import gaussian_least_squares, gaussian_list, gaussians_to_df
from ..custom_plots import Gaussian_plots


import urllib.parse
import pandas as pd


def ftir_curve_fit_modal(id):
    return dbc.Modal(
        [
            dbc.ModalHeader("FTIR Amide I Curve Fitting Controller"),
            dbc.ModalBody(
                [
                    html.H6(
                        "FTIR Curvefit Trace Selector", className="section_headings"
                    ),
                    html.Hr(className="hr"),
                    html.Div(
                        [
                            html.P(
                                "Select sample for curve fitting: ",
                                id="curvefit_trace_select_heading",
                            ),
                            dcc.RadioItems(
                                id="curvefit_trace_select",
                                inputStyle={
                                    "margin-left": "10px",
                                    "margin-right": "1px",
                                },
                            ),
                        ],
                        className="ftir_curvefit_inputs_div",
                    ),
                    html.Hr(className="hr"),
                    html.Div(
                        [
                            html.P("Peak width", className="slider_name"),
                            dcc.Slider(
                                id="ftir_curvefit_bw_slider",
                                value=5,
                                min=0.1,
                                max=20.0,
                                step=0.1,
                                updatemode="mouseup",
                            ),
                            dcc.Input(
                                id="ftir_curvefit_bw_value", type="number", step=0.1
                            ),
                            dbc.Checklist(
                                id="ftir_side_chain_chkbox",
                                options=[
                                    {
                                        "label": "Fit side chain peak?",
                                        "value": "ftir_side_chain",
                                    },
                                ],
                                value=[],
                                switch=False,
                            ),
                        ],
                        className="ftir_curvefit_inputs_div",
                    ),
                    html.Hr(className="hr"),
                    dcc.Graph(id="ftir_curvefit_graph", config=config),
                    html.Hr(className="hr"),
                    html.H5("Deconvolution results"),
                    html.Div(id="ftir_deconvolution_table"),
                    html.Hr(className="hr"),
                    html.A(
                        "Download Trace Comparison Data",
                        id="structs_df_download_link",
                        download="ftir_deconvolution.csv",
                        href="",
                        target="_blank",
                        className="download_link",
                    ),
                    html.A(
                        "Download Gaussian Curve Fit Data",
                        id="gaussian_df_download_link",
                        download="ftir_gaussians.csv",
                        href="",
                        target="_blank",
                        className="download_link_margin_left",
                    ),
                    html.P(
                        "When opening the downloaded trace comparison data result csv file in your preferred application (e.g. Excel), if the greek characters don't import correctly, ensure the csv is imported using the UTF-8 format",
                        className="P_Small",
                    ),
                ],
                id="ftir_curvefit_container",
            ),
        ],
        id=f"{id}_collapse",
        size="xl",
        is_open=False,
        className="xxl_modal",
    )


# FTIR curve fit modal controller
def ftir_curve_fit_callbacks(app, id):

    # FTIR Bandwidth Slider and Input
    @app.callback(
        Output("ftir_curvefit_bw_value", "value"),
        Output("ftir_curvefit_bw_slider", "value"),
        Input("ftir_curvefit_bw_slider", "value"),
        Input("ftir_curvefit_bw_value", "value"),
    )
    def callback(slider_value, input_value):
        ctx = callback_context
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # Format slider values (and accompanying inputs since they are initially defined by slider values)
        # slider_str_value = slider_num_formatter(float(slider_value), sci_sig_figs=3, sci_note_upper=10000, sci_note_lower=0.01)

        input_value = (
            input_value if trigger_id == "ftir_curvefit_bw_value" else slider_value
        )
        slider_value = (
            slider_value if trigger_id == "ftir_curvefit_bw_slider" else input_value
        )

        return float(input_value), float(slider_value)

    # Send selected traces to FTIR Trace Selector
    # Needs to be separate from the graphing output callbacks
    # So that the trace options radio buttons are pre-populated
    # Before the modal gets opened with the button click
    @app.callback(
        Output("curvefit_trace_select", "options"),
        Input("sel-traces", "children"),
        # prevent_initial_call=True
    )
    def update_pk_labels(sel_trace):
        if sel_trace is None or sel_trace is []:
            raise PreventUpdate
        return [{"label": i, "value": i} for i in sel_trace]

    # FTIR graphing output
    @app.callback(
        Output("ftir_curvefit_graph", "figure"),
        Output("structs_df_download_link", "href"),
        Output("gaussian_df_download_link", "href"),
        Output("ftir_deconvolution_table", "children"),
        Input(f"{id}_button", "n_clicks"),
        Input("curvefit_trace_select", "value"),
        Input("ftir_side_chain_chkbox", "value"),
        Input("ftir_curvefit_bw_slider", "value"),
        Input('session-id', 'data'),
    )
    def ftir_curve_fit_processing(n, trace_to_fit, side_chains, peak_width, session_id):
        # changed_id = [p['prop_id'] for p in callback_context.triggered][0]

        ### TODO: add changed id prop call?
        if trace_to_fit is not None and n != 0:

            # Read processed dataframe from redis
            df = read_dataframe(f"processed_df_{session_id}")
            # Temparary variables, will replace with callbacks
            linewidth = 1.2
            reverse = False

            if side_chains:
                peaks = yang_h20_2015_w_side_chains
            else:
                peaks = yang_h20_2015
            try:
                area, res = gaussian_least_squares(
                    df,
                    trace_to_fit,
                    peaks=peaks,
                    peak_width=peak_width,
                    params={"loss": "linear"},
                )
                gaussian_list_data = gaussian_list(df.iloc[:, 0], *res.x)

                structs = secondary_structure(area, peaks)
                structs_df = pd.DataFrame(
                    list(structs.items()), columns=["Structure", "Fraction"]
                )
                structs_df["Fraction"] = structs_df["Fraction"].map("{:,.4f}".format)

                # Convert to csv to enable data download
                structs_df_csv = structs_df.to_csv(index=False, encoding="utf-8-sig")
                structs_df_csv = (
                    "data:text/csv;charset=utf-8-sig,"
                    + urllib.parse.quote(structs_df_csv)
                )

                # Create downloadable csv href from curvefit dataframe
                gaussian_df = gaussians_to_df(df, gaussian_list_data, trace_to_fit)
                # print("INSIDE CURVEFIT", gaussian_df.head())
                gaussian_csv = gaussian_df.to_csv(index=False, encoding="utf-8-sig")
                gaussian_csv = "data:text/csv;charset=utf-8-sig," + urllib.parse.quote(
                    gaussian_csv
                )

                fig = Gaussian_plots(
                    df,
                    trace_to_fit,
                    gaussian_list_data,
                    linewidth=linewidth,
                    reverse=reverse,
                )

                return fig, structs_df_csv, gaussian_csv, generate_table(structs_df)
            except:
                return {}, "", "", ""
        else:
            return {}, "", "", ""

    # Collapse controller
    @app.callback(
        Output(f"{id}_collapse", "is_open"),
        Input(f"{id}_button", "n_clicks"),
        State(f"{id}_collapse", "is_open"),
    )
    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open

    # Change the button to indicate when function is activated
    @app.callback(
        Output(f"{id}_button", "children"),
        Output(f"{id}_button", "color"),
        Input(f"{id}_collapse", "is_open"),
    )
    def format_collapse_button(is_open):
        if is_open:
            return html.I(className="fas fa-chevron-down"), "success"
        else:
            return html.I(" ", className="fas fa-chevron-right"), "secondary"
