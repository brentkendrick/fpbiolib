from scipy.stats import cauchy as cauchy_dist
from scipy.stats import norm as norm_dist


def reduce_chisquare(r):
    """Reduce residual array to scalar (chi-square).

    Calculate the chi-square value from residual array `r` as
    ``(r*r).sum()``.

    Parameters
    ----------
    r : numpy.ndarray
        Residual array.

    Returns
    -------
    float
        Chi-square calculated from the residual array.

    """
    return (r * r).sum()


def reduce_negentropy(r):
    """Reduce residual array to scalar (negentropy).

    Reduce residual array `r` to scalar using negative entropy and the
    normal (Gaussian) probability distribution of `r` as pdf:

       ``(norm.pdf(r)*norm.logpdf(r)).sum()``

    since ``pdf(r) = exp(-r*r/2)/sqrt(2*pi)``, this is
       ``((r*r/2 - log(sqrt(2*pi))) * exp(-r*r/2)).sum()``.

    Parameters
    ----------
    r : numpy.ndarray
        Residual array.

    Returns
    -------
    float
        Negative entropy value calculated from the residual array.

    """
    return (norm_dist.pdf(r) * norm_dist.logpdf(r)).sum()


def reduce_cauchylogpdf(r):
    """Reduce residual array to scalar (cauchylogpdf).

    Reduce residual array `r` to scalar using negative log-likelihood and
    a Cauchy (Lorentzian) distribution of `r`:

       ``-scipy.stats.cauchy.logpdf(r)``

    where the Cauchy pdf = ``1/(pi*(1+r*r))``.

    This gives better suppression of outliers compared to the default
    sum-of-squares.

    Parameters
    ----------
    r : numpy.ndarray
        Residual array.

    Returns
    -------
    float
        Negative entropy value calculated from the residual array.

    """
    return -cauchy_dist.logpdf(r).sum()
