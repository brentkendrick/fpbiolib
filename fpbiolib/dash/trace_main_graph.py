# from app import app
from .peak_labeling import peak_labeling_graph_config
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output

from ..redis_storage import read_dataframe, write_dataframe, write_numeric
from ..df_transforms import (
    df_trunc,
    df_min_max_norm,
    df_area_norm,
    find_deriv,
    df_center,
)
from ..custom_plots import primary_graph, baseline_check_graph, peak_ctr_check_graph3b
from ..fig_html_download import create_fig_html_download
from .graph_params import graph_modification_parameters
from .trace_compare import trace_comparisons
from ..baselines import sd_baseline_correction, apply_als_baseline_to_df

import pandas as pd
import numpy as np
import urllib.parse


def main_graph(
    app,
    zoom,
    stack,
    pk_max_normalize,
    area_normalize,
    reverse,
    truncate,
    peak_alignment,
    peak_labeling,
    x_axis_label,
    y_axis_label,
    linewidth,
    second_derivative,
    hide_tic,
    legend_position,
):
    @app.callback(
        Output("Mygraph", "figure"),
        Output("baseline_fit_graph", "figure"),
        Output("align_graph", "figure"),
        Output("params", "children"),
        Output("trace_compare_table", "children"),
        Output("download-link", "href"),
        Output("trace-download-link", "href"),
        Output("trace-compare-download-link", "href"),
        Output("trace-html-download", "href"),
        Input("sel-traces", "children"),
        Input(f"{zoom}_slider", "value"),
        Input(f"{stack}_slider", "value"),
        Input(f"{pk_max_normalize}-chkbox", "value"),
        Input(f"{area_normalize}-chkbox", "value"),
        Input(f"{reverse}-chkbox", "value"),
        Input(f"{truncate}_slider", "value"),
        Input(f"{truncate}-chkbox", "value"),
        Input(f"{second_derivative}-chkbox", "value"),
        Input("window", "value"),
        Input("baseline_dropdown", "value"),
        Input("dropdown_baseline_sel_trace", "value"),
        Input("left_baseline_slider", "value"),
        Input("lam_slider", "value"),
        Input(f"{peak_alignment}-chkbox", "value"),
        Input("dropdown_align_trace", "value"),
        Input("threshold_slider", "value"),
        Input("min_dist_slider", "value"),
        Input("ctr_pk_slider", "value"),
        Input(f"{peak_labeling}-chkbox", "value"),
        Input("dropdown_pk_label_x_val", "value"),
        Input("dropdown_pk_label", "value"),
        Input("dropdown_pk_label_trace", "value"),
        Input("label_table", "data"),
        Input(x_axis_label, "value"),
        Input(y_axis_label, "value"),
        Input(linewidth, "value"),
        Input(f"{hide_tic}-chkbox", "value"),
        Input(f"{legend_position}-chkbox", "value"),
        Input('session-id', 'data'),
        Input("reference_trace_dropdown", "value"),
        # prevent_initial_call=True
    )
    def callback_main_graph(
        sel_trace,
        zoom_value,
        stack_value,
        pk_max_normalize,
        area_normalize,
        reverse_x_axis,
        truncation_values,
        truncate_option,
        deriv_opt,
        window,
        baseline_option,
        asym_baseline_sel_trace,
        asym_baseline_left_x,
        asym_baseline_lam_log,
        peak_alignment_option,
        align_sel_trace,
        pk_det_threshold,
        min_dist,
        ctr_pk_range,
        pk_label_chkbox,
        pk_label_x_val_sel,
        pk_label_sel,
        selected_pk_label_trace,
        pk_label_table_data,
        x_axis_label,
        y_axis_label,
        linewidth,
        hide_tic,
        legend_position_option,
        session_id,
        reference_trace,
    ):
        # print("sel_trace INSIDE INITIAL part of callback_main_graph: ", sel_trace)
        # print("truncation values INSIDE INITIAL part of callback_main_graph: ", truncation_values)
        # if pk_max_normalize:
        #     print("pk_max_normalize chkbox value: ", pk_max_normalize)

        ctx = callback_context
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # Write the baseline correction variable values to redis so it persists even after callback inputs to the baseline correction callbacks
        write_numeric(asym_baseline_lam_log, f"temp_lam_{session_id}")
        write_numeric(asym_baseline_left_x, f"temp_asym_x_{session_id}")

        # Write the peak alignment variable values to redis so it persists even after callback inputs to the peak alignment callbacks
        write_numeric(ctr_pk_range[0], f"temp_ctr_pk_range_low_{session_id}")
        write_numeric(ctr_pk_range[1], f"temp_ctr_pk_range_high_{session_id}")
        write_numeric(min_dist, f"ctr_pk_min_dist_{session_id}")
        write_numeric(pk_det_threshold, f"pk_det_threshold_{session_id}")

        zoom = 10 ** zoom_value

        if sel_trace == []:  # This will clear everything if no traces selected
            return {}, {}, {}, html.Div(), {}, "", "", "", ""

        # Read raw dataframe from redis
        df = read_dataframe(f"trace_df_{session_id}")

        # Copy selected trace headings (using slice, fastest) and insert x-value heading
        sel_trace_with_x = sel_trace[:]
        sel_trace_with_x.insert(0, df.columns[0])

        # Just carry forward the selected traces for modifications
        df = df[sel_trace_with_x]

        # Create a dictionary to hold all the trace modifications passed to the trace viewer
        trace_viewer_parameters = {}

        # Option to Truncate the traces
        if truncate_option:
            df = df_trunc(df, truncation_values[0], truncation_values[1])
            trace_viewer_parameters["truncation limits:"] = [
                "{:.2f}, ".format(i) for i in truncation_values
            ]

            # Resetting the index is necessary after truncation since peak labeling depends on index position
            df.reset_index(drop=True, inplace=True)

        # Option to take derivative with window smoothing input
        if deriv_opt:
            trace_viewer_parameters["2nd Derivative:"] = "Yes"
            df = find_deriv(df, flip=True, window_length=window)

        # Baseline correction
        if not baseline_option == "complex":

            df = sd_baseline_correction(
                df,
                flip=False,
                method=baseline_option,
                bounds=[df.iloc[0, 0], df.iloc[-1, 0]],
                inplace=True,
            )
            baseline_fig = {}

        else:
            lam_interval = 10 ** asym_baseline_lam_log
            # Baseline algorithms
            # def baseline_event_handler(df, selected_trace, asym_baseline_left_x, lam_interval):
            trace_viewer_parameters["left baseline limit:"] = asym_baseline_left_x
            trace_viewer_parameters["lam interval:"] = "{:.3e}".format(lam_interval)

            y_original = np.asarray(df[asym_baseline_sel_trace]).copy()

            df, df_fitted_baseline = apply_als_baseline_to_df(
                df, asym_baseline_left_x, lam_interval, niter=100
            )

            x_val = np.asarray(df.iloc[:, 0])
            fitted_baseline_active = np.asarray(
                df_fitted_baseline[asym_baseline_sel_trace]
            )

            # graph the baseline function, the original selected plot and corrected selected plot

            baseline_fig = baseline_check_graph(
                x_val, y_original, fitted_baseline_active, zoom_level=zoom
            )

        # Option to ormalize traces to peak max
        if pk_max_normalize:
            trace_viewer_parameters["normalized to y-max:"] = "Yes"
            # normalize uv and tic peaks to same arbitrary scale
            df = df_min_max_norm(df)

        # Option to area normalize traces
        if area_normalize:
            trace_viewer_parameters["Area normalized to 1.0:"] = "Yes"
            df = df_area_norm(df)

        # Peak alignment
        if peak_alignment_option:
            pk_det_threshold = 10 ** pk_det_threshold
            import peakutils

            trace_viewer_parameters["peak detection threshold:"] = pk_det_threshold
            trace_viewer_parameters["peak detection min distance:"] = min_dist
            ctr_left, ctr_right = ctr_pk_range[0], ctr_pk_range[1]
            trace_viewer_parameters["peak center reference range:"] = [
                "{:.2f}, ".format(i) for i in ctr_pk_range
            ]
            df_center_peaks = df_trunc(df, ctr_left, ctr_right)

            y_active = np.asarray(df_center_peaks[align_sel_trace]).copy()
            x_active = np.asarray(df_center_peaks.iloc[:, 0]).copy()
            # find peak center X, and Y values
            ctr_indexes = peakutils.indexes(y_active, pk_det_threshold, min_dist)

            align_fig = peak_ctr_check_graph3b(
                df_center_peaks, align_sel_trace, linewidth, ctr_indexes
            )

            trace_ctr_txt = "peaks centered on " + align_sel_trace + " trace:"
            trace_viewer_parameters[trace_ctr_txt] = "Yes"
            df = df_center(df.copy(), df_center_peaks, pk_det_threshold, min_dist)
        else:
            align_fig = {}

        # Option to add Peak Labels to the traces
        # pk_labels and indexes aren't being passed in the callback, so set defaults here:
        pk_labels, indexes = [], []
        if pk_label_chkbox and pk_label_x_val_sel and pk_label_sel:
            pk_labels, indexes = peak_labeling_graph_config(
                df, pk_label_table_data, pk_label_x_val_sel, pk_label_sel
            )

        if hide_tic:
            hide_tic = True

        if legend_position_option:
            legend_position = "right"
        else:
            legend_position = "left"

        # print("sel_trace in main graph: ", sel_trace_with_x)
        fig = primary_graph(
            df,
            offint=stack_value,
            zoom_level=zoom,
            linewidth=linewidth,
            indexes=indexes,
            pk_labels=pk_labels,
            pk_labeling=pk_label_chkbox,
            hide_TIC=hide_tic,
            y_label=y_axis_label,
            x_label=x_axis_label,
            reverse=reverse_x_axis,
            selected_pk_label_trace=selected_pk_label_trace,
            legend_position=legend_position,
        )

        # Create downloadable html file of plotly graph
        trace_html_download_href = create_fig_html_download(fig)

        # Trace comparision algorithims
        trace_compare_table, trace_compare_csv_string = trace_comparisons(df, reference_trace)
        trace_viewer_parameters["Similarity Reference Trace:"] = reference_trace


        # Trace processing parameters
        params_table, params_csv_string = graph_modification_parameters(
            trace_viewer_parameters
        )

        # print("MAIN GRAPH, JUST BEFORE RETURN: ")

        # Write processed trace dataframe to redis
        write_dataframe(df, f"processed_df_{session_id}")

        # Create downloadable csv href from processed dataframe
        trace_csv_string = df.to_csv(index=False, encoding="utf-8-sig")
        trace_csv_string = "data:text/csv;charset=utf-8-sig," + urllib.parse.quote(
            trace_csv_string
        )

        return (
            fig,
            baseline_fig,
            align_fig,
            params_table,
            trace_compare_table,
            params_csv_string,
            trace_csv_string,
            trace_compare_csv_string,
            trace_html_download_href,
        )
