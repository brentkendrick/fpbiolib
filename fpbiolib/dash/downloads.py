from dash import html
import dash_bootstrap_components as dbc

downloads = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Downloadable csv files", className="section_headings"),
            html.Hr(className="hr"),
            html.A(
                "Download Processing Parameters",
                id="download-link",
                download="parameters.csv",
                href="",
                target="_blank",
                className="download_link",
            ),
            html.Hr(className="hr"),
            html.A(
                "Download Processed Data",
                id="trace-download-link",
                download="trace_data.csv",
                href="",
                target="_blank",
                className="download_link",
            ),
            html.Hr(className="hr"),
            html.A(
                "Download Trace Comparison Data",
                id="trace-compare-download-link",
                download="trace_comparison.csv",
                href="",
                target="_blank",
                className="download_link",
            ),
            html.Hr(className="hr"),
        ]
    ),
    className="pretty_container",
)
