import sys

from setuptools import find_packages, setup

import fpbiolib

with open("README.md") as f:
    long_desc = f.read()

if sys.version_info < (3, 5):
    print("ERROR: fpbiolib tools require at least Python 3.5 to run")
    sys.exit(1)

install_requires = [
    "pandas>=2.0",
    "numpy>=1.26.0",
    "scipy>=1.7.3",
]

setup(
    name="fpbiolib",
    version=fpbiolib.__version__,
    url="",
    author="Brent Kendrick",
    author_email="brent.kendrick@fp-biopharma.com",
    license="MIT",
    description="fpbiolib",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    platforms="any",
    packages=find_packages(exclude=["tests"]),
    entry_points={},
    python_requires=">=3.5",
    install_requires=install_requires,
)
