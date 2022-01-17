import numpy as np
from numpy import exp

from scipy.special import erf
from scipy.special import erfc
from math import sqrt, pi, log

def EMG():
    pass

def GEMG():
    pass

def GLM():
    pass

def HVL(x, h, s, mu, a):
    return h * (exp(-1/2 * ((x-mu)/s)**2))/(1/(exp(a*mu/(1e4*s**2))) + 1/2 * (erf((x-mu)/(s*sqrt(2)))))  

def PLMG():
    pass

def ETG():
    pass

def LMG():
    pass

pk_idx = []

def component_pks_fm_model(x, pk_idx, meth, lmfit_option, params):  
    """ function to create list of all fitted component peak y-values, 
        with *params being a flat list containing peak function 
        parameters corresponding to the number of peaks desired to be modeled. 
        A note on using *args format in this function.  scipy.optimize.least_squares
        and lmfit will happily accept parameters as a list and will pass the list to the peak model functions.  However,scipy.curve_fit unpacks the parameters list. To
        facilitate comparison of curve_fit vs lmfit vs least_squares, the functions
        were written to receive unpacked lists.
    """

    # function mapper, takes in string and maps it to known functions
    fun =  {
            'gaussian':gaussian,
            'EMG':EMG,
            'GEMG':GEMG,  
            'GLM':GLM,
            'HVL':HVL,
            'PLMG':PLMG,
            'ETG':ETG,
            'LMG':LMG,       
           } 
    
    if lmfit_option: # lmfit uses a dictionary type to store parameters
        # params = params[0]
        # print("Params: ", params)
        params = list(params.valuesdict().values())
    
        
    num_pks = int(len(pk_idx))
    num_fun_params = int(len(params)/num_pks)   

    y_model_pks = []
    
    j = 0           
    for i in range(num_pks):
        params_temp = params[j: (j + num_fun_params)] # Grab a block of parameters to pass to model
        # Unpack params_temp to match the number of arguments in the function
        # calculate the function and append the peak to the y_model_pks
        y_model_pks.append(fun[meth](x, *params_temp)) 
        j += num_fun_params
    
    y_model_pks = np.asarray(y_model_pks) # convert list to an array, generally takes less memory
    
    # The gaussian peaks resulting from the curve fit often result in values 
    # that are insanely small (e.g. < 1e-30) and should just be converted to zero
    y_model_pks = np.where(y_model_pks < 1.0e-30, 0.0, y_model_pks)
      
    return y_model_pks



def gaussian(x, h, mu, s):  
    return h*exp(-(x - mu)**2/(2*s**2)) #Function defining a gaussian distribution

def gaussian_component_pks(params, x, pk_idx, lmfit=False):  
    """ function to create list of all fitted component peak y-values, 
        with flat list containing peak function parameters corresponding
        to the number of peaks desired to be modeled.  Params must be 
        passed as a flat (1-D) list.
    """
    if lmfit: # lmfit uses a dictionary type to store parameters
        params = list(params.valuesdict().values())
        
    num_pks = int(len(pk_idx))
    num_fun_params = 3 # Three parameters for each gaussian, h, mu, s.
   
    y_fun_pks = []
    
    j = 0           
    for i in range(num_pks):
        params_temp = params[j: (j + num_fun_params)] # Grab a block of parameters to pass to model
        y_fun_pks.append(gaussian(x, *params_temp)) # Append modeled peak y-values to list
        j += num_fun_params
    
    y_fun_pks = np.asarray(y_fun_pks) # convert list to an array, generally takes less memory
    
    # The gaussian peaks resulting from the curve fit often result in values 
    # that are insanely small (e.g. < 1e-30) and should just be converted to zero
    y_fun_pks = np.where(y_fun_pks < 1.0e-30, 0.0, y_fun_pks)
      
    return y_fun_pks