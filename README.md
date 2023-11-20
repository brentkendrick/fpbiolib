# fpbiolib

fpbiolib is a Python package that contains handy functions.

## Installation and updating

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install fpbiolib like below.
Rerun this command to check for and install updates, using the -I switch to force update.

```bash
pip install -I git+https://github.com/brentkendrick/fpbiolib
```

## Installation

Currently fpbiolib is not open source, and must be installed from source or a private
codeartifact repository.

## Mac Installation - I've had the most success with PYENV on the Mac Apple Silicon

To ensure psycopg installs on MAC or Linux, first ensure postgres and libpq is installed
on the local host, and included in PATH
https://stackoverflow.com/questions/33866695/error-installing-psycopg2-on-macos-10-9-5

using the official python.org installers has led to some package
incompatibilities which haven't arisen when using pyenv for python
version management.

Update pyenv frequently

```
brew update && brew upgrade pyenv
```

Check installed python versions

```
pyenv versions
```

Find all available python versions

```
pyenv install --list
```

Install specific python version

```
pyenv install 3.11.4
```

Set local directory and subdirectories to use specific python version

```
pyenv local 3.11.4
```

Create virtual environment and activate it

```
python -m venv env311
source ./env311/bin/activate
```

Install setuptools

```
pip install -U pip setuptools wheel
```

Attempt to install all packages using requirements.txt

```
pip install -r requirements.txt
```

Some may fail, which can often be overcome by trying a different package version
(some get updated to the new arm architecture)

After successfull install, re-try installing the entire requirements.txt file again, it should work.

```
pip install -r requirements.txt
```

### From Source

Clone or download the repo and use setuptools to install the package locally. For
standard operation this can be done using the `setup.py` file in the top level
of the package. A development installation can also be done substituting
`develop` for `install`.

```bash
python setup.py install
```

### From CodeArtifact

To install from AWS CodeArtifact you can use the AWS CLI to autheticate pip
as follows.

```bash
aws codeartifact login --tool pip --repository norbi --domain norbi --domain-owner 979711578039
```

To install in docker or environments that do not have AWS CLI available you can
you can manually create a pip index url using the following

```bash
ARG AWS_DEFAULT_REGION=us-east-2
ARG AWS_DOMAIN_OWNER=979711578039
ARG CODEARTIFACT_DOMAIN=norbi
ARG CODEARTIFACT_REPO=norbi
ARG CODEARTIFACT_AUTH_TOKEN  # no default, longest possible token 12 hours
ARG PIP_INDEX_URL="https://aws:${CODEARTIFACT_AUTH_TOKEN}@${CODEARTIFACT_DOMAIN}-${AWS_DOMAIN_OWNER}.d.codeartifact.${AWS_DEFAULT_REGION}.amazonaws.com/pypi/${CODEARTIFACT_REPO}/simple/"

pip config set global.index-url PIP_INDEX_URL
```

You can then install fpcd using pip normally `pip install fpbiolib`.

## Deploy

Black is used to format all python files using a line length of 79. After
formatting remember to increment the package version prior to building and deploy.
Push to CodeArtifact as follows. (must pip install twine first)

```bash
black --line-length 79 .
python setup.py sdist bdist_wheel
aws codeartifact login --tool twine --domain norbi --repository norbi
twine upload --repository codeartifact dist/*
```

### Redis usage

The redis_storage module requires either a local instance of redis running on the host computer, or a docker instance of redis. This can be switched through the use of an environment variable, which can be set by creating a .env file in your project's root directory setup following the example below.

```
# If running local redis. Install for WSL2 using instructions here:
# https://docs.microsoft.com/en-us/windows/wsl/tutorials/wsl-database

# To start the local redis server: sudo service redis-server start
# To stop: sudo service redis-server stop
```

The environment variables in the .env file
can be accessed in your project by installing python-dotenv using pip. Then, create a settings.py
file in a root folder titled "config". Inside
settings.py use a command as in the following
example to allow the .env variables to be
activated when called.

config/settings.py

```
import os

# Redis default
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
```

fpbiolib/redis_storage.py

```

from config.settings import REDIS_URL

r = Redis.from_url(REDIS_URL, decode_responses=True)
```

## Usage

Features:

- baselines.rubberband --> applies rubberband baseline to x,y array

#### Demo of some of the features:

```python
from fpbiolib import baselines.rubberband

```

## License

[MIT](https://choosealicense.com/licenses/mit/)
