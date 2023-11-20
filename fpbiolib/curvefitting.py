import numpy as np
import pandas as pd
from lmfit import Parameters


def component_pks(x, params, num_params, line_function):
    """function to create list of all fitted component peak y-values,
    with *params being a flat list containing peak function
    parameters corresponding to the number of peaks desired to be modeled.
    A note on using *args format in this function.  scipy.optimize.least_squares
    and lmfit will happily accept parameters as a list and will pass the list to the peak model functions.
    However,scipy.curve_fit unpacks the parameters list. To
    facilitate comparison of curve_fit vs lmfit vs least_squares, the functions
    were written to receive unpacked lists.
    """
    num_pks = int(len(params) / num_params)

    y_model_pks = []

    j = 0
    for i in range(num_pks):
        params_temp = params[
            j : (j + num_params)
        ]  # Grab a block of parameters to pass to model

        # Unpack params_temp to match the number of arguments in the function
        # calculate the function and append the peak to the y_model_pks
        y_model_pks.append(line_function(x, *params_temp))
        j += num_params

    y_model_pks = np.asarray(y_model_pks)

    # The gaussian peaks resulting from the curve fit often result in values
    # that are insanely small (e.g. < 1e-30) and should just be converted to zero
    y_model_pks = np.where(y_model_pks < 1.0e-30, 0.0, y_model_pks)

    return y_model_pks


def component_pks_sum(x_with_params: list, *flat_variable_params: list):
    """curve fitting and least squares minimization techniques
    depend on optimizing only the function parameters (i.e.
    flat_variable_params) and not the static parameters.
    A few workarounds:

      1. Static parameters (line_function, num_params) are
    defined outside the function.

      2. Create a dedicated function that has the static parameters
      defined within the function

      3. Pass in static parameters with the first argument (which
      is fixed by default and normally contains the x-values, or
      independent variable array), and then extract them

    Scipy curve_fit will unpack the parameters and pass them as multiple
    arguments, rather than as a list in the case of Scipy least_squares.
    Therefore, the * is required in this function to accept all
    the model parameters from curve_fit and pack them in a tuple,
    which gets passed to the function component_pks.
    """
    x = x_with_params[0]
    num_params = x_with_params[1][0]
    line_function = x_with_params[1][1]
    return sum(
        component_pks(x, flat_variable_params, num_params, line_function)
    )


def peak_area_pct(x, peaklist):
    pk_area = []
    for i in range(int(len(peaklist))):

        pk_area_tmp = np.trapz(
            peaklist[i], x
        )  # integrates individual fitted peak
        pk_area.append(pk_area_tmp)  # packs each peak area into a list

    pk_area_pct = []
    for i in range(int(len(peaklist))):
        pk_area_pct_temp = pk_area[i] / (sum(pk_area))
        pk_area_pct.append(pk_area_pct_temp)

        print(
            "Area {}  is {:1.2%} of the whole area".format(
                str(i + 1), pk_area[i] / (sum(pk_area))
            )
        )

    return pk_area_pct


def residuals(parameters, x, y, model):
    """function to take in function parameters
    pass them and the x, y values and method to create a
    set of component peaks using the specified model and
    then sum the peaks to create the overall peak profile.
    This peak sum is subtracted from the actual y-data
    to create an error function to minimize.
    When lmfit is used to pass parameters, they are of
    a class object Parameters and need to get converted
    to a list for the function to work
    """
    # print('parameters: ', parameters)
    # print('x: ', x)
    # print('y: ', y)
    # print('model: ', model)
    if isinstance(parameters, Parameters):
        parameters = list(parameters.valuesdict().values())

    """Can't pass any static parameters to the model function
    when using a minimizer, since all parameters will get
    varied as part of the minimizer algorithm.
    """

    return y - model(x, *parameters)


def loss_function(params, data_x, data_y, model, verbose, reducer):
    """
    This is a really generic loss function.
    It can take in any number of params, any generic model.

    Notice that the params are passed *first*.
    This is because of the way scipy's libraries need the funct
    ion to be formatted.
    """
    # loss = pow(residuals(params, data_x, data_y, model, verbose), 2.).sum()
    loss = reducer(residuals(params, data_x, data_y, model, verbose))
    if verbose:
        print(loss)
    return loss


def fitted_lines_to_df(df, fitted_lines: list, sel_trace: str):
    tmp_col_names = [f"Fitted line {i+1}" for i, _ in enumerate(fitted_lines)]
    fit_df = pd.DataFrame(fitted_lines).transpose()
    fit_df.columns = tmp_col_names
    fit_df.insert(0, df.columns[0], df.iloc[:, 0])
    fit_df.insert(1, sel_trace, df[sel_trace])
    fit_df.insert(2, "Model Fit", sum(fitted_lines))
    return fit_df
