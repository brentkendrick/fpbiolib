from dash import html


def generate_table(dataframe, max_rows=26):
    """Create a HTML table. Important:  Will fail if all
    dataframe elements are not converted to string elements."""
    return html.Table(
        # Header
        [html.Thead(html.Tr([html.Th(col) for col in dataframe.columns]))] +
        # Body
        [
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(dataframe.iloc[i][col])
                            for col in dataframe.columns
                        ]
                    )
                    for i in range(min(len(dataframe), max_rows))
                ]
            )
        ],
        className="norbi-table",
    )
