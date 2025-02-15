from .ftir_band_assignments import yang_h20_2015, yang_h20_2015_w_side_chains
import numpy as np
import pandas as pd
import math
from scipy import optimize

def interpolate_dataframe(df):
    """
    Interpolates a DataFrame with an 'x' column and multiple 'y' columns.
    The interpolation is performed on all columns except 'x', which is used as the index.
    
    Parameters:
        df (pd.DataFrame): Original DataFrame with 'x' as one of the columns.
        
    Returns:
        pd.DataFrame: New DataFrame with 'x' spaced at every integer unit and
                      the y columns interpolated accordingly.
    """
    # Make a copy to avoid modifying the original DataFrame
    df = df.copy()
    
    x_name = df.columns[0]
    # Set 'x' as the index
    df.set_index(x_name, inplace=True)
    
    # Create a new index that spans from the minimum to the maximum value of x, inclusive
    new_index = np.arange(df.index.min(), df.index.max() + 1)
    
    # Reindex the DataFrame so that all x values are present (new rows will have NaNs)
    df = df.reindex(new_index)
    
    # Interpolate the missing values for all columns using linear interpolation
    df = df.interpolate(method='linear')
    
    # Reset the index to bring x_name back as a column and keep the original column names
    df = df.reset_index().rename(columns={'index': x_name})
    
    return df

def guess_heights(df, col, center_list, gain=0.95):
    """Determines guesses for the heights based on measured data.

    Function creates an integer mapping to the measured frequencies, and then
    creates an initial peak height guess of gain*actual height at x=freq*. A
    Default of 0.95 seems to work best for most spectra, but can be change to
    improve convergence.

    Parameters
    ----------
    df : Dataframe
        Dataframe containing the measured absorbance data

    col : string or integer
        Column index for the absorbance data being fit. Accepts either index
        or string convention.

    center_list : iterable of integers
        An iterable of integer peak positions used to find the experiment
        absorbance at a given wavenumber. I.e, the heights are returned at the
        center values in this iterable

    gain : number (optional)
        Fraction of the measured absorbance value to use determine the initial
        guess for the peak height. The value Default value is 0.95, and thus
        by default, all initial peak guesses are 95% of the peak max.

    """
    heights = []
    freq_map = {}
    # print("df cols inside guess_heights: ", df.columns)
    df = interpolate_dataframe(df.copy())
    for i in df.iloc[:, 0]:
        j = math.floor(i)
        freq_map[j] = float(df[col].get(df.iloc[:, 0] == i).item())
    for i in center_list:
        height = freq_map[i]
        heights.append(gain * height)
    return heights

def gaussian_least_squares(df, col, peaks=yang_h20_2015, peak_width=5, params=dict()):
    """
    Fit a sum of Gaussian peaks to y-data in a DataFrame using least-squares optimization.

    This function models the specified y-data column (or the second column by default) as a sum
    of Gaussian functions, using initial guesses for peak centers and heights provided via the
    'peaks' dictionary. It returns both the computed areas under each fitted Gaussian and the
    full optimization result.

    Parameters:
        df (pandas.DataFrame): DataFrame containing the x-data (in the first column) and y-data.
        col (str): Name of the y-data column. If not provided, the second column is used.
        peaks (dict, optional): Dictionary with expected peak parameters, including:
            - "means": Expected centers for the Gaussian peaks.
            - "uncertainties": Uncertainty bounds for the peak centers.
            Default is yang_h20_2015.
        peak_width (float, optional): Initial guess for the width of each Gaussian peak. Default is 5.
        params (dict, optional): Additional keyword arguments for the least-squares optimizer.

    Returns:
        tuple: A tuple containing:
            - areas (list): List of the areas under each fitted Gaussian peak.
            - res: The optimization result object from scipy.optimize.least_squares.
    """
    if not col:
        col = df.columns[1]
    # print("col: ", col)
    def fun(p, x, y):
        """
        Define the objective function for the least-squares optimization.
        This function calculates the difference between the sum of Gaussians (model)
        and the observed data for given parameters 'p' over x-values 'x' and y-data 'y'.
        """
        return gaussian_sum(x, *p) - y

    # Concatenate the first column (assumed to be x-data) and the specified y-data column,
    # then convert to a NumPy array. The resulting array 'data' has two columns: x and y.
    data = np.array(pd.concat([df.iloc[:, 0], df[col]], axis=1))

    # Generate initial guesses for the peak heights using a helper function.
    # 'peaks["means"]' provides the expected centers of the peaks.
    # print("data: ", data)
    # print("df.head")
    heights = guess_heights(df.copy(), col, peaks["means"], gain=1.0)
    # Initialize lists for lower bounds (lb), upper bounds (ub), and the initial guess (guess)
    # for the optimization. Each Gaussian peak is modeled with three parameters:
    # [height, center (mean), width].
    lb = list()
    ub = list()
    guess = list()

    # Loop over each expected peak. For each peak, use the provided mean, uncertainty bounds,
    # and the guessed height to build the parameter arrays.
    for mean, bound, height in zip(peaks["means"], peaks["uncertainties"], heights):
        # Lower bounds:
        # - Height must be non-negative (>= 0)
        # - Center is bounded by the lower uncertainty bound (bound[0])
        # - Width must be non-negative (>= 0)
        lb.extend([0, bound[0], 0])

        # For the upper bound of the height:
        # If the guessed height is non-positive, allow an unbounded (infinite) height;
        # otherwise, use the guessed height as the upper limit.
        ubh = np.inf if height <= 0 else height

        # Upper bounds:
        # - Height is limited by 'ubh'
        # - Center is limited by the upper uncertainty bound (bound[1])
        # - Width is set to the provided 'peak_width'
        ub.extend([ubh, bound[1], peak_width])

        # Initial guess for each parameter:
        # - Use 95% of the guessed height (to start slightly below the guess)
        # - Use the provided mean as the center guess
        # - Use 'peak_width' as the initial width guess
        guess.extend([height * 0.95, mean, peak_width])

    # Prepare arguments for the least-squares optimization function:
    # 'fun' is the function to minimize and 'np.array(guess)' is the flattened initial guess.
    args = [fun, np.array(guess)]

    # Update the 'params' dictionary with additional required arguments:
    # - 'args': a tuple containing the x and y data extracted from the 'data' array.
    # - 'bounds': a tuple of lower and upper bounds for the parameters.
    params["args"] = (data[:, 0], data[:, 1])
    params["bounds"] = (np.array(lb), np.array(ub))

    # Run the least-squares optimization to fit the sum of Gaussians to the data.
    # The optimizer adjusts the parameters in 'guess' within the specified 'bounds'
    # to minimize the residual returned by 'fun'.
    # print("bounds: ", params["bounds"])
    res = optimize.least_squares(*args, **params)

    # After fitting, calculate the area under each fitted Gaussian.
    # The parameter vector 'res.x' is a 1-D array with groups of three parameters for each peak:
    # [height, center, width]. Iterate over this array in steps of 3.
    areas = list()
    centers = list()
    for i in range(0, len(res.x), 3):
        height = res.x[i]
        center = res.x[i + 1]
        width = res.x[i + 2]
        # Compute the area (integral) of the Gaussian with the given height and width.
        area = gaussian_integral(height, width)
        areas.append(area)
        centers.append(center)
    # print("centers: ", centers)
    # print("areas: ", areas)
    # print("res: ", res.x)
    # Return a tuple containing:
    # - 'areas': a list of the areas under each fitted Gaussian peak.
    # - 'res': the full result object from the least-squares optimization.
    return areas, res

def gaussian(x, height, center, width):
    """Function defining a gaussian distribution"""
    return height * np.exp(-((x - center) ** 2) / (2 * width**2))


def gaussian_sum(x, *args):
    """Returns the sum of the gaussian function inputs"""
    return sum(gaussian_list(x, *args))


def gaussian_list(x, *args):
    """Returns a list containing all gaussian component peaks passed in by *args"""
    if len(args) % 3 != 0:
        raise ValueError("Args must divisible by 3")
    gausslist = []
    count = 0
    for i in range(int(len(args) / 3)):
        gausstemp = gaussian(x, args[count], args[count + 1], args[count + 2])
        gausslist.append(gausstemp)
        count += 3

    gausslist = [
        np.where(gausslist[i] < 1.0e-30, 0.0, gausslist[i])
        for i, _ in enumerate(gausslist)
    ]

    # The gaussian peaks resulting from the curve fit often result in values
    # that are insanely small (e.g. < 1e-30) and should just be converted to zero

    return gausslist


def gaussian_integral(height, width):
    """Returns the integral of a gaussian curve with the given height, width
    and center
    """
    return height * width * math.sqrt(2 * math.pi)


def gaussians_to_df(df, gaussian_list_data, fitted_trace):
    tmp_col_names = [
        f"Gaussian {i+1}" for i, _ in enumerate(gaussian_list_data)
    ]
    gaussian_df = pd.DataFrame(gaussian_list_data).transpose()
    gaussian_df.columns = tmp_col_names
    gaussian_df.insert(0, df.columns[0], df.iloc[:, 0])
    gaussian_df.insert(1, fitted_trace, df[fitted_trace])
    gaussian_df.insert(2, "Model Fit", sum(gaussian_list_data))
    return gaussian_df
