import base64
import csv
import io
import re
import struct
from collections import OrderedDict
from pathlib import Path

import numpy as np
import pandas as pd
from chemlabparser.parser import FileReader
from scipy.io.netcdf import NetCDFFile

from fpbiolib.df_cleanup import (
    cleanup_df_import,
    downcast_floats_and_ints,
    fix_duplicate_col_names,
)
from fpbiolib.df_transforms import x_many_y_to_many_x_y

# File parsing and temporary dataframe storage functions


def parse_uploaded_files(contents, filenames, parser):
    """Create dataframes based on type of file loaded
    and parser function.  Since the user can click-select
    multiple files we need to append each parsed file's
    dataframe to a list and then concatenate them.
    """
    try:
        dfs = []
        for content, filename in zip(contents, filenames):
            content_type, content_string = content.split(",")
            b64_content = base64.b64decode(content_string)
            df_i = parser(b64_content, filename)
            dfs.append(df_i)

        df = pd.concat(dfs, axis=1)

        df = cleanup_df_import(df)
        df = fix_duplicate_col_names(df)
        df = downcast_floats_and_ints(df)
        df.reset_index(drop=True, inplace=True)
        upload_error = False

    except Exception:
        print("Incompatible file, returning empty dataframe")
        df = pd.DataFrame()
        upload_error = True

    return df, upload_error


def parse_filereader_parser_data(content, filename):
    try:
        # print("filename: ", filename)
        fr = FileReader(filename=filename, decoded_file_contents=content)
        # print("\nfr: \n", fr)
        # print("fr filename: ", fr.fullpath, fr.filename)
        # print("\nsuffix: ", str(fr.filename.suffix).upper())
        # TODO work on ascending dataframes!
        if str(fr.filename.suffix).upper() == ".DSX":
            df = fr.parser.average_traces_df
        else:
            df = fr.parser.df
        df = df.sort_values(by=df.columns[0])

    except Exception as e:
        print(e)
        raise

    return df


def parse_x_many_y_data(content, filename):
    """
    Parse uploaded tabular file and return dataframe.
    """

    try:
        if "csv" in filename.lower():
            # Assume that the user uploaded a CSV or TXT file
            df = pd.read_csv(io.StringIO(content.decode("utf-8")))
            # print('csv loaded')
            # print('df head: \n', df.head())
        elif "xls" in filename.lower():
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(content))
        elif "txt" or "tsv" in filename.lower():
            # Assume that the user upl, delimiter = r'\s+'oaded an excel file
            df = pd.read_csv(io.StringIO(content.decode("utf-8")), delimiter=r"\s+")

        # Last row has nan values, let's drop those, cleanup and sort
        # by ascending wavelength
        df = cleanup_df_import(df)
        df = fix_duplicate_col_names(df)
        df = df.apply(pd.to_numeric)
        if df.iloc[0, 0] > df.iloc[-1, 0]:
            df.sort_values(by=df.columns[0], inplace=True)

        """
        to allow multiple files to be concatenated
        need to create many_x_y and then recombine
        after concatenation
        """
        df = x_many_y_to_many_x_y(df)

    except Exception as e:
        print(e)
        raise

    return df


def parse_many_x_y_data(content, filename):
    """
    Parse uploaded tabular file and return dataframe.
    """

    try:
        if "csv" in filename.lower():
            # Assume that the user uploaded a CSV or TXT file
            df = pd.read_csv(io.StringIO(content.decode("utf-8")))
            # print('csv loaded')
            # print('df head: \n', df.head())
        elif "xls" in filename.lower():
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(content))
        elif "txt" or "tsv" in filename.lower():
            # Assume that the user upl, delimiter = r'\s+'oaded an excel file
            df = pd.read_csv(io.StringIO(content.decode("utf-8")), delimiter=r"\s+")

        # Last row has nan values, let's drop those, cleanup and sort
        # by ascending wavelength
        df = cleanup_df_import(df)
        df = fix_duplicate_col_names(df)
        df = df.apply(pd.to_numeric)
        if df.iloc[0, 0] > df.iloc[-1, 0]:
            df.sort_values(by=df.columns[0], inplace=True)

    except Exception as e:
        print(e)
        raise

    return df


def parse_du800_csv_data(content, filename):
    """
    Parse uploaded tabular file and return dataframe.
    """

    try:
        # Assume that the user uploaded a CSV or TXT file
        # DU800 csv files usually have a single cell in row 1,
        # which causes issues with reading the csv,
        # current fix is to generate a bunch of columns, then delete them later
        col_names = [f"Col{a}" for a in range(100)]
        df = pd.read_csv(io.StringIO(content.decode("utf-8")), names=col_names)

        # df = df.reset_index() # this is needed in the dash app!
        filt1 = df.iloc[:, 0] == "Scan Speed:"
        idx1 = df.index[filt1][0]

        filt2 = df.iloc[:, 0] == "nm"
        idx2 = df.index[filt2][0]

        num_cols = idx2 - idx1 - 2
        samps = [
            str(df.iloc[26 + i, 1]) + " " + str(df.iloc[26 + i, 3]).replace("nan", "")
            for i in range(num_cols)
        ]
        # print(samps)
        cols = ["Wavelength (nm)"] + samps
        df.drop(df.columns[(num_cols + 1) :], axis=1, inplace=True)
        df = df[27 + num_cols :]
        df.columns = cols

        df = cleanup_df_import(df)
        df = fix_duplicate_col_names(df)
        df = df.apply(pd.to_numeric)
        if df.iloc[0, 0] > df.iloc[-1, 0]:
            df.sort_values(by=df.columns[0], inplace=True)
        df = df.reset_index(drop=True)

        """
        to allow multiple files to be concatenated
        need to create many_x_y and then recombine
        after concatenation
        """
        df = x_many_y_to_many_x_y(df)

    except Exception as e:
        print(e)
        raise

    return df


def parse_du800_dux_data(content, filename):
    """
    Reads in Beckman DU-800 .dux file and returns
    many x,y dataframe
    """
    try:
        with io.BytesIO(content) as f:
            sample_name_start_hex_string = b"\x0cBaseProperty\x01\x00\x00\x00"

            # loop through the entire file string, s, and find the start positions of all the sample data
            sample_name_start_positions = [
                m.end() + 1 for m in re.finditer(sample_name_start_hex_string, content)
            ]

            sample_names = []
            for position in sample_name_start_positions:
                f.seek(position)
                read_temp = f.read(200)
                sample_text_end_position = [
                    m.start() for m in re.finditer(b"\x01\x01\x00\x00\x00", read_temp)
                ][0]
                f.seek(position)
                sample_name = f.read(sample_text_end_position).decode("utf-8")
                sample_name = sample_name.replace("\n", " ")
                sample_name = sample_name.replace("\x00", "")
                sample_names.append(sample_name)

            # Each data set appears to start with the following
            data_start_hex_string = b"\x07DpoData"

            # loop through the entire file string, s, and find the start positions of all the sample data
            wavelength_start_positions = [
                m.start() + 44 for m in re.finditer(data_start_hex_string, content)
            ]

            uv_dataset = OrderedDict()
            i = 0
            for position in wavelength_start_positions:
                """
                seek to the file position where the wavelength parameters are located, and build the wavelength dataset
                """
                f.seek(position)
                st_wv = struct.unpack("<d", f.read(8))[0]
                end_wv = struct.unpack("<d", f.read(8))[0]
                step = struct.unpack("<d", f.read(8))[0]

                # determine number of datapoints for wavelength data
                num_wv_data_pts = int(
                    abs(st_wv - end_wv) / step + 1
                )  # add 1 to include first data point in count

                wavelength_data = []
                for x in range(num_wv_data_pts):
                    inp_x = struct.unpack("<d", f.read(8))[0]
                    wavelength_data.append(inp_x)
                # The absorbance data starts 36 units after the end of the wavelength data
                f.read(36)

                absorbance_data = []
                for x in range(num_wv_data_pts):
                    inp_x = struct.unpack("<d", f.read(8))[0]
                    absorbance_data.append(inp_x)

                uv_dataset[f"{sample_names[i]} Wavelength (nm)"] = wavelength_data
                uv_dataset[f"{sample_names[i]}"] = absorbance_data
                i += 1

            df = pd.DataFrame(uv_dataset)

            df = cleanup_df_import(df)
            df = fix_duplicate_col_names(df)
            df = df.apply(pd.to_numeric)
            if df.iloc[0, 0] > df.iloc[-1, 0]:
                df.sort_values(by=df.columns[0], inplace=True)
            df = df.reset_index(drop=True)

    except Exception as e:
        print(e)
        raise

    return df


def parse_nanodrop_tsv_data(content, filename):
    """
    Parse uploaded tabular file and return x_many_y dataframe.
    """

    try:
        # Assume that the user uploaded a TSV wavelength file
        df = pd.read_csv(
            io.StringIO(content.decode("utf-8")),
            sep="\t+",
            engine="python",
            names=["col1", "col2"],
        )

        """
        Convert a raw tsv imported with pandas in the format
        pd.read_csv(fname, sep='\t+', engine='python', names=['col1', 'col2'])
        to a single x, multi-y column dataframe, with sample
        names identified in the datafile
        """
        # date pattern in tsv file is a key file locator for the data
        date_pattern = re.compile(
            r"(?:[1-9]|1[0-2])/(?:[1-9]|[12][0-9]|3[01])/(?:19|20)\d\d"
        )

        # Sample name always precedes date by 1 index unit. For
        name_indices = df.index[
            df.iloc[:, 0].str.contains(date_pattern) == True
        ].tolist()
        name_indices[:] = [number - 1 for number in name_indices]

        # wavelength start of formal data always follows the
        # //QSpecEnd index by 1 index unit
        wv_st_indices = df.index[df.iloc[:, 0] == "//QSpecEnd:"].tolist()
        wv_st_indices[:] = [number + 1 for number in wv_st_indices]

        # wavelength end of formal data always precedes the
        # subsequent name index by 1 index unit
        wv_end_indices = [number - 1 for number in name_indices[1:]]
        wv_end_indices.append(df.tail(1).index.item())

        # create empty dataframe for holding the transformed data
        df_tsv = pd.DataFrame()

        # Just utilize the first sample dataset for the wavelength range since they are all the same
        df_tsv["Wavelength (nm)"] = (
            df.iloc[wv_st_indices[0] : wv_end_indices[0], 0]
            .reset_index(drop=True)
            .astype(float)
        )

        # Populate all the y-data
        for i in range(int(len(name_indices))):
            df_tsv[df.iloc[name_indices[i], 0]] = (
                df.iloc[wv_st_indices[i] : wv_end_indices[i], 1]
                .reset_index(drop=True)
                .astype(float)
            )

        df_tsv = cleanup_df_import(df_tsv)
        df_tsv = fix_duplicate_col_names(df_tsv)
        df_tsv = df_tsv.apply(pd.to_numeric)
        if df.iloc[0, 0] > df.iloc[-1, 0]:
            df.sort_values(by=df.columns[0], inplace=True)

        """
        to allow multiple files to be concatenated
        need to create many_x_y and then recombine
        after concatenation
        """
        df_tsv = x_many_y_to_many_x_y(df_tsv)

    except Exception as e:
        print(e)
        raise

    return df_tsv


def parse_solovpe_csv_data(content, filename):
    """
    Parse uploaded tabular file and return dataframe.
    """

    try:
        # Assume that the user uploaded a CSV wavelength file
        """
        Converts a raw SoloVPE formatted csv imported with pandas in the format
        to a single x, multi-y column dataframe, with sample
        names identified in the datafile
        """
        df = pd.read_csv(io.StringIO(content.decode("utf-8")))
        # Take the sample names from the header row and place them in row 0
        # above the absorbance data
        for i in range(0, int(len(df.columns)) - 1, 2):
            df.iloc[0, i + 1] = df.columns[i]

        # Replace the column names with row 0 and drop row 0
        df.columns = df.iloc[0]
        df.drop(0, inplace=True)

        # Last row has nan values, let's drop those, cleanup and sort
        # by ascending wavelength
        df = cleanup_df_import(df)
        df = fix_duplicate_col_names(df)
        df = df.apply(pd.to_numeric)
        if df.iloc[0, 0] > df.iloc[-1, 0]:
            df.sort_values(by=df.columns[0], inplace=True)

    except Exception as e:
        print(e)
        raise

    return df


def parse_waters_tab_arw_data(content, filename):
    try:
        df_temp = pd.read_csv(
            io.StringIO(content.decode("utf-8")), lineterminator="\r", header=1
        )
        df = df_temp[df_temp.columns[0]].str.split("\t", expand=True)
        df.columns = ["retention time", df_temp.columns[0]]
        df.drop(0, inplace=True)

        df = cleanup_df_import(df)
        df = fix_duplicate_col_names(df)
        df = df.apply(pd.to_numeric)
        if df.iloc[0, 0] > df.iloc[-1, 0]:
            df.sort_values(by=df.columns[0], inplace=True)

    except Exception as e:
        print(e)
        raise

    return df


# # stdlib
# import os
# from pathlib import Path

# # 3rd party
# from netCDF4 import Dataset  # type: ignore[import]

# def read_cdf_metadata(rootgrp: Dataset) -> dict:
#     cdf_metadata = {}
#     for name in rootgrp.ncattrs():
#         cdf_metadata[name] = getattr(rootgrp, name)
#     return cdf_metadata

# def read_cdf_data(rootgrp: Dataset) -> dict:
#     cdf_data = {}
#     for key, item in rootgrp.variables.items():
#         cdf_data[key] = item[:].data
#         if item == rootgrp.variables["ordinate_values"]:
#             uniform_sampling = item.uniform_sampling_flag

#     ydata = cdf_data.get("ordinate_values")

#     if uniform_sampling == "Y":
#         xstart = cdf_data["detector_minimum_value"]
#         xend = cdf_data["detector_maximum_value"]
#         num_points = len(ydata)
#         cdf_data["calculated_sampling_interval"] = (xend-xstart)/num_points

#         xdata = np.linspace(xstart, xend, num_points)

#         # if retention_unit is seconds for Waters cdf exports, may need this conversion...
#         if rootgrp.retention_unit == "seconds":
#             cdf_data["actual_delay_time"] = cdf_data["actual_delay_time"]/60
#             cdf_data["actual_sampling_interval"] = cdf_data["actual_sampling_interval"]/60
#     else:
#         xdata = cdf_data.get("raw_data_retention")
#     return xdata, ydata, cdf_data

# def read_cdf(content: bytes, filename: (str, Path)):
#     """Takes in either a file.read() datastream or
#     base64.b64decode(content_string) bytes content
#     from a Dash dcc.upload object and
#     a filename and returns the data / metadata"""

#     if not isinstance(filename, (str, Path)):
#         raise TypeError("'filename' must be a string or a pathlib.Path object")

#     filename = Path(filename)
#     rootgrp = Dataset('name', "r", memory=content, format="NETCDF3_CLASSIC")
#     print(f" -> Reading netCDF file '{filename}'")

#     cdf_metadata = read_cdf_metadata(rootgrp)
#     x, y, cdf_data = read_cdf_data(rootgrp)

#     if rootgrp.sample_name:
#         sample_name = f"{rootgrp.sample_name}...{filename.stem}...{cdf_metadata.get('detector_unit')}"
#     else:
#         sample_name = filename.stem

#     rootgrp.close()
#     return x, y, sample_name, cdf_metadata, cdf_data

# def parse_cdf_data2(content, filename):
#     try:
#         x, y, sample_name, cdf_metadata, _ = read_cdf(content, filename)
#         df = pd.DataFrame({"retention time (min)": x, sample_name: y})

#         df = cleanup_df_import(df)

#     except Exception as e:
#         print(e)
#         raise

#     return df


def parse_cdf_data1(content, filename):
    # print("\n\n Inside parse waters")
    try:
        f = NetCDFFile(io.BytesIO(content))

        tic = f.variables["ordinate_values"].data
        tic = tic.byteswap().newbyteorder()  # Convert big endian to LE, create array

        xstart = f.variables["detector_minimum_value"].data[()]
        xend = f.variables["detector_maximum_value"].data[()]
        num_points = len(tic)

        xdata = np.linspace(xstart, xend, num_points)

        filename = Path(filename)
        if f.sample_name:
            sample_name = f"{f.sample_name.decode('utf-8')}...{filename.stem}"
        else:
            sample_name = filename.stem

        f.close()

        df = pd.DataFrame({"retention time (min)": xdata, sample_name: tic})

        df = cleanup_df_import(df)

    except Exception as e:
        print(e)
        raise

    return df


def parse_trace_html_data(content, filename):
    """
    Create a dataframe of data embedded in html file by
    running through it with regular expressions
    """
    try:
        data_st_str = re.compile(
            r'"name":"([a-zA-Z0-9_.+\s-]+)","x":\[([^\]]+)\],"y":\[([^\]]+)'
        )  # grabs names and all characters (floats) NOT in brackets

        sample_names = [m.group(1) for m in data_st_str.finditer(content.decode())]

        x_data = [m.group(2).split(",") for m in data_st_str.finditer(content.decode())]

        x_data = [[float(x) for x in x_list] for x_list in x_data]

        y_data = [m.group(3).split(",") for m in data_st_str.finditer(content.decode())]

        y_data = [[float(y) for y in y_list] for y_list in y_data]

        df = pd.DataFrame()
        df["x_data"] = x_data[0]

        for i, sample_name in enumerate(sample_names):
            df[sample_name] = y_data[i]

        """
        to allow multiple files to be concatenated
        need to create many_x_y and then recombine
        after concatenation
        """
        df = x_many_y_to_many_x_y(df)
        # print("df cols: ", df.columns)

    except Exception as e:
        print(e)
        raise

    return df


def parse_params(contents, filename) -> dict:
    """
    Parse uploaded parameters file and return dict...
    """
    if contents is None or filename is None:
        return {}
    try:
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        if "csv" in filename.lower():
            # Assume that the user uploaded a CSV or TXT file
            # df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), index_col=0)

            data = csv.DictReader(io.StringIO(decoded.decode("utf-8")))

            params = {}
            for row in data:
                params[row["Parameter"]] = row["Value"]
            # print('csv loaded')
            # print('df head: \n', df.head())

    except Exception as e:
        print(e)
        raise

    return params


def parse_label_data(content, filename):
    """
    Parse uploaded tabular file and return dataframe.
    """

    try:
        if "csv" in filename.lower():
            # Assume that the user uploaded a CSV or TXT file
            df = pd.read_csv(io.StringIO(content.decode("utf-8")), dtype=str)
            # print('csv loaded')
            # print('df head: \n', df.head())
        elif "xls" in filename.lower():
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(content), dtype=str)
        elif "txt" or "tsv" in filename.lower():
            # Assume that the user upl, delimiter = r'\s+'oaded an excel file
            df = pd.read_csv(
                io.StringIO(content.decode("utf-8")),
                delimiter=r"\s+",
                dtype=str,
            )

        # Last row has nan values, let's drop those, cleanup and sort
        # by ascending wavelength
        df = cleanup_df_import(df)
        df = fix_duplicate_col_names(df)

    except Exception as e:
        print(e)
        raise

    return df
