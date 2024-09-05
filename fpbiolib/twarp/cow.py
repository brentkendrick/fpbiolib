import math
import numpy as np


def cow(ref, y, Seg=np.array([7]), Slack=np.array([1]), Options=[0, 1, 0, 0, 0, 1]):
    """
    Translated from MATLAB to Python by Brent Kendrick, Feb 2023

    Warping,XWarped,Diagnos = cow(ref,y,Seg,Slack,Options);
    Correlation Optimized Warping function with linear interpolation
    Giorgio Tomasi / Frans van den Berg 070821 (GT)

    in:  ref (1 x nt) target (reference) vector
         y (mP x nP) matrix with data for mP row vectors of length nP to be warped/corrected
         Seg (1 x 1) segment length; number of segments N = floor(nP/m) where m is length of ind seg??
          or (2 x N+1) matrix with segment (pre-determined) boundary-points
                       first row = index in "xt", must start with 0 and end with "nt" (i.e. last index position of ref)
                       second row = index in "xP", must start with 0 and end with "nP"
         Slack (1 x 1) 'slack' - maximum range or degree of warping in segment length "m"
         Options [
                    triggers plot and progress-text (note: only last row/object in "xP" is plotted),
                    correlation power (minimum 1th power, maximum is 4th power),
                    force equal segment lengths in "xt" and "xP" instead of filling up "xt" with
                      N boundary-points, (notice that different number of boundaries in "xt"
                      and "xP" will generate an error),
                    fix maximum correction to + or - options(4) points from the diagonal
                    save in "diagnos" the table with the optimal values of loss function and
                        predecessor (memoryconsuming for large problems - on how to read the
                        tables are in the m-file
                    lengthen trace to enable accurate shifting of peaks bumping up at the end of x-range
                ]
                 default [0, 1, 0, 0, 0]
                 (no plot; power 1; no forced equal segment lengths;
                 no band constraints; no Table in "diagnos")

    out: Warping (mP x N x 2) interpolation segment starting points (in "nP"
             units) after warping (first slab) and before warping (second slab)
             (difference of the two = alignment by repositioning segment
             boundaries; useful for comparing correction in different/new objects/samples)
         XWarped (mP x nt) corrected vectors (from "xP" warped to mach "xt")
         Diagnos (struct) warping diagnostics: options, segment, slack,
             index in target ("xt", "warping" is shift compared to this) and sample ("xP"),
             search range in "xP", computation time
             (note: diagnostics are only saved for one - the last - signal in "xP")

    based on: Niels-Peter Vest Nielsen, Jens Micheal Carstensen and Jrn Smedegaard 'Aligning of singel and multiple
            wavelength chromatographic profiles for chemometric data analysis using correlation optimised warping'
            J. Chrom. A 805(1998)17-35

    Reference: Correlation optimized warping and dynamic time warping as preprocessing methods for chromatographic Data
            Giorgio Tomasi, Frans van den Berg and Claus Andersson, Journal of Chemometrics 18(2004)231-241

    Authors:
    Giorgio Tomasi / Frans van den Berg
    Royal Agricultural and Veterinary University - Department of Food Science
    Quality and Technology - Spectroscopy and Chemometrics group - Denmark
    email: gt@kvl.dk / fb@kvl.dk - www.models.kvl.dk
    """

    if (Options[1] < 1) or (Options[1] > 4):
        raise Exception(
            'ERROR: "Options(2)" (correlation power) must be in the range 1:4'
        )

    if np.any(np.isnan(ref)) or np.any(np.isnan(y)):
        raise Exception('ERROR: function "cow" can not handle missing values')

    ## Initialise
    if len(y.shape) == 1:
        y = y[None, :]  # make (1 x yn) so array stuff below works

    if Options[5] == 1:  # extend baseline for fitting late eluting pks
        ref = extend_baseline(ref)
        y = extend_baseline(y)

    # yn: number of signals that are to be aligned
    # ym: number of data points in each signal
    yn, ym = y.shape

    ref_m = ref.shape[0]  # number of data points in ref

    XWarped = np.zeros((yn, ref_m))  # Initialise matrix of warped signals

    ## Initialise segments
    Seg = Seg.astype(int)  # Segments can only be integers

    # Seg array larger than (1 x 1)...True if segment boundaries are predefined
    Pred_Bound = len(Seg) > 1
    if Pred_Bound:
        if not np.array_equal(Seg[:, 0], np.zeros((2))) and not np.array_equal(
            Seg[:, -1], np.array([ref_m, ym])
        ):
            raise Exception(
                "End points must be equal to 1 and to the length of the pattern/target"
            )
        LenSeg = np.diff(Seg, axis=1)
        if not (LenSeg >= 2).all():
            raise Exception("Segments must contain at least two points")
        nSeg = LenSeg.shape[1]  # nSeg: number of segments

    else:
        if np.max(Seg) > min(ym, ref_m):
            raise Exception("Segment length is larger than length of the signal")
        # Segments in the signals can have different length from those in the target
        if Options[2]:
            nSeg = math.floor((ref_m - 1) / Seg)
            LenSeg = np.empty((2, nSeg), dtype=int)
            LenSeg[0].fill(math.floor((ref_m - 1) / nSeg))
            LenSeg[1].fill(math.floor((ym - 1) / nSeg))
            print("\n Segment length adjusted to best cover the remainders")
        else:
            nSeg = math.floor((ref_m - 1) / (Seg - 1))
            LenSeg = np.empty((2, nSeg), dtype=int)
            LenSeg.fill(int(Seg[0] - 1))
            if math.floor((ym - 1) / (Seg - 1)) != nSeg:
                raise Exception(
                    "For non-fixed segment lengths the target and the signal do not have the same number of segments (try Options(3))"
                )
        temp = (ref_m - 1) % (LenSeg[0, 0])
        if temp > 0:
            LenSeg[0, nSeg - 1] = LenSeg[0, nSeg - 1] + temp
            if Options[0]:
                print(
                    f"\n Segments: {LenSeg[0,0] +1} points x {nSeg -1} segments + {LenSeg[0,-1] + 1} (target)"
                )
        else:
            if Options[0]:
                print(
                    f"\n Segments: {LenSeg[1,0] + 1} points x {nSeg} segments (target)"
                )
        temp = (ym - 1) % (LenSeg[1, 0])
        if temp > 0:
            LenSeg[1, nSeg - 1] = LenSeg[1, nSeg - 1] + temp
            if Options[0]:
                print(
                    f"\n {LenSeg[1,0] + 1} points x {nSeg - 1} segments + {LenSeg[1,-1] + 1} (signals)\n"
                )
        else:
            if Options[0]:
                print(f"\n {LenSeg[1,0] + 1} points x {nSeg} segments (signals)\n")
    if np.any(LenSeg.ravel("F") < Slack + 2):
        raise Exception("The slack cannot be larger than the length of the segments")

    bT = np.cumsum(np.insert(1, 1, LenSeg[0, :]))
    bP = np.cumsum(np.insert(1, 1, LenSeg[1, :]))
    Warping = np.zeros((yn, nSeg + 1))

    ## Check slack
    # Different slacks for the segment boundaries will be implemented if
    # slack array is passed rather than p[1]
    if len(Slack) > 1:
        if Slack.shape[0] <= nSeg:
            raise Exception(
                "The number of slack parameters is not equal to the number of optimised segments"
            )
        print("\n Multiple slacks have not been implemented yet")

    # All possible slacks for a segment boundary
    Slacks_vec = np.arange(-Slack, Slack + 1, dtype=int)

    ## Set feasible points for boundaries
    Bounds = np.ones((2, nSeg + 1))

    # Slope Constraints
    offs = (int(Slack) * np.transpose(np.array([[-1, 1]], dtype=int))) * (
        np.arange(0, nSeg + 1, dtype=int)
    )
    Bounds_a = np.add(np.vstack([bP, bP]), offs)
    Bounds_b = np.add(np.vstack([bP, bP]), np.fliplr(offs))
    Bounds[0] = np.maximum(Bounds_a[0], Bounds_b[0])
    Bounds[1] = np.minimum(Bounds_a[1], Bounds_b[1])

    # Band Constraints
    if Options[3]:
        if np.abs(ref_m - ym) > Options[3]:
            raise Exception(
                "The band is too narrow and proper correction is not possible"
            )
        Bounds[0] = np.maximum(Bounds[0], np.maximum(0, ym / ref_m * bT - Options[3]))
        Bounds[1] = np.minimum(Bounds[1], np.minimum(ym, ym / ref_m * bT + Options[3]))
        if np.any(np.diff(Bounds < 0)):
            raise Exception("The band is incompatible with the fixed boundaries")

    ## Calculate first derivatives for interpolation
    Xdiff = np.diff(y)

    ## Calculate coefficients and indexes for interpolation
    if not Pred_Bound:

        n = int(LenSeg[0, 0] + 1)
        nprime = LenSeg[1, 0] + Slacks_vec + 1
        offs = Slacks_vec
        A, B = interp_coeff(n=n, nprime=nprime, offs=Slacks_vec)

        int_coeff = [A for i in range(nSeg - 1)]
        int_index = [B for i in range(nSeg - 1)]

        n = int(LenSeg[0, nSeg - 1] + 1)
        nprime = LenSeg[1, nSeg - 1] + Slacks_vec + 1
        offs = Slacks_vec
        tmp_A, tmp_B = interp_coeff(n=n, nprime=nprime, offs=offs)

        int_coeff.append(tmp_A)
        int_index.append(tmp_B)

    else:
        int_coeff = []
        int_index = []
        for i_seg in range(nSeg):
            A, B = interp_coeff(
                int(LenSeg[0, i_seg] + 1), LenSeg[1, i_seg] + Slacks_vec + 1, Slacks_vec
            )
            int_coeff.append(A)
            int_index.append(B)

    ## Dynamic Programming Section
    Table_Index = np.cumsum(
        np.hstack([np.array([[0]]), np.diff(Bounds, axis=0) + 1]), dtype=int
    )  # Indices for the first node (boundary point) of each segment in Table

    # Table: each column refers to a node
    #        (1,i) position of the boundary point in the signal
    #        (2,i) optimal value of the loss function up to node (i)
    #        (3,i) pointer to optimal preceding node (in Table)
    Table = np.zeros((yn, 3, int(Table_Index[nSeg + 1])))

    # All loss function values apart from node (0) are set to -Inf
    Table[0:yn, 1, 1:] = -np.inf
    for i_seg in range(nSeg + 1):
        v = np.transpose(np.array([np.arange(Bounds[0, i_seg], Bounds[1, i_seg] + 1)]))
        Table[:, 0, Table_Index[i_seg] : Table_Index[i_seg + 1]] = np.transpose(
            v + np.zeros(yn, dtype=int)
        )

    np.seterr(divide="ignore")  # To avoid warning if division for zero occurs

    # Forward phase
    for i_seg in range(nSeg):  # Loop over segments
        # a,b,c: auxiliary values that depend only on segment number and not node
        a = Slacks_vec + LenSeg[1, i_seg]
        b = Table_Index[i_seg] + 1 - Bounds[0, i_seg]
        c = LenSeg[0, i_seg] + 1
        Count = 0  # Counter for local table for segment i_seg
        Node_Z = Table_Index[i_seg + 2]  # Last node for segment i_seg
        Node_A = Table_Index[i_seg + 1] + 1  # First node for segment i_seg
        # Initialise local table for boundary
        Bound_k_Table = np.zeros((yn, 2, Node_Z - Node_A + 1))
        # Indexes for interpolation of segment i_seg
        Int_Index_Seg = np.transpose(int_index[i_seg]) - (LenSeg[1, i_seg] + 2).astype(
            int
        )
        # Coefficients for interpolation of segment i_seg
        Int_Coeff_Seg = np.transpose(int_coeff[i_seg])
        # Segment i_seg of target ref
        TSeg = ref[np.arange(bT[i_seg] - 1, bT[i_seg + 1])]
        # Centred TSeg (for correlation coefficients)
        TSeg_centred = TSeg - np.sum(TSeg) / len(TSeg)
        # (n - 1) * standard deviation of TSeg (Euclidean dist)
        Norm_TSeg_cen = np.linalg.norm(TSeg_centred, 2)

        # Loop over nodes (i.e. possible boundary positions) for segment i_seg
        for i_node in np.arange(Node_A, Node_Z + 1):
            # Possible predecessors given the allowed segment lengths
            Prec_Nodes = Table[0, 0, i_node - 1] - a
            # Arcs allowed by local and global constraints
            Allowed_Arcs = np.logical_and(
                Prec_Nodes >= Bounds[0, i_seg], Prec_Nodes <= Bounds[1, i_seg]
            )
            # Pointer to predecessors in Table
            Nodes_TablePointer = (b + Prec_Nodes[Allowed_Arcs]).astype(int)
            # Number of allowed arcs
            N_AA = np.sum(Allowed_Arcs)
            # Sometimes boundaries are ineffective and few nodes are allowed
            # that cannot be reached, It has to be further investigated
            if N_AA:
                # Interpolation signal indexes for all the allowed arcs for node i_node
                Index_Node = (
                    Table[0, 0, i_node - 1] + Int_Index_Seg[:, Allowed_Arcs]
                ).astype(int)
                # Interpolation coefficients for all the allowed arcs for node i_node
                Coeff_b = Int_Coeff_Seg[:, Allowed_Arcs]
                Coeff_b = np.transpose(Coeff_b.ravel("F"))
                # create a (yn x Coeff_b) array
                Coeff_b = Coeff_b + np.zeros((yn, 1), dtype=int)
                Xi_Seg = y[:, Index_Node.ravel("F").astype(int)]
                Xi_diff = Xdiff[:, Index_Node.ravel("F").astype(int)]
                # Interpolate for all allowed predecessors
                Xi_Seg = np.transpose((Xi_Seg + np.multiply(Coeff_b, Xi_diff))).reshape(
                    int(c), N_AA * yn, order="F"
                )
                # Means of the interpolated segments
                Xi_Seg_mean = Xi_Seg.sum(axis=0) / Xi_Seg.shape[0]
                # Fast method for calculating the covariance of ref and y
                # (no centering of y is needed)
                Norm_Xi_Seg_cen = np.sqrt(
                    (Xi_Seg**2).sum(axis=0) - Xi_Seg.shape[0] * Xi_Seg_mean**2
                )

                # Correlation coefficients relative to all possible predecessors
                CCs_Node = np.dot(TSeg_centred, Xi_Seg) / np.dot(
                    Norm_TSeg_cen, Norm_Xi_Seg_cen
                )
                # If standard deviation is zero, update is not chosen
                CCs_Node[~np.isfinite(CCs_Node)] = 0
                CCs_Node = CCs_Node.reshape(N_AA, yn, order="F")
                # Optimal value of loss function from all predecessors
                if Options[1] == 1:
                    Cost_Fun = (
                        np.transpose(Table[:, 1, Nodes_TablePointer - 1]) + CCs_Node
                    )
                else:
                    Cost_Fun = (
                        np.transpose(Table[:, 1, Nodes_TablePointer - 1])
                        + CCs_Node ** Options[1]
                    )

                ind, pos = Cost_Fun.max(axis=0), Cost_Fun.argmax(axis=0)
                Bound_k_Table[:, 0, Count] = ind
                # Pointer to optimal predecessor
                Bound_k_Table[:, 1, Count] = Nodes_TablePointer[pos]
                Count += 1
        # Update general table (it turned out to be faster than using
        # Table directly in the loop over nodes
        Table[:, 1:, (Node_A - 1) : Node_Z] = Bound_k_Table

    # Backward phase
    for i_sam in range(yn):
        Pointer = Table.shape[2]
        Warping[i_sam, nSeg] = ym
        for i_bound in np.arange(nSeg - 1, -1, -1, dtype=int):
            Pointer = Table[i_sam, 2, Pointer - 1].astype(int)
            Warping[i_sam, i_bound] = Table[i_sam, 0, Pointer - 1]

    w_vert_size = np.zeros(yn, dtype=int)
    w_temp = bT + w_vert_size[:, None]
    Warping = np.vstack([[Warping], [w_temp]])

    np.seterr()  # Reset

    # Reconstruct aligned signals
    for i_seg in range(nSeg):
        indT = np.arange(bT[i_seg] - 1, bT[i_seg + 1])
        lenT = bT[i_seg + 1] - bT[i_seg]
        for i_sam in range(yn):
            indX = np.arange(
                Warping[0, i_sam, i_seg],
                Warping[0, i_sam, i_seg + 1] + 1,
                dtype=int,
            )
            lenX = int(Warping[0, i_sam, i_seg + 1]) - int(Warping[0, i_sam, i_seg])
            XWarped[i_sam, indT] = np.interp(
                np.arange(0, lenT + 1) / lenT * lenX + 1,
                indX - Warping[0, i_sam, i_seg] + 1,
                y[i_sam, indX - 1],
            )

    Diagnos = {
        "indexP": bP,
        "indexT": bT,
        "Nsegments": nSeg,
        "options": Options,
        "rangeP": np.transpose(Bounds),
        "segment_length": LenSeg,
        "slack": Slack,
        "table": [],
    }
    if Options[4]:
        Diagnos["table"] = Table

    # ## Plot
    # if Options(1):
    #     figure
    #     minmaxaxis = np.array([1,np.amax(np.array([ref_m,ym])),np.amin(np.array([ref,y(yn,:)])),np.amax(np.array([ref,y(yn,:)]))])
    #     subplot(2,1,1)
    #     plt.plot(np.arange(1,ref_m+1),ref,'b',bT,ref(bT),'.b',np.arange(1,ym+1),y(yn,:),'g',bP,y(yn,bP),'.g')
    #     hold('on')
    #     for a in np.arange(np.arange(2,len(Warping(yn,,,1))+1)):
    #         plt.plot(np.array([bT(a),Warping(yn,a,1)]),np.array([ref(Warping(yn,a,2)),ref(Warping(yn,a,2))]),'r')
    #         if (Warping(yn,a,2) > Warping(yn,a,1)):
    #             plt.plot(Warping(yn,a,2),ref(Warping(yn,a,2)),'>r')
    #         else:
    #             plt.plot(Warping(yn,a,2),ref(Warping(yn,a,2)),'<r')
    #     hold('off')
    #     plt.axis(minmaxaxis)
    #     grid
    #     plt.title(np.array(['COW reference = blue, Sample ',num2str(yn),'(/',num2str(yn),') = green, Segment-boundary movement = red']))
    #     subplot(2,1,2)
    #     plt.plot(np.arange(1,ref_m+1),ref,'b',np.arange(1,ref_m+1),XWarped(yn,:),'g')
    #     grid
    #     plt.axis(minmaxaxis)
    #     plt.title('Warped sample')

    if Options[5] == 1:
        return Warping, XWarped[:, :-200], Diagnos

    return Warping, XWarped, Diagnos


def interp_coeff(n=None, nprime=None, offs=None):
    """Calculate coefficients for interpolation"""
    p = len(nprime)
    q = n - 1
    Coeff = np.zeros((p, n))
    Index = np.zeros((p, n))
    for i_p in range(p):
        pp = np.arange(1, nprime[i_p] + 1, dtype=int)
        p = np.arange(0, q + 1, dtype=int) * (nprime[i_p] - 1) / q + 1
        k = np.digitize(p, pp)
        k[p < 1] = 1
        k[p >= nprime[i_p]] = nprime[i_p] - 1
        r = pp[k - 1]  # create an array from pp index 0 with length of k
        Coeff[i_p, :] = p - r
        Index[i_p, :] = k - offs[i_p]

    return Coeff, Index.astype(int)


def extend_baseline(y):
    """Extends y (intensity) data by 200 index points,
    based on random baseline noise of 25% of lowest
    y-values.
    """
    xtend_amt = 200
    if len(y.shape) == 1:
        temp = np.sort(y)  # sort lowest to highest y-values
        std = np.std(temp[0 : int(len(temp) * 0.25)], ddof=1)
        return np.hstack([y, np.random.randn(xtend_amt) * std + y[-1]])
    else:
        new_y = np.empty([y.shape[0], y.shape[1] + xtend_amt])
        for i in range(y.shape[0]):
            temp = np.sort(y[i, :])
            std = np.std(temp[0 : int(len(temp) * 0.25)], ddof=1)
            aug = np.hstack([y[i, :], np.random.randn(xtend_amt) * std + y[i, -1]])
            new_y[i, :] = aug
        return new_y
