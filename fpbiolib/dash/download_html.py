from dash import html
import dash_bootstrap_components as dbc


def html_downloader(id, btn_label, tooltip_text):
    return dbc.Row(
        [
            dbc.Col(
                [
                    html.A(
                        dbc.Button(
                            html.Span(btn_label, id=f"tooltip-{id}"),
                            class_name="primary_button",
                            color="primary",
                        ),
                        id=f"{id}",  # id in main_graph_callback
                        download="trace.html",
                        href="",
                        className="download_link",
                    ),
                    dbc.Tooltip(tooltip_text, target=f"tooltip-{id}",),
                ],
                width=3,
            ),
        ]
    )
