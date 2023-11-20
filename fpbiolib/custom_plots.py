import math

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.graph_objs import Layout
from plotly.subplots import make_subplots

# import symbol

MINOR_TICKS = {
    "None": None,
    "one_tick": dict(
        ticklen=5,
        tickmode="auto",
        nticks=3,
    ),
    "four_ticks": dict(
        ticklen=5,
        tickmode="auto",
        nticks=5,
    ),
    "nine_ticks": dict(
        ticklen=5,
        tickmode="auto",
        nticks=10,
    ),
}

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

# pltcolors_orig = pltcolors.copy()

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
        # traceorder="reversed",
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
    ),
    modebar=dict(
        orientation="h",
        bgcolor="white",
        color="lightgray",  # button color
        activecolor="darkblue",  # controls color when hovering mouse
        uirevision="",  # Controls `hovermode`, `dragmode`, and `showspikes`
    ),
)


def dec_notation(sci_note_upper):
    num_order_power = math.floor(math.log10(num))
    num_order = 10**num_order_power
    dec = str(int(math.log10(sci_note_upper) - math.log10(num_order)))
    return ".4f"


".2e"


def sci_notation(num, sig_figs):
    return f"{{:.{sig_figs}e}}".format(num)


def tick_label_formatter(
    num, sci_sig_figs=3, sci_note_upper=1000000, sci_note_lower=0.01
):
    print("\nnum: ", num)
    if num >= sci_note_upper or num < sci_note_lower:
        return ".3e"
    else:
        return ".6"


def primary_graph(
    df,
    reference_trace,
    stack_value=0,
    zoom_level=1.0,
    pk_label_indexes=[],
    pk_labels=[],
    pk_labeling=False,
    hide_reference_trace=False,
    y_label="Abs",
    x_label="RT (min)",
    reverse=False,
    pk_label_sel_trace="default",
    legend_position="left",
    trace_colors=[],
    trace_dash=[],
    trace_width=[],
    current_anno=None,
    graph_font="Arial",
    x_axis_ticks="None",
    y_axis_ticks="None",
    pk_label_arrow=True,
    pk_label_angle=0,
    pk_label_line_length=35,
):

    if trace_dash is None or len(trace_dash) != len(df.columns[1:]):
        trace_dash = []
        for i, _ in enumerate(df.columns[1:]):
            trace_dash.append("solid")

    if trace_width is None or len(trace_width) != len(df.columns[1:]):
        trace_width = []
        for i, _ in enumerate(df.columns[1:]):
            trace_width.append(1.25)

    trace_colors_default = pltcolors.copy()
    if trace_colors is not None and "Custom" not in trace_colors:
        for i, val in enumerate(trace_colors):
            if val is not None:
                trace_colors_default[i] = trace_colors[i]

    # print("\n\n INSIDE CUSTOM PLOT")
    # print("\n\n trace_colors:", trace_colors)
    # print("\n trace_colors_default:", trace_colors_default)

    fig = go.Figure(layout=primary_layout)

    fig.update_layout(
        margin=dict(l=0, r=50, t=30, b=50),
        font_family=graph_font,
        font_color="black",
        font_size=16,
        title_font_family=graph_font,
        title_font_color="black",
        title_font_size=16,
        legend_title_font_color="black",
        legend_title_font_size=16,
        # uirevision="dash",
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
        # TODO: figure out how to persist uirevision when autorange="reversed"
        fig.update_layout(xaxis=dict(autorange="reversed"))
    else:
        fig.update_layout(uirevision="persist")

    # Option to hide a reference trace (e.g. TIC trace for combined TIC/UV plots)
    trace_idx = [(i + 1) for i in range(len(df.columns) - 1)]

    if hide_reference_trace:
        offset = stack_value * (len(trace_idx) - 1)
        ref_idx = df.columns.get_loc(reference_trace)
        del trace_idx[ref_idx - 1]
        for col_idx in trace_idx:

            fig.add_trace(
                go.Scatter(
                    x=df.iloc[:, 0],
                    y=df.iloc[:, col_idx] + offset,
                    mode="lines",
                    line_shape="spline",
                    name=df.columns[(col_idx)],
                    line=dict(
                        color=trace_colors_default[col_idx - 1],
                        width=trace_width[col_idx - 1],
                        dash=trace_dash[col_idx - 1],
                    ),
                    # uid="testTrace",
                )
            )
            offset -= stack_value

    else:
        offset = stack_value * (len(trace_idx) - 1)
        for i in range(len(df.columns) - 1):

            fig.add_trace(
                go.Scatter(
                    x=df.iloc[:, 0],
                    y=df.iloc[:, (i + 1)] + offset,
                    mode="lines",
                    line_shape="spline",
                    name=df.columns[(i + 1)],
                    line=dict(
                        color=trace_colors_default[i],
                        width=trace_width[i],
                        dash=trace_dash[i],
                    ),
                )
            )

            offset -= stack_value

    layout_data = {}
    if pk_labeling:

        all_annotations = create_annotations(
            df,
            pk_labels,
            pk_label_sel_trace,
            pk_label_indexes,
            stack_value,
            pk_label_arrow=pk_label_arrow,
            pk_label_angle=pk_label_angle,
            pk_label_line_length=pk_label_line_length,
        )

        for anno in all_annotations:
            fig.add_annotation(anno)

        # print("figure layout annotations: \n: ", fig["layout"]["annotations"])
        if current_anno:
            # print("\ncurrent_anno: ", current_anno)
            for index, annotations in enumerate(fig["layout"]["annotations"]):
                update_annos = [
                    "ax",
                    "ay",
                    "x",
                    "y",
                    "text",
                    "arrowhead",
                    "textangle",
                ]
                for anno in update_annos:
                    if current_anno.get(f"annotations[{index}].{anno}"):
                        fig["layout"]["annotations"][index][
                            anno
                        ] = current_anno.get(f"annotations[{index}].{anno}")
                    layout_data[f"annotations[{index}].{anno}"] = annotations[
                        anno
                    ]

    fig.update_xaxes(
        showline=True,
        linewidth=1,
        linecolor="black",
        ticks="outside",
        tickwidth=1,
        tickcolor="black",
        ticklen=8,
        # tickformat=tick_label_formatter(df.iloc[-1,0]),
        tickformat=".6",  # anything above 1e6 gets formatted as sci notation
        mirror=True,
        minor=MINOR_TICKS[x_axis_ticks],
        ticklabelstep=2,
        tickmode="auto",
        tickangle=0,
        nticks=20,
        # rangemode="tozero"
    )
    fig.update_yaxes(
        showline=True,
        linewidth=1,
        linecolor="black",
        ticks="outside",
        tickwidth=1,
        tickcolor="black",
        ticklen=8,
        tickformat=".6",  # anything above 1e6 gets formatted as sci notation
        mirror=True,
        minor=MINOR_TICKS[y_axis_ticks],
        ticklabelstep=2,
        tickmode="auto",
        tickangle=0,
        nticks=15,
    )

    max_y = 1.10 * df[df.columns[1:]].max(axis=1).max()
    min_y = 1.10 * df[df.columns[1:]].min(axis=1).min()

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
    fig["data"][0]["name"] = df.columns[trace_idx[0]]

    # print("fig: \n", fig)
    # print("\nlayout_data: ", layout_data)
    return fig, layout_data


def create_annotations(
    df,
    pk_labels,
    pk_label_sel_trace,
    pk_label_indexes,
    stack_value,
    pk_label_arrow=True,
    pk_label_angle=0,
    pk_label_line_length=35,
):
    """Creates plotly figure annotations from a peak label list.
    A dataframe is passed in so that x and y values for the
    label positions can be determined based on pre-determined index
    values.  The stack value allows a vertical offset based on
    the Stack Traces slider input.
    """
    if pk_label_arrow == True:
        pk_label_arrow = 2

    else:
        pk_label_arrow = 0

    # For peak labeling find top y value
    if pk_label_sel_trace == "default":
        top_y_val = np.asarray(df.iloc[:, -1])
    else:
        top_y_val = np.asarray(df[pk_label_sel_trace])

    x_val = np.asarray(df.iloc[:, 0])
    trace_idx = [(i + 1) for i in range(len(df.columns) - 1)]
    sel_trace_col_idx = df.columns.get_loc(pk_label_sel_trace)
    offset = stack_value * (len(trace_idx) - (sel_trace_col_idx))

    all_annotations = []
    for i, pk_idx in enumerate(pk_label_indexes):
        anno = dict(
            x=x_val[pk_idx],
            y=top_y_val[pk_idx] + offset,
            text=pk_labels[i],
            xref="x",
            yref="y",
            showarrow=True,
            # arrowhead=2,
            arrowhead=pk_label_arrow,
            ax=0,
            ay=-pk_label_line_length,
            clicktoshow="onoff",
            standoff=2,
            font=dict(color="black", size=14),
            # textangle=0,
            textangle=pk_label_angle,
            xanchor="center",
        )
        all_annotations.append(anno)

    return all_annotations


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


def create_pk_align_fig(df_cen_chk, all_ctrs=[]):
    linewidth = 1.2
    fig = go.Figure(layout=primary_layout)
    # Add traces
    for i in range(len(df_cen_chk.columns) - 1):

        fig.add_trace(
            go.Scatter(
                x=df_cen_chk.iloc[:, 0],
                y=df_cen_chk.iloc[:, (i + 1)]
                + i * 0.03 * df_cen_chk.iloc[:, (i + 1)].max(),
                mode="lines",
                name=df_cen_chk.columns[(i + 1)],
                line=dict(color=pltcolors[i], width=linewidth),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=df_cen_chk.iloc[all_ctrs[i], 0],
                y=df_cen_chk.iloc[all_ctrs[i], (i + 1)]
                + i * 0.03 * df_cen_chk.iloc[all_ctrs[i], (i + 1)].max()
                + 0.1 * df_cen_chk.iloc[all_ctrs[i], (i + 1)].max(),
                marker=dict(
                    size=14,
                    color=pltcolors[i],
                    symbol="diamond-tall-dot",
                    line=dict(width=1, color="DarkSlateGrey"),
                ),
                mode="markers",
                name=None,  # f"{df_cen_chk.columns[(i + 1)]} pk max",
                showlegend=False,
            )
        )
    # print("\nReturning peak alignment figure\n")
    return fig


def create_cow_pk_align_fig(df):
    linewidth = 1.2
    fig = go.Figure(layout=primary_layout)
    # Add traces
    for i in range(len(df.columns) - 1):

        fig.add_trace(
            go.Scatter(
                x=df.iloc[:, 0],
                y=df.iloc[
                    :, (i + 1)
                ],  # + i * 0.03 * df.iloc[:, (i + 1)].max(),
                mode="lines",
                name=df.columns[(i + 1)],
                line=dict(color=pltcolors[i], width=linewidth),
            )
        )

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
        a_max / 10**delta_mag - a_min / 10**delta_mag
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
