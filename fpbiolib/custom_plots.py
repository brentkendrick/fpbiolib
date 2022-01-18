from plotly.graph_objs import Layout
import plotly.io as pio
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
import math

pltcolors = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]

primary_layout = go.Layout(
    # width = 1000,
    # height = 400,
    margin=dict(l=0, r=0, t=20, b=20),
    paper_bgcolor="white",
    plot_bgcolor="white",
    xaxis=dict(
        showgrid=False,
        showline=True,
        linewidth=2,
        linecolor="black",
        mirror=True,
        title_text="",
        ticks="outside",
        tickcolor="black",
        tickwidth=2,
        ticklen=10,
    ),
    yaxis=dict(
        showgrid=False,
        showline=True,
        linewidth=2,
        linecolor="black",
        mirror=True,
        title_text="",
        ticks="outside",
        tickcolor="black",
        tickwidth=2,
        ticklen=10,
    ),
    legend=dict(
        traceorder="reversed", yanchor="top", y=0.99, xanchor="left", x=0.01
    ),
    modebar=dict(
        orientation="h",
        bgcolor="white",
        color="lightgray",  # button color
        activecolor="darkblue",  # controls color when hovering mouse
        uirevision="",  # Controls `hovermode`, `dragmode`, and `showspikes`
    ),
)


def primary_graph(
    df,
    offint=0,
    zoom_level=1.0,
    linewidth=1,
    indexes=[],
    pk_labels=[],
    pk_labeling=False,
    hide_TIC=False,
    y_label="Abs",
    x_label="RT (min)",
    reverse=False,
    selected_pk_label_trace="default",
    legend_position="left",
):

    # print("INSIDE PRIMARY GRAPH")

    max_y = 1.10 * df[df.columns[1:]].max(axis=1).max()
    min_y = 1.10 * df[df.columns[1:]].min(axis=1).min()
    offset = 0
    offint = 0.001 * offint * (max_y - min_y)  # *(len(df.columns)-2)

    fig = go.Figure(layout=primary_layout)

    fig.update_layout(
        margin=dict(l=0, r=50, t=30, b=50),
        font_family="Arial",
        font_color="black",
        font_size=16,
        title_font_family="Arial",
        title_font_color="black",
        title_font_size=16,
        legend_title_font_color="black",
        legend_title_font_size=16,
    )

    if legend_position == "left":
        fig.update_layout(
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
        )
    else:
        fig.update_layout(
            legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99)
        )

    if reverse:
        fig.update_layout(
            xaxis=dict(tickmode="auto", tickangle=0, autorange="reversed")
        )
    else:
        fig.update_layout(xaxis=dict(tickmode="auto", tickangle=0))

    # Option to hide TIC trace for combined TIC/UV plots
    if hide_TIC:  # assumes TIC is first trace
        offset = 0
        for i in range(len(df.columns) - 2):

            fig.add_trace(
                go.Scatter(
                    x=df.iloc[:, 0],
                    y=df.iloc[:, (i + 2)] + offset,
                    mode="lines",
                    line_shape="spline",
                    name=df.columns[(i + 2)],
                    line=dict(color=pltcolors[i], width=linewidth),
                )
            )

            offset += offint

    else:
        offset = 0
        for i in range(len(df.columns) - 1):

            fig.add_trace(
                go.Scatter(
                    x=df.iloc[:, 0],
                    y=df.iloc[:, (i + 1)] + offset,
                    mode="lines",
                    line_shape="spline",
                    name=df.columns[(i + 1)],
                    line=dict(color=pltcolors[i], width=linewidth),
                )
            )

            offset += offint

    if pk_labeling:
        # For peak labeling find top y value (may need work?)
        if selected_pk_label_trace == "default":
            top_y_val = np.asarray(df.iloc[:, -1])
        else:
            top_y_val = np.asarray(df[selected_pk_label_trace])
        x_val = np.asarray(
            df.iloc[:, 0]
        )  # numpy array creation is faster than to_list creation
        for i in range(len(x_val[indexes].tolist())):
            fig.add_annotation(
                dict(
                    x=x_val[indexes][i],
                    y=top_y_val[indexes][i] + offset - offint,
                    text=pk_labels[i],
                )
            )

        fig.update_annotations(
            dict(
                xref="x",
                yref="y",
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-35,
                clicktoshow="onoff",
                standoff=2,
                font=dict(color="black", size=14),
                textangle=0,
                xanchor="center",
            )
        )

    fig.update_xaxes(
        showline=True,
        linewidth=1,
        linecolor="black",
        ticks="outside",
        tickwidth=1,
        tickcolor="black",
        ticklen=5,
        mirror=True,
    )
    fig.update_yaxes(
        showline=True,
        linewidth=1,
        linecolor="black",
        ticks="outside",
        tickwidth=1,
        tickcolor="black",
        ticklen=5,
        mirror=True,
    )
    fig.update_layout(
        yaxis=dict(
            range=[min_y, max_y / zoom_level],
            title_text=y_label,
        ),
        xaxis=dict(
            title_text=x_label,
        ),
    )
    # Override default behavior to hide legend if only 1 trace plotted
    fig["data"][0]["showlegend"] = True
    if hide_TIC:
        fig["data"][0]["name"] = df.columns[2]

    else:
        fig["data"][0]["name"] = df.columns[1]
    return fig


def baseline_check_graph(x_val, y_val, base, zoom_level=1):

    # Call graph object figure initialization
    fig = go.Figure(layout=go.Layout())

    # Add traces
    fig.add_trace(
        go.Scatter(
            x=x_val, y=(y_val - base), mode="lines", name="baseline corrected"
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x_val, y=y_val - base.min(), mode="lines", name="original"
        )
    )
    fig.add_trace(
        go.Scatter(x=x_val, y=base - base.min(), mode="lines", name="baseline")
    )
    fig.update_layout(
        template="plotly_white",
        yaxis=dict(
            title_text="Absorbance",
            range=[(0 - abs(0.002 * y_val.max())), y_val.max() / zoom_level],
        ),
        xaxis=dict(title_text="Wavelength (nm)"),
    )
    return fig


def peak_ctr_check_graph3b(
    df_cen_chk, selected_trace, linewidth, indexes, labels=False, pk_labels=[]
):

    indexes = indexes
    # Call graph object figure initialization
    layout = go.Layout()
    fig = go.Figure(layout=layout)
    #         idx_len = len(x_val)
    y_active = np.asarray(df_cen_chk[selected_trace].copy())
    x_active = np.asarray(df_cen_chk.iloc[:, 0].copy())
    # Add traces
    for i in range(len(df_cen_chk.columns) - 1):

        fig.add_trace(
            go.Scatter(
                x=df_cen_chk.iloc[:, 0],
                y=df_cen_chk.iloc[:, (i + 1)],
                mode="lines",
                name=df_cen_chk.columns[(i + 1)],
                line=dict(color=pltcolors[i], width=linewidth),
            )
        )

    for i in range(len(x_active[indexes].tolist())):
        if labels:
            fig.add_annotation(
                dict(
                    x=x_active[indexes][i],
                    y=y_active[indexes][i],
                    text=pk_labels[i],
                )
            )
            i += 1
        else:
            fig.add_annotation(
                dict(
                    x=x_active[indexes][i],
                    y=y_active[indexes][i],
                    text="{:.2f}".format((round(x_active[indexes][i], 2))),
                )
            )
            i += 1
    fig.update_annotations(
        dict(
            xref="x",
            yref="y",
            showarrow=True,
            # captureevents=True,
            # plotly_clickannotation=True,
            arrowhead=2,
            ax=0,
            ay=-35,
            clicktoshow="onoff",
            standoff=2,
            font=dict(color="black", size=10),
            textangle=-90,
            xanchor="left",
        )
    )
    # pio.show(fig)
    return fig


def axis_ticks(a, zoom, dfmax, y_ax):

    #     if zoom <= 1:
    #         zoom = 1
    #     elif zoom <= 3:
    #         zoom = 2
    #     else:
    #         zoom =5

    if not y_ax:
        zoom = 1
    a_min = a.min() / zoom
    a_max = dfmax / zoom
    delta = abs(a_max - a_min)
    delta_mag = magnitude(delta)

    """
    create tick value rounded down to appropriate place value, i.e.
    if a_min is 0, and a_max is 50 - 100, we want major ticks every 10 and minor every 2.
    if a_min is 0, and a_max is 10 - 50, we want major ticks every 5 and minor every 1

    if a_max - a_min is between 10 - 99, deltamag is 1
    we want low end of ticks to start at nearest 10 place on the low side (i.e. if a_min is 11, we want tick_low at 10)
    """
    tick_low = rounddown(
        a_min, 10 ** (int(delta_mag))
    )  # rounds to nearest place value on low end
    tick_hi = roundup(a_max, 10 ** (int(delta_mag)))

    dif_norm = (
        a_max / 10 ** delta_mag - a_min / 10 ** delta_mag
    )  # create normalized difference parameter, i.e. if a_max is 600, and delta_mag is 2 it gets normalized to 6

    if dif_norm >= 5:
        tick_spc_maj = 10 ** (int(delta_mag))
        tick_spc = tick_spc_maj / 5
        #         tick_vals_major = list(np.around((np.arange(tick_low, tick_hi+tick_spc*1, tick_spc_maj)), decimals = magnitude(a_max)-4))
        tick_vals_major = list(
            np.arange(tick_low, tick_hi * zoom, tick_spc_maj)
        )
        tick_vals = list(np.arange(tick_low, tick_hi * zoom, tick_spc))
    else:
        tick_spc_maj = (10 ** (int(delta_mag))) / 2
        tick_spc = tick_spc_maj / 5
        #         tick_vals_major = list(np.around((np.arange(tick_low, tick_hi+tick_spc*1, tick_spc_maj)), decimals = magnitude(a_max)-4))
        tick_vals_major = list(
            np.arange(tick_low, tick_hi * zoom, tick_spc_maj)
        )
        tick_vals = list(np.arange(tick_low, tick_hi * zoom, tick_spc * zoom))

    #     if y_ax:

    #         tick_spc_maj = (10**(int(delta_mag)))/2
    #         tick_spc = tick_spc_maj/5
    #         tick_vals_major = list(np.arange(tick_low, tick_hi+tick_spc*1, tick_spc_maj))
    #         tick_vals = list(np.arange(tick_low, tick_hi+tick_spc, tick_spc*zoom))

    #'''Create function to format tick_txt decimal places based on a_max value '''

    mag_a_max = magnitude(a_max)
    if (
        mag_a_max <= 1
    ):  # formatting only works for decimal places, and only want 1 decimal for power of 10
        s = (
            -mag_a_max + 2
        )  #  magnitudes will be negative for values < 0, need to reverse sign
    else:
        s = 0  # zero places for magnitudes >1

    tick_txt = ["" for x in tick_vals]
    if (
        abs(tick_vals[0]) >= 10000 or abs(tick_vals[-1]) >= 10000
    ):  # use sci not if above 10000
        tick_txt_major = ["{:.2e}".format(x) for x in tick_vals_major]
    else:
        tick_txt_major = ["{:.{}f}".format(x, s) for x in tick_vals_major]

    return a_min, a_max, tick_vals, tick_txt, tick_vals_major, tick_txt_major


def roundup(
    x, val
):  # x is value to be rounded, val is the placevalue, i.e. 100, 10, 1, 0.1, 0.01, etc. to be rounded to
    return (
        x
        if x % val == 0
        else round((x + val - x % val), -int(math.log10(val)))
    )  # python has floating point issues, only soln seems to round again here.


def rounddown(x, val):
    return x if x % val == 0 else round((x - x % val), -int(math.log10(val)))


def magnitude(value):
    if value == 0:
        return 0
    return int(math.floor(math.log10(abs(value))))


left = False
right = False
min_y = 0
max_y = (100,)

basic_layout = Layout(
    # width = 1000,
    # height = 400,
    margin=dict(l=0, r=0, t=20, b=20),
    paper_bgcolor="white",
    plot_bgcolor="white",
    xaxis={
        "showgrid": True,
        "showline": True,
        "linewidth": 2,
        "linecolor": "black",
        "mirror": True,
        "title_text": "Wavelength",
        "range": [left, right],
        "ticks": "outside",
        "tickcolor": "black",
        "tickwidth": 2,
        "ticklen": 10,
    },
    yaxis={
        "showgrid": True,
        "showline": True,
        "linewidth": 2,
        "linecolor": "black",
        "mirror": True,
        "title_text": "Abs",
        # "range": [min_y, max_y],
        "ticks": "outside",
        "tickcolor": "black",
        "tickwidth": 2,
        "ticklen": 10,
    },
    xaxis2={
        "showgrid": True,
        "showline": True,
        "linewidth": 2,
        "linecolor": "black",
        "mirror": True,
        "title_text": "",
        "range": [left, right],
        "ticks": "outside",
        "tickcolor": "black",
        "tickwidth": 2,
        "ticklen": 10,
    },
)


def Simple_plot(df):
    fig = make_subplots(rows=2)

    xdata = df.iloc[:, 0]
    ydata = df.iloc[:, 1]
    # Add traces
    fig.add_trace(
        go.Scatter(x=xdata, y=ydata, mode="lines", name="original"),
        row=1,
        col=1,
    )

    fig["layout"].update(basic_layout)

    fig.layout.yaxis2.update(
        {
            "showgrid": False,
            "showline": True,
            "linewidth": 2,
            "linecolor": "black",
            "mirror": True,
            "title_text": "",
            "ticks": "outside",
            "tickcolor": "black",
            "tickwidth": 2,
            "ticklen": 10,
        }
    )
    fig.layout.xaxis2.update(
        {
            "showgrid": False,
            "showline": True,
            "linewidth": 2,
            "linecolor": "black",
            "mirror": True,
            "title_text": "",
            "ticks": "outside",
            "tickcolor": "black",
            "tickwidth": 2,
            "ticklen": 10,
        }
    )
    return fig


def Gaussian_plots(df, col, peak_list, linewidth=1.2, reverse=False):

    layout = go.Layout(
        # width = 1000,
        height=800,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(
            showgrid=False,
            showline=True,
            linewidth=2,
            linecolor="black",
            mirror=True,
            title_text="",
            ticks="outside",
            tickcolor="black",
            tickwidth=2,
            ticklen=10,
        ),
        yaxis=dict(
            showgrid=False,
            showline=True,
            linewidth=2,
            linecolor="black",
            mirror=True,
            title_text="",
            ticks="outside",
            tickcolor="black",
            tickwidth=2,
            ticklen=10,
        ),
    )
    # Call graph object figure initialization
    fig = make_subplots(rows=2)

    xdata = df.iloc[:, 0]
    y_fit = sum(peak_list)
    # Add traces
    fig.add_trace(
        go.Scatter(x=xdata, y=df[col], mode="lines", name="original"),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=xdata, y=y_fit, mode="lines", name="Model fit"),
        row=1,
        col=1,
    )
    for i in range(len(peak_list)):
        fig.add_trace(
            go.Scatter(
                x=xdata,
                y=peak_list[i],
                showlegend=False,
                line=dict(width=linewidth, dash="dash"),
            ),
            row=1,
            col=1,
        )

    # Add subplot with residuals
    resid = df[col] - y_fit
    fig.add_trace(
        go.Scatter(x=xdata, y=resid, mode="lines", name="residuals"),
        row=2,
        col=1,
    )
    fig["layout"].update(layout)

    if reverse:
        fig.update_xaxes(autorange="reversed")
    else:
        fig.update_xaxes()

    fig.layout.yaxis2.update(
        {
            "showgrid": False,
            "showline": True,
            "linewidth": 2,
            "linecolor": "black",
            "mirror": True,
            "title_text": "",
            "ticks": "outside",
            "tickcolor": "black",
            "tickwidth": 2,
            "ticklen": 10,
        }
    )
    fig.layout.xaxis2.update(
        {
            "showgrid": False,
            "showline": True,
            "linewidth": 2,
            "linecolor": "black",
            "mirror": True,
            "title_text": "",
            "ticks": "outside",
            "tickcolor": "black",
            "tickwidth": 2,
            "ticklen": 10,
        }
    )
    return fig
