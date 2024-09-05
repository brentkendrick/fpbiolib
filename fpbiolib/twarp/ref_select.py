import numpy as np
import plotly.graph_objects as go


def ref_select(y, x=None, options=None):

    """Interpolate a 1-D function.

    x and y are arrays of values used to approximate some function f: y = f(x). This class returns a function whose call method uses interpolation to find the value of new points.

    Parameters:
    x(m,) array_like
    A 1-D array of real values.

    y(n x m) array_like
    A n x m array of real values. The length of y along the interpolation axis must be equal to the length of x.
        ref,refs,N = ref_select(ydata,x,options);

    Assists in select a reference vector for warping
    Thomas Skov / Frans van den Berg 060515 (FvdB)

    in:  y (n x m) matrix - objects(samples) x variables(datapoints) - with data for warping/correction
         x (1 x m) Variable labels for plotting (e.g. number of columns)
         options list    1 : reference selection
                              0 - interactive (all options below - plotting is on)
                              1 - mean signal vector
                              2 - median signal vector
                              3 - bi-weighted mean (iterative, slow, but robust)
                              4 - maximum signal vector
                              5 - maximum cumulative produXmct of correlation coefficients
                         2 : plotting of the selection
                         default [0, 1] (interactive) type "ref_select" for more details

    out: ref (1 x m) target/reference vector selected
         refs (5 x m) target/reference vectors from all five methods
         N (1x1) if options(1) == 5 --> index in "y" of "ref" selected,
              otherwise []

    Authors:
    Thomas Skov / Frans van den Berg
    Royal Agricultural and Veterinary University - Department of Food Science
    Quality and Technology - Spectroscopy and Chemometrics group - Denmark
    email: thsk@kvl.dk / fb@kvl.dk - www.models.kvl.dk
    """

    yn, ym = y.shape
    # yn: number of signals that are to be aligned, ym: number of data points in each signal

    if not x or len(x) == 0:
        x = np.arange(1, ym + 1)

    if ym != len(x):
        raise Exception(
            'ERROR: number of entries in "variables" and number of columns in "y" must be the same'
        )

    if np.any(np.isnan(y)):
        raise Exception('ERROR: function "ref_select" can not handle missing values')

    N = 0
    refs = np.zeros((5, ym))  # creates (5, ym) array shape

    # user selects all options to be computed, set interactive to a value
    if options[0] == 0:
        interactive = 1
    else:
        interactive = None

    if (options[0] == 1) or interactive:
        refs[0, :] = np.mean(y, axis=0)
        if options[1] == 1 or interactive:
            fig = go.Figure()
            for i in range(yn):
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=y[i],
                        name=f"y{i + 1}",
                        mode="lines",
                        line_color="blue",
                    )
                )
            fig.add_trace(
                go.Scatter(x=x, y=refs[0, :], name=f"mean signal", mode="lines")
            )
            fig.update_layout(
                title="Reference (orange) = mean signal (criterion #1)",
                xaxis_title="x",
                yaxis_title="intensity",
                template="plotly_white",
            )
            fig.show()

    if (options[0] == 2) or interactive:
        refs[1, :] = np.median(y, axis=0)
        if options[1] == 1 or interactive:
            fig = go.Figure()
            for i in range(yn):
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=y[i],
                        name=f"y{i + 1}",
                        mode="lines",
                        line_color="blue",
                    )
                )
            fig.add_trace(
                go.Scatter(x=x, y=refs[1, :], name=f"median signal", mode="lines")
            )
            fig.update_layout(
                title="Reference (orange) = median signal (criterion #2)",
                xaxis_title="x",
                yaxis_title="intensity",
                template="plotly_white",
            )
            fig.show()

    if (options[0] == 3) or interactive:
        for a in range(ym):
            refs[2, a] = biwmean(y[:, a])
        if options[1] == 1 or interactive:
            fig = go.Figure()
            for i in range(yn):
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=y[i],
                        name=f"y{i + 1}",
                        mode="lines",
                        line_color="blue",
                    )
                )
            fig.add_trace(
                go.Scatter(x=x, y=refs[2, :], name=f"bwm signal", mode="lines")
            )
            fig.update_layout(
                title="Reference (orange) = bi-weighted mean signal (criterion #3)",
                xaxis_title="x",
                yaxis_title="intensity",
                template="plotly_white",
            )
            fig.show()

    if (options[0] == 4) or interactive:
        refs[3, :] = np.amax(y, axis=0)
        if options[1] == 1 or interactive:
            fig = go.Figure()
            for i in range(yn):
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=y[i],
                        name=f"y{i + 1}",
                        mode="lines",
                        line_color="blue",
                    )
                )
            fig.add_trace(
                go.Scatter(x=x, y=refs[3, :], name=f"max signal", mode="lines")
            )
            fig.update_layout(
                title="Reference (orange) = maximum signal (criterion #4)",
                xaxis_title="x",
                yaxis_title="intensity",
                template="plotly_white",
            )
            fig.show()

    if (options[0] == 5) or interactive:
        R = np.eye(yn)
        for a in range(yn - 1):
            for b in range(1, yn):
                xx1 = y[a, :] - np.sum(y[a, :]) / ym
                xx2 = y[b, :] - np.sum(y[b, :]) / ym
                R[a, b] = (
                    np.dot(xx1, xx2.T)
                    / (np.linalg.norm(xx1, 2) * np.linalg.norm(xx2, 2))
                ) ** 2
                R[b, a] = R[a, b]
        Rcp = np.prod(R, 2 - 1)
        N = Rcp.argmax()
        refs[4, :] = y[N, :]

        if options[1] == 1 or interactive:
            fig = go.Figure()
            for i in range(yn):
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=y[i],
                        name=f"y{i + 1}",
                        mode="lines",
                        line_color="blue",
                    )
                )
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=refs[4, :],
                    name=f"max prod of corr coefs",
                    mode="lines",
                )
            )
            fig.update_layout(
                title=f"Reference (orange) = maximum cumulative product of correlation coefficients (criterion #5)",
                xaxis_title="x",
                yaxis_title="intensity",
                template="plotly_white",
            )
            fig.show()

    if interactive:
        print("Enter number (1 - 5) from criterion choice above: ")
        chk = True
        while chk:
            choice = input()
            try:
                choice = int(choice)
                if choice <= 0 or choice > 5:
                    print("only numbers between 1 - 5 are allowed")
                else:
                    print("Choice = ", choice)
                    options[0] = choice
                    chk = False
            except:
                print("only numbers between 1 - 5 are allowed")

    ref = refs[options[0] - 1, :]

    return ref, refs, N


# Internal functions
def biwmean(x):
    nx = len(x)
    niqr = int(np.round(nx * 0.25))
    sx = np.sort(x)
    medianx = np.median(x)
    iqr = sx[nx - niqr - 1] - sx[niqr - 1]

    if 2 * iqr < np.finfo(float).eps:
        return medianx

    zx = (x - medianx) / (3 * iqr)
    biw = (1 - zx**2) ** 2
    biw[np.abs(zx) > 1] = 0
    biwm = np.sum(biw * x, axis=0) / np.sum(biw, axis=0)
    oldbiwm = medianx + np.finfo(float).eps
    iter = 0
    biwmiter = [biwm]
    while ((oldbiwm - biwm) ** 2 / oldbiwm**2) > 1e-8 and (iter <= 100):
        iter += 1
        zx = (x - biwm) / (3 * iqr)
        biw = (1 - zx**2) ** 2
        biw[np.abs(zx) > 1] = 0
        oldbiwm = biwm
        biwm = np.sum(biw * x, axis=0) / np.sum(biw, axis=0)
        biwmiter.append(biwm)
    return biwm


# def say_what():
#     disp('Explanation "reference selection" (options(1)):');
#     disp('0 - All the methods below are computed and shown, and the user can select her/his preferred method.');
#     disp('1 - The mean vector from matrix "y" is used as reference.');
#     disp('    Usually this results in a little broader/"wobbly" signal compared to the individual')
#     disp('    measurements due to the shifting.');
#     disp('2 - The median vector from matrix "y" is used as reference.');
#     disp('    Usually this is a little "sharper" then the choice 1 (mean).');
#     disp('3 - The so-called bi-weighted mean vector from matrix "y" is used as reference.');
#     disp('    This is based on a robust estimator somewhere between 1 (mean) and 2 (median).');
#     disp('4 - The reference vector is composed of the maximum value in each variable in matrix "y".');
#     disp('    This is a strange (and very broad) reference that is sometimes useful to see in which way the');
#     disp('    alignment correction "wants to go".');
#     disp('5 - The object from matrix "y" with the maximum cumulative product of correlation coefficients with');
#     disp('    all other objects (notice that this is the only criterion selecting a real sample).');
#     disp('    Each object get a score, e.g. score(1) = r(1,2)*r(1,3)*... , where r(1,2) is the (squared) correlation');
#     disp('    coefficient between object 1 and 2, etc. Object with the highest score matches best with all others,');
#     disp('    and is thus selected as reference');
#     disp(' ');
