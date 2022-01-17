import base64
import io
import pandas as pd

from collections import OrderedDict
import re, struct

from .df_transforms import many_x_y_to_x_many_y, x_many_y_interpolate

from .df_cleanup import cleanup_df_import, downcast_floats_and_ints


# File parsing and temporary dataframe storage functions

def du_800_file_converter(fname):
    f = open(fname, "rb")
    s = f.read()

    sample_name_start_hex_string = b'\x0cBaseProperty\x01\x00\x00\x00'

    # loop through the entire file string, s, and find the start positions of all the sample data
    sample_name_start_positions = [m.end() + 1 for m in re.finditer(sample_name_start_hex_string, s)]

    sample_names = []
    for position in sample_name_start_positions:
        f.seek(position)
        read_temp = f.read(200)
        sample_text_end_position = [m.start() for m in re.finditer(b'\x01\x01\x00\x00\x00', read_temp)][0]
        f.seek(position)
        sample_name = f.read(sample_text_end_position).decode("utf-8")
        sample_name = sample_name.replace('\n', ' ')
        sample_name = sample_name.replace('\x00', '')
        sample_names.append(sample_name)

    # Each data set appears to start with the following
    data_start_hex_string = b'\x07DpoData'

    # loop through the entire file string, s, and find the start positions of all the sample data
    wavelength_start_positions = [m.start() + 44 for m in re.finditer(data_start_hex_string, s)]

    uv_dataset = OrderedDict()
    i = 0
    for position in wavelength_start_positions:
        '''
        seek to the file position where the wavelength parameters are located, and build the wavelength dataset
        '''
        f.seek(position)
        st_wv = struct.unpack('<d', f.read(8))[0]
        end_wv = struct.unpack('<d', f.read(8))[0]
        step = struct.unpack('<d', f.read(8))[0]

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

        uv_dataset[f'{sample_names[i]} Wavelength (nm)'] = wavelength_data
        uv_dataset[f'{sample_names[i]}'] = absorbance_data
        i += 1

    sample_df = pd.DataFrame(uv_dataset)
    sample_df_clean = many_x_y_to_x_many_y(sample_df)
    return sample_df_clean


def du800(df):
    df = df.reset_index()
    num_cols = len(df.columns)
    samps = [df.iloc[25+i,1] for i in range(num_cols-1)]
    cols = ['Wavelength (nm)'] + samps
    df = df[25+num_cols:]
    df.columns = cols    
    df = df.apply(pd.to_numeric, errors = 'coerce')
    df = df.reset_index(drop=True)
    return df
    
def du800_v2(df):
    # df = df.reset_index() # this is needed in the dash app!
    filt1 = df.iloc[:, 0] == 'Scan Speed:'
    idx1 = df.index[filt1][0]
    
    filt2 = df.iloc[:, 0] == 'nm'
    idx2 = df.index[filt2][0]
    
    num_cols = idx2-idx1-2
    samps = [str(df.iloc[26+i,1]) + ' ' + str(df.iloc[26+i, 3]).replace('nan', '') for i in range(num_cols)]
    # print(samps)
    cols = ['Wavelength (nm)'] + samps
    df.drop(df.columns[(num_cols+1):], axis = 1, inplace = True)
    df = df[27+num_cols:]
    df.columns = cols    
    df = df.apply(pd.to_numeric, errors = 'coerce')
    df = df.reset_index(drop=True)
    return df

def parse_data(contents, filename):
    """
    Parse uploaded tabular file and return dataframe.
    """

    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)

    try:
        if "csv" in filename:
            # Assume that the user uploaded a CSV or TXT file
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        elif "xls" in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        elif "txt" or "tsv" in filename:
            # Assume that the user upl, delimiter = r'\s+'oaded an excel file
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), delimiter=r"\s+")
    except Exception as e:
        print(e)
        raise

    return df

def parse_du800_csv_data(contents, filename):
    '''
    Parse uploaded tabular file and return dataframe.
    '''

    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    try:
        # Assume that the user uploaded a CSV or TXT file
        # DU800 csv files usually have a single cell in row 1,
        # which causes issues with reading the csv,
        # current fix is to generate a bunch of columns, then delete them later
        col_names = [f"Col{a}" for a in range(100)]
        df = pd.read_csv(
            io.StringIO(decoded.decode('utf-8')),
            names=col_names
            )
    except Exception as e:
        print(e)
        raise

    return df

def parse_du800_dux_data(contents, filename):
    '''
    Parse uploaded tabular file and return dataframe.

    For now, need to recreate the uploaded binary dux file
    to use functions like f.seek when parsing the file
    '''

    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    # print("DECODED: ", decoded)
    tempFile = open("tempfile.dux", "wb")
    tempFile.write(decoded)

    try:
        df = du_800_file_converter('tempfile.dux')
        # print("df inside parse: ", df.head())
    except Exception as e:
        print(e)
        raise

    return df

def parse_uploaded_traces(contents, filenames, changed_id):
    # Create empty list to enable multiple file concatination
    appended_df = []
    uploaded_trace_filenames = []
    for name in filenames:
        file_txt = name + "; "
        uploaded_trace_filenames.append(file_txt)
    uploaded_trace_filenames.insert(0, "Uploaded: ")

    if "x_many_y_button" in changed_id:
        try:
            for content, filename in zip(contents, filenames):
                df_i = parse_data(content, filename)

                df_i = cleanup_df_import(df_i)

                df_i = downcast_floats_and_ints(df_i)

                appended_df.append(df_i.iloc[:, 1:])
                x_data = df_i.iloc[:, 0]  # x-data for the merged dataset
            appended_df.insert(0, x_data)
            df_i_concat = pd.concat(appended_df, axis=1)
            df = df_i_concat.sort_values(by=df_i_concat.columns[0])
            df.reset_index(drop=True, inplace=True)

            df = x_many_y_interpolate(df)
            x_min = df.iloc[0, 0]
            x_max = df.iloc[-1, 0]
            import_status = "success"
        except:
            df = pd.DataFrame()
            x_min = 0
            x_max = 0
            import_status = 'error'    
    elif 'beckman_csv_button' in changed_id:
        try:
            for content, filename in zip(contents, filenames):
                df_i = parse_du800_csv_data(content, filename)
                
                df_i = du800_v2(df_i)

                df_i = downcast_floats_and_ints(df_i)

                appended_df.append(df_i.iloc[:, 1:])
                x_data = df_i.iloc[:,0] #x-data for the merged dataset
            appended_df.insert(0, x_data)
            df_i_concat = pd.concat(appended_df, axis=1)
            df = df_i_concat.sort_values(by=df_i_concat.columns[0])
            df.reset_index(drop=True, inplace=True)

            x_min=df.iloc[0,0]
            x_max=df.iloc[-1,0]
            import_status = 'success'
        except:
            df = pd.DataFrame()
            x_min = 0
            x_max = 0
            import_status = 'error'        
    elif 'beckman_dux_button' in changed_id:
        try:
            for content, filename in zip(contents, filenames):
                df_i = parse_du800_dux_data(content, filename)
                
                df_i = downcast_floats_and_ints(df_i)

                appended_df.append(df_i.iloc[:, 1:])
                x_data = df_i.iloc[:,0] #x-data for the merged dataset
            appended_df.insert(0, x_data)
            df_i_concat = pd.concat(appended_df, axis=1)
            df = df_i_concat.sort_values(by=df_i_concat.columns[0])
            df.reset_index(drop=True, inplace=True)

            x_min=df.iloc[0,0]
            x_max=df.iloc[-1,0]
            import_status = 'success'
        except:
            df = pd.DataFrame()
            x_min = 0
            x_max = 0
            import_status = 'error'            
    else:
        try:
            for content, filename in zip(contents, filenames):
                df_i = parse_data(content, filename)
                df_i = cleanup_df_import(df_i)
                df_i = downcast_floats_and_ints(df_i)
                df_i = many_x_y_to_x_many_y(df_i)
                df_i_y = df_i.iloc[:, 1:]
                x_data = df_i.iloc[:, 0]
                appended_df.append(df_i_y)

            appended_df.insert(0, x_data)

            df_i_concat = pd.concat(appended_df, axis=1)
            df = df_i_concat.sort_values(by=df_i_concat.columns[0])
            df.reset_index(drop=True, inplace=True)
            x_min = df.iloc[0, 0]
            x_max = df.iloc[-1, 0]
            import_status = "success"
        except:
            df = pd.DataFrame()
            x_min = 0
            x_max = 0
            import_status = "error"

    cols = pd.Series(df.columns)

    # rename any duplicate column names
    for dup in cols[cols.duplicated()].unique():
        cols[cols[cols == dup].index.values.tolist()] = [
            dup + "." + str(i) if i != 0 else dup for i in range(sum(cols == dup))
        ]

    # rename the columns with the cols list.
    df.columns = cols.to_list()

    return uploaded_trace_filenames, df, import_status, x_min, x_max
