import re
import time

import numpy as np

from .cow import cow
from .ref_select import ref_select


def optim_cow(y, optim_space, options=None, ref=np.array([])):
    """
    Translated from MATLAB to Python by B. Kendrick, Feb 2023

    Inputs come from warp_script06.m and include:
    optim_pars,OS,diagnos = optim_cow(y, [5 30 1 10], [1 3 50 0.15], ref);

    The routine automatically optimizes the segment length and slack size for COW
    alignment pre-processing.

    It does a "discrete-coordinates simplex" optimization (EVOP-like) for
    segment and slack parameters in COW alignment with so-called
    Warping Effect = "Simplicity" + Peak Factor
    FvdB/ThS 070305

        in:     y (n x m) data table with "n" objects(samples) and "m" variables(datapoints)
                optim_space [segment minimum, maximum, slack minimum, maximum]
                options [
                    trigger plot and progress text,
                    number of optimizations from grid maxima,
                    maximum number of optimization steps,
                    Fraction of maximal deviation from center in COW alignment
                ]
                    default [0 3 50 0.15] (no plot; 3 starts from 3 maxima in grid search;
                      maximum 50 steps; 15%)

                ref (1 x m) reference object used in COW alignment (vector); if omitted
                            reference is selected from the matrix "y" by "ref_select.m" with option 5

        out:    optim_pars [optimal segment length, slack size]
                OS (5 x N) optimization sequence (first row segment, second slack,
                                                third row "Warping Effect", fourth "Simplicity",
                                                Fifth "Peak Factor")
                diagnos (struct): simplicity raw data, total run time, start points for
                optimization (columns in OS), "optim_space" and warping results for
                optimum (path + aligned matrix + diagnostics)

        uses ref_select.m, cow.m

    Authors:
    Thomas Skov / Frans van den Berg
    Royal Agricultural and Veterinary University - Department of Food Science
    Quality and Technology - Spectroscopy and Chemometrics group - Denmark
    email: thsk@kvl.dk / fb@kvl.dk - www.models.kvl.dk
    """
    if not options or len(options) != 4:
        options = [0, 3, 50, 0.15]

    if len(ref) == 0:
        ref, _, refN = ref_select(y=y, varlabels=None, options=[5, 0])
        if options[0]:
            print(f"Object {refN} selected as reference")

    if len(optim_space) != 4:
        raise Exception('ERROR: "optim_space" must be of length 4')

    # S = (svd(y / np.sqrt(sum(y ** 2))) ** 4).sum(axis=0) #sum(a) in matlab is equivalent to a.sum(axis=0),
    # svd in MATLAB returns s diagonal matrix only if svd is callded with s = svd(A), or [U, ,V] if svd is called with: [U,S,V] = svd(A)
    # see: https://www.mathworks.com/help/matlab/ref/double.svd.html

    A = y / np.sqrt((y.ravel("F") ** 2).sum(axis=0))
    U, sdiag, VH = np.linalg.svd(A, full_matrices=False)
    S = (sdiag**4).sum(axis=0)

    se_g = np.arange(optim_space[0], optim_space[1] + 1)  # integer array min:max seg
    sl_g = np.arange(optim_space[2], optim_space[3] + 1)  # integer array min:max slack

    if len(se_g) <= 5:
        ag = se_g
    else:  # create an array of 5 roughly evenly spaced seg integers from min:max
        t = (se_g[-1] - se_g[0]) / 4
        ag = np.array(
            [
                se_g[0],
                np.round(se_g[0] + t * 1),
                np.round(se_g[0] + t * 2),
                np.round(se_g[0] + t * 3),
                se_g[-1],
            ],
            dtype=int,
        )
        ag = np.unique(ag)

    if len(sl_g) <= 5:
        bg = sl_g
    else:  # create an array of 5 roughly evenly spaced slack integers from min:max
        t = (sl_g[-1] - sl_g[0]) / 4
        bg = np.array(
            [
                sl_g[0],
                np.round(sl_g[0] + t * 1),
                np.round(sl_g[0] + t * 2),
                np.round(sl_g[0] + t * 3),
                sl_g[-1],
            ],
            dtype=int,
        )
        bg = np.unique(bg)

    t00 = time.time()
    if options[0]:
        print("Starting grid search")

    OS = np.empty((5, 1))  # initialize empty array to hold all seg and slack values

    N = 0

    for a in range(
        len(ag)
    ):  # loop through all seg and slack values and evaluate for optimal cow
        for b in range(len(bg)):
            if options[0]:
                t0 = time.time()
            OS[0, N] = ag[a]
            OS[1, N] = bg[b]
            OS[2:, N] = np.array([0, 0, 0]).T
            temp, exitflag = optim_eval(
                y=y,
                p=OS[0:2, N],
                OS=OS,
                ref=ref,
                losange=np.round(len(ref) * options[3]),
            )
            OS[:, N] = temp.T
            if N < len(ag) * len(bg) - 1:
                OS = np.hstack([OS, np.zeros((5, 1))])
            N += 1
            if options[0]:
                if exitflag == 1:
                    s = f"run {b + 1 + a * len(bg)}/{(len(ag) * len(bg))}: segment/slack combination was already computed"
                else:
                    if exitflag == 2:
                        s = f"run {b + 1 + a * len(bg)}/{(len(ag) * len(bg))}: illegal segment/slack combination"
                    else:
                        s = f"run {b + 1 + a * len(bg)}/{(len(ag) * len(bg))}: {round(time.time() - t0, 3)} sec"
                print(s)

    _, c = np.unique(OS[2, :], return_index=True)
    starts = c[-3:]
    # starts = np.flip(c[-3:]) # MATLAB code has fliplr but it is for (n x 1), nothing gets flipped. Above gives correct result.
    steps = np.zeros(len(starts))
    for a in range(len(starts)):
        if options[0]:
            print(
                f"Starting optimization {a + 1}/{len(starts)} (segment = {int(OS[0, starts[a]])}, slack = {int(OS[1, starts[a]])})"
            )
            t0 = time.time()
        Na = N - 1
        ps = np.array([starts[a], 0, 0])
        OS = np.hstack([OS, np.zeros((5, 1))])

        OS[0:2, N] = OS[0:2, ps[0]] + np.array([1, 0]).T

        temp, exitflag = optim_eval(
            y=y, p=OS[0:2, N], OS=OS, ref=ref, losange=np.round(len(ref) * options[3])
        )
        OS[:, N] = temp.T

        ps = np.array([ps[0], N, 0])
        N += 1
        OS = np.hstack([OS, np.zeros((5, 1))])
        OS[0:2, N] = OS[0:2, ps[0]] + np.array([0, 1]).T
        temp, exitflag = optim_eval(
            y=y, p=OS[0:2, N], OS=OS, ref=ref, losange=np.round(len(ref) * options[3])
        )
        OS[:, N] = temp.T
        ps = np.hstack([ps[0:2], N])
        N += 1

        pt = True

        while pt:
            b, c = np.sort(OS[2, ps]), np.argsort(OS[2, ps])
            OS = np.hstack([OS, np.zeros((5, 1))])

            position = [
                len(np.where(OS[0, ps] < OS[0, ps[c[0]]])[0]),
                len(np.where(OS[0, ps] > OS[0, ps[c[0]]])[0]),
                len(np.where(OS[1, ps] < OS[1, ps[c[0]]])[0]),
                len(np.where(OS[1, ps] > OS[1, ps[c[0]]])[0]),
            ]

            OS_opt1 = {
                re.compile(r"1, 0, 0, 1"): OS[0:2, ps[c[0]]] + np.array([-1, 1]).T,
                re.compile(r"0, 1, 0, 1"): OS[0:2, ps[c[0]]] + np.array([1, 1]).T,
                re.compile(r"0, 1, 1, 0"): OS[0:2, ps[c[0]]] + np.array([1, -1]).T,
                re.compile(r"1, 0, 1, 0"): OS[0:2, ps[c[0]]] + np.array([-1, -1]).T,
                re.compile(r"\d, \d, 2, \d"): OS[0:2, ps[c[0]]]
                + np.array([0, -2 * 1]).T,
                re.compile(r"2, \d, \d, \d"): OS[0:2, ps[c[0]]]
                + np.array([-2 * 1, 0]).T,
                re.compile(r"\d, \d, \d, 2"): OS[0:2, ps[c[0]]]
                + np.array([0, 2 * 1]).T,
                re.compile(r"\d, 2, \d, \d"): OS[0:2, ps[c[0]]]
                + np.array([2 * 1, 0]).T,
            }

            for key, val in OS_opt1.items():
                if key.findall(f"{position}"):
                    OS[0:2, N] = val

            temp, exitflag = optim_eval(
                y=y,
                p=OS[0:2, N],
                OS=OS,
                ref=ref,
                losange=np.round(len(ref) * options[3]),
            )
            OS[:, N] = temp.T
            if OS[2, N] <= b[0]:
                N += 1
                OS = np.hstack([OS, np.zeros((5, 1))])

                c = np.array([c[1], c[0], c[2]])
                b = np.array([b[1], b[0], b[2]])

                position = [
                    len(np.where(OS[0, ps] < OS[0, ps[c[0]]])[0]),
                    len(np.where(OS[0, ps] > OS[0, ps[c[0]]])[0]),
                    len(np.where(OS[1, ps] < OS[1, ps[c[0]]])[0]),
                    len(np.where(OS[1, ps] > OS[1, ps[c[0]]])[0]),
                ]

                OS_opt2 = {
                    re.compile(r"1, 0, 0, 1"): OS[0:2, ps[c[0]]] + np.array([-1, 1]).T,
                    re.compile(r"0, 1, 0, 1"): OS[0:2, ps[c[0]]] + np.array([1, 1]).T,
                    re.compile(r"0, 1, 1, 0"): OS[0:2, ps[c[0]]] + np.array([1, -1]).T,
                    re.compile(r"1, 0, 1, 0"): OS[0:2, ps[c[0]]] + np.array([-1, -1]).T,
                    re.compile(r"\d, \d, 2, \d"): OS[0:2, ps[c[0]]]
                    + np.array([0, -2 * 1]).T,
                    re.compile(r"2, \d, \d, \d"): OS[0:2, ps[c[0]]]
                    + np.array([-2 * 1, 0]).T,
                    re.compile(r"\d, \d, \d, 2"): OS[0:2, ps[c[0]]]
                    + np.array([0, 2 * 1]).T,
                    re.compile(r"\d, 2, \d, \d"): OS[0:2, ps[c[0]]]
                    + np.array([2 * 1, 0]).T,
                }

                for key, val in OS_opt2.items():
                    if key.findall(f"{position}"):
                        OS[0:2, N] = val

                temp, exitflag = optim_eval(
                    y=y,
                    p=OS[0:2, N],
                    OS=OS,
                    ref=ref,
                    losange=np.round(len(ref) * options[3]),
                )
                OS[:, N] = temp.T

                if OS[2, N] <= b[0]:
                    pt = False
                else:
                    ps[c[0]] = N

            ps[c[0]] = N
            N += 1

            if N - Na - 1 >= options[2]:
                pt = False
                print(f"Early termination after {N - Na - 1} steps!")

        if options[0]:
            print(
                f"optimization {a + 1}/{len(starts)}: {round(time.time() - t0, 3)} sec,  {N - Na - 1} steps"
            )

        steps[a] = N - Na - 1

    optim = np.argmax(OS[2, :])
    optim_pars = OS[0:2, optim]
    return optim_pars, OS


"""Thus far is verified with Matlab"""


#     # Plotting
#     if options(1):
#         f = figure
#         stem3(OS(1,:),OS(2,:),OS(3,:),'filled')
#         plt.xlabel('Segment length')
#         plt.ylabel('Slack size')
#         plt.zlabel('Warping Effect')
#         s = np.array(['Warping Effect(',num2str(optim_pars(1)),',',num2str(optim_pars(2)),')'])
#         text(OS(1,optim),OS(2,optim),OS(3,optim),s)
#         figure
#         stem3(OS(1,:),OS(2,:),OS(4,:),'filled')
#         hold('on')
#         stem3(OS(1,:),OS(2,:),np.ones(((OS(4,:)).shape,(OS(4,:)).shape)) * S)
#         hold('off')
#         plt.title('(Solid = Simplicity, Open = Simplicity Raw Data)')
#         plt.xlabel('Segment length')
#         plt.ylabel('Slack size')
#         plt.zlabel('Simplicity')
#         _,b = np.amax(OS(4,:))
#         s = np.array(['Simplicity(',num2str(OS(1,b)),',',num2str(OS(2,b)),')'])
#         text(OS(1,b),OS(2,b),OS(4,b),s)
#         s = np.array(['Warping Effect(',num2str(optim_pars(1)),',',num2str(optim_pars(2)),')'])
#         text(OS(1,optim),OS(2,optim),OS(4,optim),s)
#         figure
#         stem3(OS(1,:),OS(2,:),OS(5,:),'filled')
#         plt.xlabel('Segment length')
#         plt.ylabel('Slack size')
#         plt.zlabel('Peak Factor')
#         _,b = np.amax(OS(5,:))
#         s = np.array(['Peak Factor(',num2str(OS(1,b)),',',num2str(OS(2,b)),')'])
#         text(OS(1,b),OS(2,b),OS(5,b),s)
#         s = np.array(['Warping Effect(',num2str(optim_pars(1)),',',num2str(optim_pars(2)),')'])
#         text(OS(1,optim),OS(2,optim),OS(5,optim),s)
#         plt.figure(f)
#         print(np.array(['Finished optimization, optimal (segment slack) = (',num2str(np.transpose(optim_pars)),'), total time : ',num2str(etime(clock,t00) / 60,2),'min']))

#     # Diagnostics
#     if (nargout > 2):
#         if options(1):
#             print('Computing diagnostics')
#         diagnos.base_simplicity = S
#         diagnos.time_min = etime(clock,t00) / 60
#         diagnos.optim_starts_in_OS = starts
#         diagnos.optim_steps_in_OS = steps
#         diagnos.optim_space = optim_space
#         diagnos.reference = ref
#         if ('refN' is not None):
#             diagnos.reference_sample = refN
#         try:
#             diagnos.warping,diagnos.Xw,diagnos.warping_diagnos = cow(ref,y,optim_pars(1),optim_pars(2),np.array([0,1,0,np.round(len(ref) * options(4)),0]))
#         finally:
#             pass
#         if options(1):
#             figure
#             subplot(2,1,1)
#             plt.plot(np.arange(1,y.shape[2-1]+1),y)
#             plt.title('Data raw')
#             grid
#             subplot(2,1,2)
#             plt.plot(np.arange(1,diagnos.Xw.shape[2-1]+1),diagnos.Xw)
#             plt.title(np.array(['Data from optimal correction (segment ',num2str(optim_pars(1)),', slack ',num2str(optim_pars(2)),')']))
#             grid

#     ###
#     return optim_pars,OS,diagnos


def optim_eval(y=None, p=None, OS=None, ref=None, losange=None):
    """
    Takes in from optim_cow:
    y, p=OS[0:2, N], OS, ref, np.round(len(ref) * options(4))
    """

    index1 = np.nonzero(OS[0, 0:-1] == p[0])[
        0
    ]  # returns a linear array of indexes in first row of OS that equal p[0]
    index2 = np.nonzero(OS[1, 0:-1] == p[1])[0]
    index3 = np.intersect1d(
        index1, index2
    )  # for multi-dimensional matrices, see https://stackoverflow.com/questions/45637778/how-to-find-intersect-indexes-and-values-in-python

    z = np.zeros((5))
    z[0:2] = p

    exitflag = 0

    if index3.size > 0:  # check to see if segment/slack combo already computed
        z[2] = OS[2, index3[0]]
        z[3] = OS[3, index3[0]]
        z[4] = OS[4, index3[0]]
        exitflag = 1

    else:
        if (p[0] <= p[1] + 3) or (p[1] < 1):  # segment > slack OR slack < 1
            z[2:] = 0
            exitflag = 2
        else:
            K = y.shape[0]  # number of traces (rows) in y
            normX = np.zeros((K))
            for k in range(K):
                normX[k] = np.linalg.norm(
                    y[k, :], 2
                )  # assign Euclidean distance to normX

            try:
                warping, y, diagnos = cow(
                    ref,
                    y,
                    Seg=np.array([p[0]]),
                    Slack=np.array([p[1]]),
                    Options=[0, 1, 0, losange, 0, 1],
                )

            except:
                for a in range(K):
                    warping, y[a], diagnos = cow(
                        ref,
                        y[a][None, :],
                        Seg=np.array([p[0]]),
                        Slack=np.array([p[1]]),
                        Options=[0, 1, 0, losange, 0, 1],
                    )

            z[0] = diagnos["segment_length"][0, 0] + 1
            z[1] = diagnos["slack"]
            A = y / np.sqrt((y.ravel("F") ** 2).sum(axis=0))
            U, sdiag, VH = np.linalg.svd(A, full_matrices=False)
            z[3] = (sdiag**4).sum(axis=0)

            peakface = []
            for k in range(K):
                pkfac_tmp = np.abs((np.linalg.norm(y[k]) - normX[k]) / normX[k])
                peakface.append((1 - np.min(pkfac_tmp)) ** 2)
            z[4] = np.mean(peakface)
            z[2] = z[3] + z[4]

    return z, exitflag
