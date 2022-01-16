import sys
import tracetools

from setuptools import setup, find_packages

with open("README.md") as f:
    long_desc = f.read()

if sys.version_info < (3, 5):
    print("ERROR: tracetools tools require at least Python 3.5 to run")
    sys.exit(1)

install_requires = [
    "pandas>=1.2.4",
    "numpy>=1.20",
    "scikit-learn>=1.0.1",
    "plotly>=5.1.0 ",
    "dash>=2.0.0",
    "dash-bootstrap-components>=1.0.0",
    "multiprocess>=0.70",
    "diskcache>=5.3.0",
    "psutil>=5.8.0",
    "redis>=3.5.3",
    "celery>=5.2.1",
    "jsonpickle>=2.0.0",
]

setup(
    name="tracetools",
    version=tracetools.__version__,
    url="",
    author="Brent Kendrick",
    author_email="brent.kendrick@fp-biopharma.com",
    license="MIT",
    description="tracetools",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    platforms="any",
    packages=find_packages(exclude=["tests"]),
    entry_points={},
    python_requires=">=3.5",
    install_requires=install_requires,
)