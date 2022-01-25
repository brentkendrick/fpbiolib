from dash import html
import dash_bootstrap_components as dbc

outputs = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Outputs", className="section_headings"),
            html.Hr(className="hr"),
            html.H6("Trace Similarity Values", className="section_headings"),
            html.Div(id="trace_compare_table", className="row_container_no_wrap_ctr"),
            html.Hr(className="hr"),
            html.H6("Trace Processing Parameters", className="section_headings"),
            html.Div(id="params", className="row_container_no_wrap_ctr"),
            html.Hr(className="hr"),
        ]
    ),
    className="pretty_container",
    style={"marginRight": "10px"},
)
