import pandas as pd
import urllib.parse
from dash import html, dash_table

from .generate_html_table import generate_table



def graph_modification_parameters(trace_viewer_parameters):
    trace_viewer_params_df = (
        pd.DataFrame([trace_viewer_parameters]).transpose().reset_index()
    )
    trace_viewer_params_df.columns = ["Parameter", "Value"]

    csv_string = trace_viewer_params_df.to_csv(index=False, encoding="utf-8-sig")
    csv_string = "data:text/csv;charset=utf-8-sig," + urllib.parse.quote(csv_string)

    return (
        generate_table(trace_viewer_params_df),
        csv_string,
    )
