import pandas as pd

import urllib.parse


from ..trace_compare import overlap, wsd, R2, dca
from .generate_html_table import generate_table


def trace_comparisons(df, reference_trace):
    trace_compare_df = pd.DataFrame(
        columns=[
            "Sample",
            "Area of Overlap",
            "Weighted Spectral Difference",
            "R2",
            "DCA",
        ]
    )

    for i in range(int(len(df.columns)) - 1):
        x = df.iloc[:, 0].values
        y = df[reference_trace].values
        y_compare = df.iloc[:, i + 1].values
        overlap_val = overlap(x, y, y_compare)
        wsd_val = wsd(y, y_compare)
        r2_val = R2(y, y_compare)
        dca_val = dca(x, y, y_compare)

        trace_compare_df.loc[i] = [
            df.columns[i + 1],
            overlap_val,
            wsd_val,
            r2_val,
            dca_val,
        ]

    trace_compare_df["Area of Overlap"] = trace_compare_df["Area of Overlap"].map(
        "{:,.4f}".format
    )
    trace_compare_df["Weighted Spectral Difference"] = trace_compare_df[
        "Weighted Spectral Difference"
    ].map("{:,.4f}".format)
    trace_compare_df["R2"] = trace_compare_df["R2"].map("{:,.4f}".format)
    trace_compare_df["DCA"] = trace_compare_df["DCA"].map("{:,.4f}".format)

    trace_compare_csv_string = trace_compare_df.to_csv(
        index=False, encoding="utf-8-sig"
    )
    trace_compare_csv_string = "data:text/csv;charset=utf-8-sig," + urllib.parse.quote(
        trace_compare_csv_string
    )

    return generate_table(trace_compare_df), trace_compare_csv_string
