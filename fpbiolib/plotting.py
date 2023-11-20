import plotly.graph_objects as go
import numpy as np

layout = go.Layout(template="simple_white")


def go_plot(x: np.array, y_set: list, names: list):
    fig = go.Figure(layout=layout)
    for i, trace in enumerate(y_set):
        fig.add_traces([go.Scatter(mode="lines", x=x, y=trace, name=names[i])])

    fig.update_layout(showlegend=True)
    fig.show()
