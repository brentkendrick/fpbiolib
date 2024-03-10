"""General uncategorized functions"""

import sys

# Check to see if module is loaded (e.g. in a Jupyter notebook cell)
modulename = "clr"
if modulename not in sys.modules:
    print(f"You have not imported the {modulename} module")


def run_once(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)

    wrapper.has_run = False
    return wrapper


# Example
@run_once
def load_core_clr():
    print("loading core clr")
    # Initialize pythonnet and clr (needed for certain python versions / os)
    try:
        from pythonnet import load

        load("coreclr")
        import clr
    except:
        pass
