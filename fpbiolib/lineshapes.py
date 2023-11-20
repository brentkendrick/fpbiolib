import numpy as np
import pandas as pd
from scipy.optimize import curve_fit, least_squares


"""curve fit function will sometimes fail, while least_squares works
when curve_fit works, it gives the identical fitted parameters as least_squares
"""


def linear_fun(x, m, b):
    """Function for linear regression"""
    return m * x + b


def gaussian(x, height, center, width):
    """Function defining a gaussian distribution"""
    return height * np.exp(-((x - center) ** 2) / (2 * width**2))


def ls_leach_scheraga(x, b, n):
    """Leach SJ, Scheraga HA. Effect of Light Scattering on Ultraviolet Difference Spectra 1. J Am Chem Soc. 1960;82(18):4790-4792."""
    return b * x ** (-n)


def rayleigh_mie(x, a, b, c):
    """Rayleigh scattering is inversely proportional to wavelength to
    the 4th power, and Mie scattering is inversely proportional to
    wavelength to between the 1st to 3rd power. Instruments also
    can have a baseline shift, b.
    Rayleigh, Lord. (1899). XXXIV. On the transmission of light through
    an atmosphere containing small particles in suspension, and on the
    origin of the blue of the sky.
    """
    return a / x**c + b
