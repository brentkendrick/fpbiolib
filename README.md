# fpbiolib

fpbiolib is a Python package that contains handy functions.

## Installation

Currently fpbiolib is not open source, and must be installed from source or a private
codeartifact repository.

### Local, editable installation

Clone or download the repo and use setuptools to install the package locally.

With the new pyproject.toml file format, the command python setup.py develop is no longer applicable. The modern alternative is to use pip install -e ., which installs your package in "editable" mode (the equivalent of setup.py develop).

Here's how to do it:
Ensure you have the latest version of pip, setuptools, and wheel in your virtual environment:

```bash
pip install --upgrade pip setuptools wheel
```

To install the package in editable mode:

clone the repository

```bash
git clone https://github.com/brentkendrick/fpbiolib.git
```

Line in a requirements.txt file (assumes fpbiolib was cloned to the indicated path)

```bash
-e /Users/brent/code/lib/fpbiolib
```

Or, in your project directory, run:

```bash
pip install -e .
```

This command will install your package in a way that allows you to modify the source code and immediately see changes without needing to reinstall the package.

### Installation of a specific version (good for production)

```bash
pip install fpbiolib @ git+https://github.com/brentkendrick/fpbiolib@v0.5.2

```

Line in a requirements.txt file

```bash
fpbiolib @ git+https://github.com/brentkendrick/fpbiolib@v0.5.2
```

Attempt to install all packages using requirements.txt

```bash
pip install -r requirements.txt
```

### Redis usage

The redis_storage module requires either a local instance of redis running on the host computer, or a docker instance of redis. This can be switched through the use of an environment variable, which can be set by creating a .env file in your project's root directory setup following the example below.

If running local redis. Install for WSL2 using instructions here:
https://docs.microsoft.com/en-us/windows/wsl/tutorials/wsl-database

To start the local redis server:

```bash
sudo service redis-server start
```

To stop:

```bash
sudo service redis-server stop
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
