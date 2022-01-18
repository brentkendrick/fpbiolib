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
aws codeartifact login --tool pip --repository fpbiolib --domain norbi --domain-owner 979711578039
```

To install in docker or environments that do not have AWS CLI available you can
you can manually create a pip index url using the following

```bash
ARG AWS_DEFAULT_REGION=us-east-2
ARG AWS_DOMAIN_OWNER=979711578039
ARG CODEARTIFACT_DOMAIN=norbi
ARG CODEARTIFACT_REPO=fpbiolib
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
aws codeartifact login --tool twine --domain norbi --repository fpbiolib
twine upload --repository codeartifact dist/*
```

### Redis usage

The redis_storage module requires either a local instance of redis running on the host computer, or a docker instance of redis. This can be switched through the use of an environment variable, which can be set by creating a .env file in your project's root directory setup following the example below.

```
# If running local redis. Install for WSL2 using instructions here:
# https://docs.microsoft.com/en-us/windows/wsl/tutorials/wsl-database

# To start the local redis server: sudo service redis-server start
# To stop: sudo service redis-server stop

REDIS_URL=redis://127.0.0.1:6379/0


# If running with docker-compose and redis instance, comment the above
# line and uncomment the line below.  Save and restart your project to
# load the updated .env variable.

# REDIS_URL=redis://redis:6379/0
```

The environment variable
can be accessed in your project by installing python-decouple using pip. See the documentation here: https://pypi.org/project/python-decouple/. To see an example in this project, go to the module named redis_storage.py and look for the following code:

```
from decouple import config

REDIS_URL = config('REDIS_URL')

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
