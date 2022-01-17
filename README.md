# fpbiolib

fpbiolib is a Python package that contains handy functions.

## Installation and updating

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install fpbiolib like below.
Rerun this command to check for and install updates, using the -I switch to force update.

```bash
pip install -I git+https://github.com/brentkendrick/fpbiolib
```

### Redis usage

The redis_storage module requires either a local instance of redis running on the host computer, or a docker instance of redis. This can be switched through the use of an environment variable, which can be set by creating a .env file in your project's root directory setup following the example below. The environment variable
can be accessed in your project by installing python-decouple using pip. See the documentation here: https://pypi.org/project/python-decouple/

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

## Usage

Features:

- baselines.rubberband --> applies rubberband baseline to x,y array

#### Demo of some of the features:

```python
from fpbiolib import baselines.rubberband

```

## License

[MIT](https://choosealicense.com/licenses/mit/)
